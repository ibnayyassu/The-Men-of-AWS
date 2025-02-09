import boto3
from operator import itemgetter

ec2_client = boto3.client('ec2', region_name="us-east-1")
ec2_resource = boto3.resource('ec2', region_name="us-east-1")

instance_id = "i-00aaf0e27a7fcef5b"

volumes = ec2_client.describe_volumes(
    Filters = [
        {
            'Name': 'attachment.instance-id',
            'Values': [instance_id]
        }
    ]
)

instance_volume = volumes ['Volumes'][0]

#print(instance_volume)

snapshots = ec2_client.describe_snapshots(
    OwnerIds=['self'],
    Filters=[
        {
            'Name': 'volume-id',
            'Values': [instance_volume['VolumeId']]
        }
    ]
)

latest_snapshot = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse = True)[0]   #Since itemgetter is a module it has to be imported 
print(latest_snapshot['StartTime'])

new_volume = ec2_client.create_volume(
    AvailabilityZone='us-east-1a',
    SnapshotId=latest_snapshot['SnapshotId'],
    TagSpecifications=[
        {
            'ResourceType': 'volume',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'prod'
                }
            ]
        }
    ],
)
#Using a while loop to check if the volume is available before attaching it to the instance
while True:
    vol = ec2_resource.Volume(new_volume['VolumeId'])
    print(vol.state)
    if vol.state == 'available':
        ec2_resource.Instance(instance_id).attach_volume(
            VolumeId = new_volume['VolumeId'],
            Device='/dev/xvdb'     #we changed the last letter fromt the device attached name to connect another volume
        )
        break
