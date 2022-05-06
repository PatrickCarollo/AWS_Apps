import boto3
import json
import datetime

s3client = boto3.client('s3')
def lambda_handler(event, context):
    bucketname = event['bucket']
    path = event['keydata']
    
    response = s3client.list_objects(
        Bucket = bucketname,
        Prefix = path
    )
    print(response)
    fata = json.dumps(response, default = conv)
    return fata
#uses isinstance to check if the unknown type is of datetime format and
#converts it to string
def conv(x):
    if isinstance(x, datetime.datetime):
        return x.__str__()
    