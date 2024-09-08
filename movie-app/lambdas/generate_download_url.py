import os
import json
import boto3
from botocore.config import Config

s3_client = boto3.client('s3', config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4', region_name='eu-central-1'))
bucket_name = os.environ['BUCKET_NAME']

def handler(event, context):
    try:
        file_name = event['queryStringParameters']['file_name']
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=10800
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'presigned_url': presigned_url})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
