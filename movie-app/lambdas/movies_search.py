import json
import os
import boto3
import traceback
from boto3.dynamodb.conditions import Attr, Key

table_name = os.environ['TABLE_NAME']
search_table_name = os.environ['SEARCH_TABLE_NAME']
index_name=os.environ['INDEX_NAME']
    
def get_all(event, context):
    try:
        params = event['queryStringParameters']
        movie_name = params.get('name')
        actors = params.get('actors')
        director = params.get('director')
        genres = params.get('genres')
        
        dynamodb = boto3.resource('dynamodb')
        search_table = dynamodb.Table(search_table_name)
        table = dynamodb.Table(table_name)
        found_movies = []

        key_condition_expression = Key('name').eq(movie_name) if movie_name else None

        if key_condition_expression:
        
            filter_expressions = []
            if actors:
                filter_expressions.append(Attr('actors').contains(actors))
            if director:
                filter_expressions.append(Attr('director').contains(director))
            if genres:
                filter_expressions.append(Attr('genre').contains(genres))
            
            response = search_table.query(
                IndexName = index_name,
                KeyConditionExpression = key_condition_expression
            )
            
            if 'Items' in response:
                movie_ids = response['Items']
                for item in movie_ids:
                    second_response = table.get_item(
                        Key={'id': item['id']}
                    )
                    if 'Item' in second_response:
                        movie = second_response['Item']
                        if not filter_expressions or all(expr(movie) for expr in filter_expressions):
                            found_movies.append(movie)

        else:
            actors = actors.split(',') if actors else []
            genres = genres.split(',') if genres else []

            filter_expressions = []

            if movie_name:
                filter_expressions.append(Attr('name').contains(movie_name))

            if director:
                filter_expressions.append(Attr('director').contains(director))

            for actor in actors:
                filter_expressions.append(Attr('actors').contains(actor))

            for genre in genres:
                filter_expressions.append(Attr('genres').contains(genre))

            combined_filter_expression = None

            if filter_expressions:
                combined_filter_expression = filter_expressions[0]
                for expression in filter_expressions[1:]:
                    combined_filter_expression = combined_filter_expression & expression

                response = table.scan(
                    FilterExpression = combined_filter_expression
                )
            else:
                response = table.scan()
                found_movies = response['Items']

        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Origin': '*' 
            },
            'body': json.dumps(found_movies, default=str)
        }
    
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print('#BODY')
        print(event['body'])
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }