import boto3
import json
lambdaclient = boto3.client('lambda')
cfclient = boto3.client('cloudformation')
s3client = boto3.client('s3')
    


def lambda_handler(event, context):
#getting .json to send to stack launched infrastructure 
    response0 = s3client.get_object(
        Bucket = 'Event_Resource'+ event,
        Key = 'data' + event + '.json'
    )
    file = response0['Body'].read().decode('utf-8')
    global jsonitem
    jsonitem = json.dumps(file)


#getting lambdafunction name that was created in the stack, passing stackname the unique id from main app
    response1 = cfclient.describe_stacks(
        StackName =  'Main_Stack' + event                     
    )
    print(response1)
    for x in response1['Stacks']['Outputs']:
        global name
        name = x['OutputValue']
    returned_data = {'stackfunction': name, 'status': app_invoke}
#send main application confirmation that the stack-created function was invoked succesfully.
    return returned_data


#invoking the stack created function to begin the launched app
def app_invoke():
    response2 = lambdaclient.invoke(
        FunctionName = name , 
        Payload = jsonitem)
    return response2['StatusCode']


