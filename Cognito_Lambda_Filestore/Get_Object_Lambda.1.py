import json
import boto3
import datetime
s3client = boto3.client('s3')
def lambda_handler(event, context):
    
    bucketname = event['bucket']
    path = event['keydata']
    name = event['selected']
    item = path + name
    response = s3client.get_object(
        Bucket = bucketname ,
        Key = item
    )
    
    return response['Body'].read().decode('utf-8')
    