import os
import boto3
import json
import base64

def handler(event, context):
    s3_client = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    
    # Extract the file name from query string parameters
    video_name = event['queryStringParameters'].get('file', '')

    try:
        # Retrieve the video object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=video_name)
        video_data = response['Body'].read()

        # Encode binary data to Base64
        base64_encoded_video = base64.b64encode(video_data).decode('utf-8')

        return {
            'statusCode': 200,
            'body': base64_encoded_video,  # Base64 encoded string
            'isBase64Encoded': True,  # Indicates that the body is Base64 encoded
            'headers': {
                'Content-Type': 'video/mp4',  # Adjust if needed
                'Content-Disposition': f'attachment; filename="{video_name}"'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
