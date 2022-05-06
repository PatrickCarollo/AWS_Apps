import boto3 
from botocore.exceptions import ClientError, ParamValidationError
from dotenv import load_dotenv, find_dotenv
import os
import json
import base64
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


#This app would need to be run outside of AWS environment to assume IAM roles created inside this application.
USERCOMMAND1 = input('Commands: sign up, sign in: '  )
inputemail  = 'pjcrollo@gmail.com'
inputpword = 'Passwordles1'
inputfirstname = 'pj'
inputlastname = 'carollo'
inputbdate = '09/09/1999'
inputmessage = 'yo sup big fella'


clientid = os.getenv('ClientID')
identitypoolid = os.getenv('IdentityPoolID')
poolid = os.getenv('PoolID')
cognitomap = os.getenv('CognitoMap')
bucketname = os.getenv('BucketName')
#setting userattributes object
uattr = [
    {
    'Name': 'given_name',
    'Value': inputfirstname
    },
    {
    'Name': 'family_name',
    'Value': inputlastname
    },
    { 
    'Name': 'birthdate',
    'Value': inputbdate
    },
    {       #accidental extreme customization
    'Name': 'custom:custom:message',
    'Value': inputmessage
    },
]



#begin cognito user create
idpclient = boto3.client('cognito-idp')
def Sign_Up():
    try:
        response = idpclient.sign_up(
            ClientId = clientid ,
            Username = inputemail ,
            Password = inputpword ,
            UserAttributes = uattr
        )   
        #print email status here
        if 'Destination' in response['CodeDeliveryDetails']:
            email = response['CodeDeliveryDetails']['Destination']
            print('Sign up began. '+ 'Verification code sent to ' + email + '.')
        else:
            print('Sign up received but no email found')
    #API fail
    except ParamValidationError as e:
        print("Parameter validation error: %s" % e)
    except ClientError as e:
        print("Client error: %s" % e)



def Confirm_Sign_Up():
    code = input('Enter verification code: ')
    try:
        codeconfirm = idpclient.confirm_sign_up(
            ClientId = clientid , 
            Username = inputemail , 
            ConfirmationCode = code
            )
        print('Confirmed User: ' + inputemail )
    #API fail
    except ParamValidationError as e:
        print("Parameter validation error: %s" % e)
    except ClientError as e:
        print("Client error: %s" % e)
            
            

#calling client and using userpassauth as authchallengefor user pool retrieve tokens to be used to create federated iD and get_user info
def Client_Auth_Flow():
    try: 
        authresponse = idpclient.initiate_auth(
            AuthFlow = 'USER_PASSWORD_AUTH' , 
            AuthParameters = { 
                'USERNAME': inputemail ,
                'PASSWORD' : inputpword
            },
            ClientId = clientid   
        )  #need two tokens from result
        if 'AccessToken' in authresponse['AuthenticationResult']:
            print('App authflow complete, Tokens found')
        return authresponse
    #API fail
    except ParamValidationError as e:
        print("Parameter validation error: %s" % e)
    except ClientError as e:
        print("Client error: %s" % e)



#creating user federated id
idclient = boto3.client('cognito-identity')
def Get_Id(authresult):
 
    it = authresult['AuthenticationResult']
    if 'IdToken' in it:
            token2 = it['IdToken']
    try:
        response = idclient.get_id(
            IdentityPoolId = identitypoolid,
            Logins = {
            cognitomap : token2   
            }
        )
        print('Identity id : ' + response['IdentityId'])
        return response
    #API fail
    except ParamValidationError as e:    
        print("Parameter validation error: %s" % e)
    except ClientError as e:
        print("Client error: %s" % e)        



#Post sign in api calls to get user info
def Get_User(authresult):
    at = authresult['AuthenticationResult']
    if 'AccessToken' in at:
            token1 = at['AccessToken']
    try:
        response = idpclient.get_user(
            AccessToken = token1
        )
        userdata = response['UserAttributes']
        print('get_user returned: ')
        for c in userdata:
            print(c)
        return userdata
    #API fail
    except ParamValidationError as e:
        print("Parameter validation error: %s" % e)
    except ClientError as e:
        print("Client error: %s" % e)



#Assumes IAM role 
def GetCredentialsForIdentity(authresult, iid):
    data = authresult['AuthenticationResult']
    if 'IdToken' in data:
        idtoken = data['IdToken']
    try:
        response = idclient.get_credentials_for_identity(
            IdentityId = iid['IdentityId'] , 
            Logins = {  
            cognitomap: idtoken
            }
        )
        if 'Credentials' in response:
            print('API keys found')
        return response
    #API fail
    except ParamValidationError as e:
        print("Parameter validation error: %s" % e)
    except ClientError as e:
        print("Client error: %s" % e)



