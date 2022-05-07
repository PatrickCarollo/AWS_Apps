import boto3
import json
from botocore.exceptions import ClientError
s3client = boto3.client('s3')
dynamodbclient = boto3.client('dynamodb')




def lambda_handler(event, context):
    try:
        response0 = dynamodbclient.batch_write_item(
        RequestItems = event ,
        ReturnConsumedCapacity = 'INDEXES'  
        )
        if len(response0['UnprocessedItems']) == 0:
            for x in response0['ConsumedCapacity']:
                if 'TableName' in x: 
                    tabledata = x['TableName']
                    print('Successfully uploaded .json items to ' + tabledata)
                else:
                    print('Could not find tablename in batchwrite call')
            else:
                tabledata = response0['UnprocessedItems']
                print('.json failed to batchwrite')
        return tabledata
    #API fail
    except ClientError as e:
        print("Client error: %s" % e)



def query_item(table_name):
    try:
        response1 = dynamodbclient.query(
            TableName =  table_name,
            Select = 'ALL_ATTRIBUTES' ,
            KeyConditionExpression =   'Released <= :x' ,
            ExpressionAttributeValues = {
                ':x' : {'N' : '1999' }
            }    
        )
        if 'Items' in response1:
            print('Successfully queried deployed table: '+ table_name)
            if len(response1['Items']) >= 0:
                data = response1['Items']
            else:
                data = len(response1['Items'])
        else:
            print('Could not query deployed table: ' + table_name)
        return data
    #API fail
    except ClientError as e:
        print("Client error: %s" % e)




def upload_result(query_result):
    filebody = json.dumps(query_result)
    for y in query_result:
        if 'id' in y:
            name = y['id']['N']
        try:
            response2 = s3client.put_object(
                ACL = 'private',
                Body = filebody,
                Bucket = 'Dest_Bucket0101',
                Key = name
            )
 
            if 'ETag' in response2:
                print('Uploaded query results to Dest_Bucket0101')
 
        #API fail
        except ClientError as e:
            print("Client error: %s" % e)



def main():
    x = lambda_handler
    if x == 0:
        pass
    y = query_item(x)
    if y != 0:
        upload_result(y)
if __name__ == '__main__':
    main()