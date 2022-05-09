import boto3
from botocore.exceptions import ClientError
import json
import random


#Determine whether to begin new stack configuration/test or invoke a test for an existing stack app
def User_Commands():
    usercommand0 = input('Commands: new config, use config :')
    if usercommand0 == 'use config':
        data = input('Enter 4 digit existing test id: ')
        result = {'id0': data, 'comm': usercommand0}
    elif usercommand0 == 'new config':
        data = json.dumps(random.randint(1000, 9999))
        result = {'id0': data, 'comm': usercommand0}
    else:
        print('Invalid command')
    return result
        


#Creates lambda function that finds deployed stack and invokes the created infrastructure upon create_stack success
s3client = boto3.client('s3')
def Launch_Source_Bucket(input_data):
    id0 = input_data['id0']
    bktname = 'event-resource'+ id0
    try:
        response = s3client.create_bucket(
        Bucket = bktname
        )
        if 'Location' in response:
            data = response['Location'][response['Location'].index('/') + 1:]
            print('Source bucket for stack resources has been created: '+ data)
        else:
            print('Source bucket failed to create')
        return data
    #API fail
    except ClientError as e:
        print("Client error: %s" % e)



#Upload required testing and configuration resources
def Upload_Test_Resources(input_data, bucket_name):
    with open('AWS_Apps/Stack_Deploy+Test/template.yaml') as object1:
        template1 = object1.read()
    with open('AWS_Apps/Stack_Deploy+Test/data.json') as object2:
        items = object2.read() 
    with open('AWS_Apps/Stack_Deploy+Test/Test_Event.py') as object3:
        function = object3.read()         
    id0 = input_data['id0']
    try:
        response1 = s3client.put_object(
            Bucket = bucket_name,
            Body = template1 ,
            Key = 'Template' + id0 + '.yaml'
        )
        response2 = s3client.put_object(
            Bucket = bucket_name,
            Body = items,
            Key = 'data' + id0 + '.json'
        )
        response3 = s3client.put_object(
            Bucket = bucket_name,
            Body = function,
            Key = 'Test_Event' + id0 + '.py'
        )
        if 'ETag' in response3:
            print('Resources uploaded to bucket '+ bucket_name + id0)
    #API fail
    except ClientError as e:
        print("Client error: %s" % e)



#Uses code that was uploaded to resource bucket
lambdaclient = boto3.client('lambda')
def Create_Event_Function(input_data, bucket_name):
    id0 = input_data['id0']
    try:
        response = lambdaclient.create_function(
            FunctionName = 'Lambda_Test_Event' + id0,
            Runtime = 'python3.7', 
            Role = 'arn:aws:iam::143865003029:role/Test_Event_lambda',
            Handler = 'Test_Event' + id0 + '.lambda_handler',
            Code = {
                'S3Bucket': bucket_name,
                'S3Key': 'Test_Event' + id0 + '.py'
            }
        )
        if 'FunctionName' in response:
            print('Test event succesfully created:' + response['FunctionName'] +', continuing to stack create..')
    #API fail 
    except ClientError as e:
        print("Client error: %s" % e)



#Launch stack with template fetched from test id bucket/MIGht CHANGE THIS TO RUN UPON NEW TEST
cfclient = boto3.client('cloudformation')
def CF_Create(input_data):
    id0 = input_data['id0']
    name = 'Main_Stack'+ id0
    templatelocation = 'https://event-resource{}.s3.amazonaws.com/Template{}.yaml'.format(id0, id0)
    try:
        response = cfclient.create_stack(
            StackName = name,
            TemplateURL = templatelocation,
        )
        if 'StackId' in response:
            data = response['StackId']
            print('Stack created')
        else:
            data = False
        return data
    #API fail
    except ClientError as e:
        print("Client error: %s" % e)



#Starts the test that invokes deployed stack infrastructure, returns stack-launched function name
def Lambda_Event_Invoke(input_data):
    id0 = input_data['id0']
    payload = json.dumps(id0)
    try:
        response = lambdaclient.invoke(
            FunctionName = 'Lambda_Test_Event' + id0,
            Payload = payload
        )
        if response['StatusCode'] == 200:
            data = response['Payload']
            result = json.loads(data).read().decode('utf-8')
            if result['status'] == 200:
                functionname = result['stackfunction']
            else:
                print('Test event could not invoke deployed infrastructure')
        else:
            print('Test invoke failed')
        return functionname
    #API fail
    except ClientError as e:
        print("Client error: %s" % e)



#Gets CW log results of the stack-created Lambda calls
cwlogsclient = boto3.client('logs')
def Cloudwatch_Log_Fetch(stack_function):
    try:
        response = cwlogsclient.get_log_events(
        LogGroupName = '/aws/lambda/'+ stack_function,
        limit = 1
        )
        if 'events' in response:
            for x in response['events']:
                print(x['message'])
        else:
            print('Did not receive log from deployed function:' + stack_function)
    #API fail
    except ClientError as e:
        print("Client error: %s" % e)



#Optionally deletes deployed test buckets and functions to cleanup another deploy
def Delete_Test(input_data):
    id0 = input_data['id0']
    cleanup = input('Cleanup test resources?: y/n')
    if cleanup == 'y':
        try:
            response0 = s3client.delete_objects(
                Bucket = 'event-resource' + id0 ,
                Delete = [
                    {
                    'Key': 'Template' + id0 + '.yaml'
                    },
                    {
                    'Key': 'data' + id0 + '.json'
                    },
                    {
                    'Key': 'Test_Event' + id0 + '.py'
                    }               
                ]
            )
    
            response1 = s3client.delete_bucket(
                Bucket = 'event-resource' + id0 ,
            )

            response2 = lambdaclient.delete_function(
                FunctionName= 'Lambda_Test_Event' + id0
            )

        except ClientError as e:
            print("Client error: %s" % e)
    elif cleanup == 'n':
        print('Resource with id: '+ id0 + ' kept for future deployments')
    else:
        print('Invalid deletion command')
        
        

def main():
    a = User_Commands()
    if a['comm'] == 'new config':
        y = Launch_Source_Bucket(a)
        Upload_Test_Resources(a, y)
        Create_Event_Function(a, y)
        CF_Create(a)
    else:
        pass
    z = Lambda_Event_Invoke(a)
    Cloudwatch_Log_Fetch(z)
    Delete_Test(a)
if __name__ == '__main__':
    main()
