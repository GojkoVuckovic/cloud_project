import os
import boto3

s3 = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']

def handler(event, context):
    file_name = event['file_name']
    file_content = event['file_content']

    s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)

    return {
        'statusCode': 200,
        'body': f"Successfully uploaded {file_name} to {bucket_name}"
    }
