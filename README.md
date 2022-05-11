# AWS_Apps


Cognito_Lambda_Filestore:

This app is meant to demonstrate the concept of user credentials and validation for an object storage application.
it leverages Congito Userpools to first validate the users sign up information, Then FederatedIdentity to grant the user 
narrow GET/PUT IAM access to only a bucket in the name of their unique ID(IdentityID). It uses Aws Lambda to run the 
calls to S3.




Stack_Deploy+Test:

This app is meant to demonstrate the concept of Automating the testing and deployment of an Aws CloudFormation stack.
It has the capability to either deploy new test/stack infrastructure or simply run a test through an existing stack
deployment. It does this by assigning a unique id to every component necessary to the test and deployment; for a new test
it will create the unique id and assign it accross all components, to test an existing one; it will run only components
with the provided id. It leverages the use of CloudWatchLogs to report the results of the test and Lambda to run them.

