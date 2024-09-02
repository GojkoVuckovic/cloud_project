import boto3
import os
import base64
import json

s3_client = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']

def handler(event, context):
    
    # Decode base64-encoded binary data
    video_data = event['body']
    if event.get('isBase64Encoded', False):
        video_data = base64.b64decode(video_data)
    
    # Generate a unique file name or use a specific naming scheme
    video_name = event['queryStringParameters'].get('file_name', 'default_video.mp4')

    try:
        # Upload the video object to S3
        s3_client.put_object(Bucket=bucket_name, Key=video_name, Body=video_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Upload successful'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
