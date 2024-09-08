import json
import os
import boto3

sqs_client = boto3.client('sqs')
bucket_name = os.environ['BUCKET_NAME']
queue_url = os.environ['SQS_QUEUE_URL']

def handler(event, context):
    for record in event['Records']:
        s3_info = record['s3']
        file_key = s3_info['object']['key']

        # Check if the file key starts with any of the resolution prefixes
        if file_key.startswith(('360p/', '720p/', '1080p/')):
            print(f"Skipping file as it does not start with resolution prefix: {file_key}")
            continue
        else:
            print(f"Processing file: {file_key}")

        # Send SQS messages for different resolutions
        resolutions = ['360p', '720p', '1080p']
        for resolution in resolutions:
            message_body = {
                'bucket_name': bucket_name,
                'file_key': file_key,
                'resolution': resolution
            }
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message_body)
            )
