import json
import boto3

s3client = boto3.client('s3')

def lambda_handler(event, context):
    keypath = event['keydata'] + event['name']
    bucketname = event['bucket']
    file = event['object']
    
    response = s3client.put_object(
        Body = file ,
        Bucket = bucketname , 
        Key = keypath
    )
    return response
    
    