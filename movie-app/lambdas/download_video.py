import os
import json
import boto3
import base64

def handler(event, context):
    s3_client = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    video_name = event['queryStringParameters']['file']
    
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=video_name)
        video_data = response['Body'].read()
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'video/mp4',
                'Content-Disposition': f'attachment; filename="{video_name}"'
            },
            'body': base64.b64encode(video_data).decode('utf-8'),
            'isBase64Encoded': True
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
