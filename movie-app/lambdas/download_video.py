import os
import base64
import boto3
import json

def handler(event, context):
    s3_client = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    
    # Extract the file name from query string parameters
    file_name = event['queryStringParameters'].get('file-name', '')
    format = event['queryStringParameters'].get('format', 'original')  # Default to 'original' if no format is specified

    # Generate the key for the specific format
    key = f'{format}/{file_name}' if format != 'original' else file_name

    try:
        # Retrieve the video object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        video_data = response['Body'].read()
        
        # Encode binary data to base64
        base64_encoded_video = base64.b64encode(video_data).decode('utf-8')

        return {
            'statusCode': 200,
            'body': base64_encoded_video,
            'isBase64Encoded': True,  # Important for binary data
            'headers': {
                'Content-Type': 'video/mp4'  # Adjust if your video is in a different format
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
