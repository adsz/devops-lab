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

def create_named_snapshot(instance_id, ec2_resource, description):
    try:
        # Use instance ID as the snapshot name
        snapshot_name = instance_id
        
        # Get the instance
        instance = ec2_resource.Instance(instance_id)
        
        # Get the root volume
        root_volume = next(iter(instance.volumes.all()))
        
        # Create snapshot
        snapshot = root_volume.create_snapshot(
            Description=description,
            TagSpecifications=[
                {
                    'ResourceType': 'snapshot',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': snapshot_name
                        }
                    ]
                },
            ]
        )
        
        print(f"Snapshot created with ID: {snapshot.id}")
        print(f"Snapshot name: {snapshot_name}")
        print(f"Description: {description}")

    except ClientError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error creating snapshot: {str(e)}")

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

        # Get user input
        instance_id = input("\nEnter the Instance ID to create a snapshot for: ")
        
        # Loop until a non-empty description is provided
        while True:
            description = input("Enter a description for the snapshot (mandatory): ")
            if description.strip():
                break
            print("Description cannot be empty. Please try again.")

        # Create snapshot
        create_named_snapshot(instance_id, ec2_resource, description)

    except ProfileNotFound:
        print(f"Error: AWS profile '{profile_name}' not found.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List EC2 instances and create a named snapshot for a selected instance.")
    parser.add_argument("--profile", help="AWS profile name to use. If not specified, the default profile will be used.")
    args = parser.parse_args()

    main(args.profile)