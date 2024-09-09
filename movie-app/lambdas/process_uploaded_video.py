import os
import json
import boto3

sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
bucket_name = os.environ['BUCKET_NAME']
queue_url = os.environ['SQS_QUEUE_URL']
metadata_table = dynamodb.Table(os.environ['METADATA_TABLE'])

def handler(event, context):
    for record in event['Records']:
        s3_info = record['s3']
        file_key = s3_info['object']['key']


        # Check if the file key starts with any of the resolution prefixes
        if file_key.startswith(('360p/', '720p/', '1080p/')):
            print(f"Skipping file as it does not start with resolution prefix: {file_key}")
            continue

        # Extract basic metadata
        s3_client = boto3.client('s3')
        file_metadata = s3_client.head_object(Bucket=bucket_name, Key=file_key)
        file_size = file_metadata['ContentLength']
        last_modified = file_metadata['LastModified']

        # Insert basic metadata into the DynamoDB table
        video_id = file_key.split('.')[0]  # Assuming the key is formatted like `video_id.mp4`
        metadata_table.put_item(
            Item={
                'video_id': video_id,
                'file_size': file_size,
                'last_modified': str(last_modified),
            }
        )

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
