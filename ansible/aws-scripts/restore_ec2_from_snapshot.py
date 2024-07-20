import boto3
import sys
import argparse
from botocore.exceptions import ProfileNotFound, ClientError

def list_instances(ec2_client):
    response = ec2_client.describe_instances()
    instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]
    
    print("\nExisting EC2 Instances:")
    print(f"{'Instance ID':<20} {'Instance Type':<15} {'State':<10} {'Public IP':<15} {'Private IP':<15} {'Name'}")
    print("-" * 100)
    
    for instance in instances:
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        state = instance['State']['Name']
        public_ip = instance.get('PublicIpAddress', 'N/A')
        private_ip = instance.get('PrivateIpAddress', 'N/A')
        name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
        
        print(f"{instance_id:<20} {instance_type:<15} {state:<10} {public_ip:<15} {private_ip:<15} {name}")

def list_snapshots(ec2_client):
    response = ec2_client.describe_snapshots(OwnerIds=['self'])
    snapshots = response['Snapshots']
    
    print("\nAvailable Snapshots:")
    print(f"{'Snapshot ID':<22} {'Volume ID':<22} {'Start Time':<25} {'Size (GB)':<10} {'Description'}")
    print("-" * 100)
    
    for snapshot in snapshots:
        print(f"{snapshot['SnapshotId']:<22} {snapshot.get('VolumeId', 'N/A'):<22} {snapshot['StartTime'].strftime('%Y-%m-%d %H:%M:%S'):<25} {snapshot['VolumeSize']:<10} {snapshot.get('Description', 'N/A')}")

def restore_from_snapshot(ec2_client, ec2_resource, snapshot_id, instance_id):
    try:
        # Get instance details
        instance = ec2_resource.Instance(instance_id)
        availability_zone = instance.placement['AvailabilityZone']
        
        # Create new volume from snapshot
        new_volume = ec2_client.create_volume(
            SnapshotId=snapshot_id,
            AvailabilityZone=availability_zone,
            TagSpecifications=[
                {
                    'ResourceType': 'volume',
                    'Tags': [{'Key': 'Name', 'Value': f'Restored from {snapshot_id}'}]
                }
            ]
        )
        
        print(f"New volume created: {new_volume['VolumeId']}")
        
        # Wait for the volume to be available
        waiter = ec2_client.get_waiter('volume_available')
        waiter.wait(VolumeIds=[new_volume['VolumeId']])
        
        # Stop the instance
        print(f"Stopping instance {instance_id}")
        instance.stop()
        instance.wait_until_stopped()
        
        # Detach and delete the old root volume
        old_root_volume_id = instance.root_device_name
        old_volumes = [v for v in instance.volumes.all() if v.attachments[0]['Device'] == old_root_volume_id]
        if old_volumes:
            old_volume = old_volumes[0]
            old_volume.detach_from_instance()
            waiter = ec2_client.get_waiter('volume_available')
            waiter.wait(VolumeIds=[old_volume.id])
            old_volume.delete()
            print(f"Old root volume {old_volume.id} detached and deleted")
        
        # Attach new volume
        instance.attach_volume(
            VolumeId=new_volume['VolumeId'],
            Device=instance.root_device_name
        )
        
        # Start the instance
        print(f"Starting instance {instance_id}")
        instance.start()
        instance.wait_until_running()
        
        print(f"Instance {instance_id} restored from snapshot {snapshot_id}")
        
    except ClientError as e:
        print(f"Error: {e}")

def main(profile_name=None):
    try:
        # Create a session using the specified profile or default
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
        else:
            session = boto3.Session()

        ec2_client = session.client('ec2')
        ec2_resource = session.resource('ec2')

        # List instances
        list_instances(ec2_client)

        # List snapshots
        list_snapshots(ec2_client)

        # Get user input
        instance_id = input("\nEnter the Instance ID to restore to: ")
        snapshot_id = input("Enter the Snapshot ID to restore from: ")

        # Confirm action
        confirm = input(f"\nAre you sure you want to restore instance {instance_id} from snapshot {snapshot_id}? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return

        # Restore from snapshot
        restore_from_snapshot(ec2_client, ec2_resource, snapshot_id, instance_id)

    except ProfileNotFound:
        print(f"Error: AWS profile '{profile_name}' not found.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List EC2 instances and snapshots, then restore an instance from a selected snapshot.")
    parser.add_argument("--profile", help="AWS profile name to use. If not specified, the default profile will be used.")
    args = parser.parse_args()

    main(args.profile)