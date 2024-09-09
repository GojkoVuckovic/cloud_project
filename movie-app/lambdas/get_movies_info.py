import json
import os
import boto3

table_name = os.environ['TABLE_NAME']

def get_one(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        movie_id = event['queryStringParameters']['id']

        movie_table = dynamodb.Table(table_name)
        response = movie_table.get_item(Key={'id': movie_id})
                                    
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item'], default=str),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
        }
    except Exception as e:
        return {
            'statusCode': 404,
            'body': 'Error: {}'.format(str(e))
        }