#Ensures that a user is signed in to input next commands
def Userintent(iid):
    if 'IdentityId' in iid:
        comm = input('Commands: upload objects, list objects, download objects: ')
        user0 = iid['IdentityId']
        items = {'keydata': 'Cognito_Users' + '/' + user0 + '/', 'bucket': bucketname}
        dictinfo = {'USERCOMMAND2': comm, 'user0data': items}
        data = dictinfo
    else:
            data = '0'
    return data



#Invoke put_object lambda function and pass it user/bucket info
lamclient = boto3.client('lambda')
def Upload_Object(user0data):
    itemmap = input('Enter item path origin of object to be uploaded: ')
    with open(itemmap) as obj:
        object0 = obj.read()
    #modify user0dict to add object and object key from itemmap
    user0data['object'] = object0
    user0data['name'] = itemmap[itemmap.index('/') + 1:]
    payload = json.dumps(user0data)
    try:
        response = lamclient.invoke(
            InvocationType= 'RequestResponse' ,
            FunctionName = 'put_object' ,
            LogType = 'Tail' ,
            Payload = payload
        )  
        if 'Payload' in response:
            func_resp = json.loads(response['Payload'].read().decode("utf-8"))
            status = func_resp['ResponseMetadata']['HTTPStatusCode']
            if status == 200:
                data = status
                print('Upload success: ' + user0data['name'])
            else:
                data = '0'
        else:
            print('lambda failed to return put_object')
        return data
    #API fail
    except ParamValidationError as e:
        print("Parameter validation error: %s" % e)
    except ClientError as e:
        print("Client error: %s" % e)



def List_Object(user0data):
    payload = json.dumps(user0data)
    try:
        response = lamclient.invoke(
            FunctionName = 'list_objects',
            Payload = payload ,
            LogType = 'Tail' ,
            InvocationType= 'RequestResponse'
        )
        if 'Payload' in response:
            #needed to json stringify the datetime list objects call in lambda.
            func_resp = json.loads(response['Payload'].read().decode("utf-8"))
            destringed = json.loads(func_resp)
            items = destringed['Contents']
            if len(items) >= 0:
                print(user0data['bucket'] + ':')
                for x in items:
                    print(x['Key'][x['Key'].index('/') + 1:])
            else:
                print('No objects found in: ' + user0data['bucket'])
        else:
            print('Lambda list_objects function call failed')
    #API fail
    except ParamValidationError as e:
        print("Parameter validation error: %s" % e)
    except ClientError as e:
        print("Client error: %s" % e)



#Invokes lambda function that makes an s3 get_object call. Returns single object data
def Download_Object(user0data):
    selection = input('Select item to be downloaded: ')
    user0data['selected'] = selection
    payload = json.dumps(user0data)
    try:
        response = lamclient.invoke(
        FunctionName = 'download_object',
        InvocationType = 'RequestResponse',
        Payload = payload
        )
        if 'Payload' in response:
            func_resp = json.loads(response['Payload'].read().decode("utf-8"))
            print('Item: ')
            print(func_resp)
        else:
            print('No object found, get_object lambda function failed')
    #API fail    
    except ParamValidationError as e:
        print("Parameter validation error: %s" % e)
    except ClientError as e:
        print("Client error: %s" % e)



def main():
    if USERCOMMAND1 == 'sign up':
        Sign_Up() 
        Confirm_Sign_Up()
    elif USERCOMMAND1== 'sign in':
        x = Client_Auth_Flow()
        c = Get_Id(x)
        Get_User(x)
        GetCredentialsForIdentity(x , c)
        data = Userintent(c)

        if data['USERCOMMAND2'] == 'upload objects':
            if data == '0':
                print('User not signed in')
            else:
                Upload_Object(data['user0data'])

        elif data['USERCOMMAND2'] == 'list objects':
            if data == '0':
                print('User not signed in')         
            else:    
                List_Object(data['user0data'])

        elif data['USERCOMMAND2'] == 'download objects':
            if data == '0':
                print('User not signed in')
            else:
                List_Object(data['user0data'])
                Download_Object(data['user0data'])
                
        else:
            print('Invalid object(s) command')
    else:
        print('Invalid signup/sign in command')
if __name__ == '__main__':
    main()
