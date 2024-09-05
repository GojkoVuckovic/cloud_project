# lambdas/transcode.py
import os
import boto3
import json

s3_client = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']

def handler(event, context):
    for record in event['Records']:
        message = json.loads(record['body'])
        video_id = message['video_id']
        file_name = message['file_name']
        format = message['format']

        # Simulate the transcoding process
        transcoded_file_name = f"{format}/{video_id}.mp4"
        s3_client.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': file_name},
            Key=transcoded_file_name
        )

        print(f"Transcoded {file_name} to {transcoded_file_name} in {format} format.")
