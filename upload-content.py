import json
import base64
import boto3
import string
import random



def lambda_handler(event, context):
    s3 = boto3.client("s3")

    print(event)

    get_file_content = event["content"]

    decode_content = base64.b64decode(get_file_content)
    
    

    pic_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    s3_upload = s3.put_object(Bucket="uploady-movie-bucket",Key=pic_filename+".mp4",Body=decode_content)

    return {

        'statusCode': 200,

        'body': json.dumps('The Object is Uploaded successfully!')

    }