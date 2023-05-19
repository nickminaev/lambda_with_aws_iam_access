import json
import boto3
from os.path import exists
import requests
from requests_auth_aws_sigv4 import AWSSigV4

OUTPUTS = 'outputs'
FUNCTION_INVOKER_USER_SECRET = 'function_invoker_user_secret'
FUNCTION_INVOKER_USER_ACCESS_KEY_ID = 'function_invoker_user_access_key_id'
FUNCTION_INVOKER_ROLE_ARN = 'function_invoker_role_arn'
FUNCTION_URL = 'function_url'
TF_STATE_FILE_NAME = 'terraform.tfstate'
required_info = (FUNCTION_INVOKER_USER_SECRET, FUNCTION_INVOKER_USER_ACCESS_KEY_ID, FUNCTION_INVOKER_ROLE_ARN, FUNCTION_URL)
CREDENTIALS = 'Credentials'
TEMP_CREDS_ACCESS_KEY_ID = 'AccessKeyId'
TEMP_CREDS_ACCESS_SECRET_ACCESS_KEY = 'SecretAccessKey'
TEMP_CREDS_SESSION_TOKEN = 'SessionToken'

def get_params_from_tf_state():
    request_info = {}
    tf_state_info = None
    if not exists(TF_STATE_FILE_NAME):
        print('It seems that you still did not deploy the lambda. Run the ./deploy.sh script to do so.')
        return
    try:
        with open(TF_STATE_FILE_NAME) as tf_state_file:
            tf_state_info = json.loads(tf_state_file.read())
    except:
        print('An exception occurred while opening the file')
        return
    if not OUTPUTS in tf_state_info:
        print('Missing the "outputs" information from the Terraform State file. Aborting the script.')
        return
    terraform_outputs = tf_state_info.get(OUTPUTS)
    try:
        return {param_name: terraform_outputs[param_name]['value'] for param_name in required_info}
    except KeyError:
        return    
    

def get_temporary_creds_from_aws_sts(assume_role_params):
    # specify some predefined params for the request
    role_arn = assume_role_params.get(FUNCTION_INVOKER_ROLE_ARN)
    role_session_name = 'lambda_invocation_example'
    duration_seconds = 900 # 15 mins is the minimum value
    # get the access key id & the secret itself to authenticate against sts
    aws_access_key_id = assume_role_params.get(FUNCTION_INVOKER_USER_ACCESS_KEY_ID)
    aws_secret_access_key = assume_role_params.get(FUNCTION_INVOKER_USER_SECRET)
    # finally, assume the required role
    try:
        client = boto3.client('sts', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        response = client.assume_role(RoleArn=role_arn, RoleSessionName=role_session_name, DurationSeconds=duration_seconds)
        if not CREDENTIALS in response:
            print('The response is missing the credentials')
            return
        return response[CREDENTIALS]
    except Exception as e:
        print(f'Could not assume the role. Check the user\'s credentials. {e}')

def invoke_function_with_requests(lambda_url, temp_creds):
    try:
        aws_auth = AWSSigV4('lambda',
            aws_access_key_id=temp_creds[TEMP_CREDS_ACCESS_KEY_ID],
            aws_secret_access_key=temp_creds[TEMP_CREDS_ACCESS_SECRET_ACCESS_KEY],
            aws_session_token=temp_creds[TEMP_CREDS_SESSION_TOKEN],
            region='eu-west-1'
        )
    except:
        print('Could not create AWS S4 signature')
        return
    try:
        response = requests.get(lambda_url, auth=aws_auth)
        if response.status_code == 200:
            return response.text
    except:
        print('Could not get an OK response from the lambda URL')

def main():
    lambda_invocation_params = get_params_from_tf_state()
    if not lambda_invocation_params:
        print('Some of the required paramaters are missing. Make sure you have the needed outputs specified in the main.tf file')
        exit(1)
    print('The parameters were obtained from the Terraform State file')
    print('Requesting temporary credentials for the "lambda_invoker" user')
    temporary_creds = get_temporary_creds_from_aws_sts(lambda_invocation_params)
    if not temporary_creds:
        print('Could not assume the credentials. Aborting')
        exit(1)
    print('Got the temporary credentials')
    print('Invoking the lambda')
    lambda_url = lambda_invocation_params.get(FUNCTION_URL)
    response_contents = invoke_function_with_requests(lambda_url, temporary_creds)
    if response_contents:
        print(f'The invocation succeeded. Response contents: {response_contents}')

main()