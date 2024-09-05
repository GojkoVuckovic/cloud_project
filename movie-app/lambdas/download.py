import boto3
import os
import base64

s3_client = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']

def handler(event, context):
    # Extract the file name from the event
    file_name = event['queryStringParameters']['file_name']
    
    # Get the file from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
    file_content = response['Body'].read()
    
    # Return the file content directly
    return {
        'statusCode': 200,
        'body': base64.b64encode(file_content).decode('utf-8'),
        'isBase64Encoded': True,
        'headers': {
            'Content-Type': 'video/mp4',
            'Content-Disposition': f'attachment; filename="{file_name}"'
        }
    }
