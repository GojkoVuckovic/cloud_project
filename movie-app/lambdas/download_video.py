import os
import boto3

s3 = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']

def handler(event, context):
    file_name = event['file_name']

    video = s3.get_object(Bucket=bucket_name, Key=file_name)

    return {
        'statusCode': 200,
        'body': video['Body'].read()
    }
