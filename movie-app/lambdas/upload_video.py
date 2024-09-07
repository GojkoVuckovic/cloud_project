import os
import boto3
import uuid
from botocore.exceptions import ClientError

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    s3_client = boto3.client('s3')
    
    # Generate a unique key using UUID
    unique_key = str(uuid.uuid4()) + '.mp4'
    
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': bucket_name, 'Key': unique_key},
                                                    ExpiresIn=3600)
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': f"Error generating presigned URL: {e}"
        }
    
    return {
        'statusCode': 200,
        'body': response
    }
