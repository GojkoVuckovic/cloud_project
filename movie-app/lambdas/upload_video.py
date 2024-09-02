import os
import json
import boto3
import random
import string


def handler(event, context):
    video_name = file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ".mp4"
    video_data = event['body']
    s3_client = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    try:
        s3_client.put_object(Bucket=bucket_name, Key=video_name, Body=video_data, ContentType='video/mp4')
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Video uploaded successfully',
                                'videoName': video_name})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
