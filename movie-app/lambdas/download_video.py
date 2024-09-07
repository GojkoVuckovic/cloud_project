import os
import boto3
import json

def handler(event, context):
    s3_client = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    
    # Extract the file name from query string parameters
    video_name = event['queryStringParameters'].get('file', '')
    print(f"Bucket name: {bucket_name}, Video name: {video_name}")

    try:
        # Generate a presigned URL for the video object in S3
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': bucket_name, 'Key': video_name},
                                               ExpiresIn=3600)  # URL expires in 1 hour

        return {
            'statusCode': 200,
            'body': url,
            'headers': {
                'Content-Type': 'text/plain',  # The URL is returned as plain text
                'Content-Disposition': 'inline'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
