import os
import json
import boto3
import uuid
from botocore.config import Config

s3_client = boto3.client('s3', config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4', region_name='eu-central-1'))
bucket_name = os.environ['BUCKET_NAME']

def handler(event, context):
    try:
        video_id = str(uuid.uuid4())
        file_name = f"{video_id}.mp4"

        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=10800
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'presigned_url': presigned_url, 'video_id': video_id})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
