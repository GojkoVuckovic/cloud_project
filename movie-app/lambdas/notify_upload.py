import json
import boto3
import os

sqs_client = boto3.client('sqs')
queue_url = os.environ['QUEUE_URL']

def handler(event, context):
    formats = ['360p', '720p', '1080p']

    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']
        file_key = f"upload/{file_key}"
        print("Received notification for file:", file_key)

        for format in formats:
        # Send the S3 file key to the SQS queue
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({
                    'bucket': bucket_name,
                    'file_key': file_key,
                    'format': format
                })
            )

    return {
        'statusCode': 200,
        'body': json.dumps('File notification processed')
    }
