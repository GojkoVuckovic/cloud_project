import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
metadata_table = dynamodb.Table(os.environ['METADATA_TABLE'])

def handler(event, context):
    try:
        body = json.loads(event['body'])
        video_id = body['video_id']
        metadata = {
            'actors': body.get('actors', []),
            'director': body.get('director', ''),
            'genre': body.get('genre', '')
        }

        # Update the metadata in DynamoDB
        metadata_table.update_item(
            Key={'video_id': video_id},
            UpdateExpression="SET actors = :a, director = :d, genre = :g",
            ExpressionAttributeValues={
                ':a': metadata['actors'],
                ':d': metadata['director'],
                ':g': metadata['genre']
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Metadata updated successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
