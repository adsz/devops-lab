import boto3
import sys
import argparse
from botocore.exceptions import ProfileNotFound, ClientError

def list_snapshots(profile_name=None):
    try:
        # Create a session using the specified profile or default
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
        else:
            session = boto3.Session()

        # Create EC2 client
        ec2 = session.client('ec2')

        # Describe snapshots
        response = ec2.describe_snapshots(OwnerIds=['self'])

        # Print snapshot information
        print(f"{'Snapshot ID':<22} {'Volume ID':<22} {'Start Time':<25} {'Size (GB)':<10} {'Description'}")
        print("-" * 100)

        for snapshot in response['Snapshots']:
            snapshot_id = snapshot['SnapshotId']
            volume_id = snapshot.get('VolumeId', 'N/A')
            start_time = snapshot['StartTime'].strftime('%Y-%m-%d %H:%M:%S')
            size = snapshot['VolumeSize']
            description = snapshot.get('Description', 'N/A')

            print(f"{snapshot_id:<22} {volume_id:<22} {start_time:<25} {size:<10} {description}")

    except ProfileNotFound:
        print(f"Error: AWS profile '{profile_name}' not found.")
    except ClientError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List EC2 snapshots for an AWS account.")
    parser.add_argument("--profile", help="AWS profile name to use. If not specified, the default profile will be used.")
    args = parser.parse_args()

    list_snapshots(args.profile)
