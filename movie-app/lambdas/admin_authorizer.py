import os
import logging
from aws_jwt_verify import CognitoJwtVerifier

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create the verifier outside the Lambda handler to reuse the cache
jwt_verifier = CognitoJwtVerifier(
    user_pool_id=os.environ['USER_POOL_ID'],
    token_use="id",
    client_id=os.environ['CLIENT_ID']
)

def lambda_handler(event, context):
    access_token = event['authorizationToken']

    try:
        # Verify the access token
        logger.info('#ACCESS TOKEN')
        logger.info(access_token)
        payload = jwt_verifier.verify(access_token)
    except Exception as error:
        logger.error('#Authentication error')
        logger.error(error)
        # Raise an error with the exact message expected by API Gateway
        raise Exception("Unauthorized")

    logger.info(payload)

    # Check if the user is an admin
    if payload.get('custom:isAdmin'):
        return generate_policy('user', 'Allow', event['methodArn'])

    return generate_policy('user', 'Deny', event['methodArn'])

def generate_policy(principal_id, effect, resource):
    # Generate an IAM policy
    auth_response = {
        'principalId': principal_id
    }

    if effect and resource:
        policy_document = {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
        auth_response['policyDocument'] = policy_document

    # Optional output with custom properties
    auth_response['context'] = {
        "stringKey": "stringval",
        "numberKey": 123,
        "booleanKey": True
    }

    return auth_response
