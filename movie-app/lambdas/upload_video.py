# lambdas/upload.py
import os
import json
import boto3
import base64
import uuid

s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

bucket_name = os.environ['BUCKET_NAME']
transcoding_queue_url = os.environ['TRANSCODE_QUEUE_URL']
metadata_table_name = os.environ['METADATA_TABLE_NAME']
metadata_table = dynamodb.Table(metadata_table_name)

s3_client = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']

def handler(event, context):
    try:
        video_data = event['body']
        if event.get('isBase64Encoded', False):
            video_data = base64.b64decode(video_data)
        
        # Generate a unique video ID and file name
        video_id = str(uuid.uuid4())
        file_name = f"{video_id}.mp4"

        # Upload the video to S3
        s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=video_data)

        # Store metadata in DynamoDB
        metadata = {
            'video_id': video_id,
            'file_name': file_name,
            'size': len(video_data),
            'time_added': context.aws_request_id,
            'last_modified': context.aws_request_id,
            'file_description': 'A sample video',
            'actors': 'John Doe',
            'director': 'Jane Smith',
            'genre': 'Action'
        }
        metadata_table.put_item(Item=metadata)

        # Send a message to SQS for each format
        formats = ['360p', '720p', '1080p']
        for format in formats:
            sqs_client.send_message(
                QueueUrl=transcoding_queue_url,
                MessageBody=json.dumps({
                    'video_id': video_id,
                    'file_name': file_name,
                    'format': format
                })
            )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Upload successful', 'video_id': video_id})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
