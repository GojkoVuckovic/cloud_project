from aws_cdk import (
    aws_cognito as cognito,
    core as cdk,
    Duration,
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_s3_notifications as s3n,
    aws_lambda_event_sources as lambda_event_sources,
    aws_dynamodb as dynamodb
)
from constructs import Construct
import os

class VideoAppStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        _dirname = os.path.dirname(__file__)

        user_pool = cognito.UserPool(self, 'userpool',
            user_pool_name='movie-app-user-pool',
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                given_name=cognito.StandardAttribute(required=True, mutable=True),
                family_name=cognito.StandardAttribute(required=True, mutable=True)
            ),
            custom_attributes={
                'isAdmin': cognito.StringAttribute(mutable=True)
            },
            password_policy=cognito.PasswordPolicy(
                min_length=6,
                require_lowercase=True,
                require_digits=True,
                require_uppercase=False,
                require_symbols=False
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        domain = user_pool.add_domain('CognitoDomain',
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix='movie-app-team-26-ftn'
            )
        )

        standard_cognito_attributes = {
            'given_name': True,
            'family_name': True,
            'email': True,
            'email_verified': True,
            'address': True,
            'birthdate': True,
            'gender': True,
            'locale': True,
            'middle_name': True,
            'fullname': True,
            'nickname': True,
            'phone_number': True,
            'phone_number_verified': True,
            'profile_picture': True,
            'preferred_username': True,
            'profile_page': True,
            'timezone': True,
            'last_update_time': True,
            'website': True,
        }

        client_read_attributes = cognito.ClientAttributes() \
            .with_standard_attributes(**standard_cognito_attributes) \
            .with_custom_attributes('isAdmin')

        client_write_attributes = cognito.ClientAttributes() \
            .with_standard_attributes(
                **{**standard_cognito_attributes, 'email_verified': False, 'phone_number_verified': False}
            )

        user_pool_client = cognito.UserPoolClient(self, 'web-client',
            user_pool=user_pool,
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                custom=True,
                user_srp=True,
                user_password=True
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    implicit_code_grant=True,
                    authorization_code_grant=True
                ),
                callback_urls=[
                    'https://cloud-movie-app-front-bucket.s3.amazonaws.com/index.html',
                    'http://localhost:4200'
                ],
                logout_urls=[
                    'https://cloud-movie-app-front-bucket.s3.amazonaws.com/index.html',
                    'http://localhost:4200'
                ]
            ),
            supported_identity_providers=[cognito.UserPoolClientIdentityProvider.COGNITO],
            read_attributes=client_read_attributes,
            write_attributes=client_write_attributes
        )

        sign_in_url = domain.sign_in_url(user_pool_client,
            redirect_uri='https://cloud-movie-app-front-bucket.s3.amazonaws.com/index.html'
        )

        cdk.CfnOutput(self, 'userPoolId', value=user_pool.user_pool_id)
        cdk.CfnOutput(self, 'userPoolClientId', value=user_pool_client.user_pool_client_id)
        cdk.CfnOutput(self, 'signInUrl', value=sign_in_url)

        user_authorizer = apigateway.CognitoUserPoolsAuthorizer(self, 'user-pool-authorizer',
            cognito_user_pools=[user_pool]
        )

        authorize_admin_function = _lambda.Function(self, 'AuthorizeAdminFunction',
            runtime=_lambda.Runtime.NODEJS_LATEST,
            handler='handler',
            code=_lambda.Code.from_asset(os.path.join(_dirname, '../lambdas/admin_authorizer.py')),
            timeout=cdk.Duration.seconds(30),
            bundling=_lambda.BundlingOptions(
                node_modules=['aws-jwt-verify']
            ),
            environment={
                'USER_POOL_ID': user_pool.user_pool_id,
                'CLIENT_ID': user_pool_client.user_pool_client_id
            }
        )

        admin_authorizer = apigateway.TokenAuthorizer(self, 'admin-authorizer',
            handler=authorize_admin_function
        )

        # 1. Create S3 Bucket for storing videos
        video_bucket = s3.Bucket(self, 
                                 "VideoBucket",
                                 removal_policy=RemovalPolicy.DESTROY,
                                 cors=[s3.CorsRule(
                                     allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.DELETE],
                                     allowed_origins=["*"],
                                     allowed_headers=["*"]
                                 )],
                                 auto_delete_objects=True,
                                 versioned=True
                                )

        movie_info_table = dynamodb.Table(self, 'MovieInfoTable',
            table_name='movie-app-movie-info',
            partition_key=dynamodb.Attribute(
                name='id',
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            read_capacity=1,
            write_capacity=1,
            stream=dynamodb.StreamViewType.NEW_IMAGE
        )

        movie_search_table = dynamodb.Table(self, 'MovieSearchIndexedTable',
            table_name='movie-app-movie-search',
            partition_key=dynamodb.Attribute(
                name='id',
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            read_capacity=1,
            write_capacity=1
        )
        
        movie_search_table.add_global_secondary_index(
            index_name='SearchIndex',
            partition_key=dynamodb.Attribute(
                name='name',
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # ADD IN UPLOAD MOVIE
        # search_table = dynamodb.Table(search_table_name)
        # search_response = search_table.put_item(
        #     Item={
        #         'id': str(id),
        #         'name': movie_name,
        #         }
        # )

        get_movie_info = _lambda.Function(self, 'GetMovieInfoFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='get_movies_info.get_one',
            code=_lambda.Code.from_asset(os.path.join(_dirname, '../lambdas')),
            timeout=Duration.seconds(30)
        )

        get_movie_info.add_environment("TABLE_NAME", movie_info_table.table_name)

        movie_info_table.grant_read_data(get_movie_info)

        search_movies = _lambda.Function(self, 'GetMoviesFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='movies_search.get_all',
            code=_lambda.Code.from_asset(os.path.join(_dirname, '../lambdas')),
            timeout=Duration.seconds(30)
        )

        search_movies.add_environment('TABLE_NAME', movie_info_table.table_name)
        search_movies.add_environment('SEARCH_TABLE_NAME', movie_search_table.table_name)
        search_movies.add_environment('INDEX_NAME', 'SearchIndex')

        movie_info_table.grant_read_data(search_movies)
        movie_search_table.grant_read_data(search_movies)

        # SQS Queue for transcoding tasks
        transcoding_queue = sqs.Queue(self, 
                                      "TranscodingQueue", 
                                      visibility_timeout=Duration.minutes(10))

        metadata_table = dynamodb.Table(self, "MetadataTable",
            partition_key=dynamodb.Attribute(name="video_id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY  # Adjust as needed
        )

        # Add the table name to Lambda environment variables
        metadata_lambda = _lambda.Function(self, 
            "MetadataLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="upload_metadata.handler",
            code=_lambda.Code.from_asset("lambdas"),
            environment={
                "METADATA_TABLE": metadata_table.table_name
            }
        )


        # 2. Create Upload Lambda function
        upload_lambda = _lambda.Function(self, 
                                         "GenerateUploadURLFunction",
                                         runtime=_lambda.Runtime.PYTHON_3_9,
                                         handler="generate_upload_url.handler",
                                         code=_lambda.Code.from_asset("lambdas"),
                                         environment={
                                             "BUCKET_NAME": video_bucket.bucket_name
                                         })

        # 3. Create Download Lambda function
        download_lambda = _lambda.Function(self, 
                                           "GenerateDownloadURLFunction",
                                           runtime=_lambda.Runtime.PYTHON_3_9,
                                           handler="generate_download_url.handler",
                                           code=_lambda.Code.from_asset("lambdas"),
                                           environment={
                                               "BUCKET_NAME": video_bucket.bucket_name
                                           })

        # Process the uploaded video
        process_upload_lambda = _lambda.Function(self, 
                                                 "ProcessUploadLambda",
                                                 runtime=_lambda.Runtime.PYTHON_3_9,
                                                 handler="process_uploaded_video.handler",
                                                 code=_lambda.Code.from_asset("lambdas"),
                                                 environment={
                                                     "SQS_QUEUE_URL": transcoding_queue.queue_url,
                                                     "BUCKET_NAME": video_bucket.bucket_name,
                                                     "METADATA_TABLE": metadata_table.table_name
                                                 })

        # Define the Lambda layer with FFmpeg
        ffmpeg_layer = _lambda.LayerVersion(self, "FFmpegLayer",
            code=_lambda.Code.from_asset("layer/ffmpeg"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="A layer that contains FFmpeg binary",
        )

        transcode_lambda = _lambda.Function(self, "TranscodeVideoFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="transcode_video.handler",
            code=_lambda.Code.from_asset("lambdas"),
            environment={
                "BUCKET_NAME": video_bucket.bucket_name
            },
            layers=[ffmpeg_layer],
            timeout=Duration.minutes(10),
            memory_size=1024
        )

        # 4. Grant permissions to Lambda functions to access S3 bucket


        # 5. API Gateway setup
        api = apigateway.RestApi(self, 
            "VideoApi",
            rest_api_name="Video Service API",
            description="API for uploading and downloading videos",
            default_cors_preflight_options={
                'allow_origins': apigateway.Cors.ALL_ORIGINS,
                'allow_methods': apigateway.Cors.ALL_METHODS,
                'allow_headers': [
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                    'Access-Control-Allow-Headers',
                    'Access-Control-Allow-Methods'
                ],
                'allow_credentials': True
            }
        )

        movie_info_resource = api.root.add_resource('movie_info')
        get_movie_info_integration = apigateway.LambdaIntegration(get_movie_info)
        movie_info_resource.add_method('GET', get_movie_info_integration, 
            authorizer=user_authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        search_movies_resource = api.root.add_resource('search')
        search_movies_integration = apigateway.LambdaIntegration(search_movies)
        search_movies_resource.add_method('GET', search_movies_integration,
            authorizer=user_authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # 6. Create /upload and /download endpoints
        upload_resource = api.root.add_resource("upload")
        upload_resource.add_method("GET", apigateway.LambdaIntegration(upload_lambda),
                                   authorizer=admin_authorizer)

        download_resource = api.root.add_resource("download")
        download_resource.add_method("GET", apigateway.LambdaIntegration(download_lambda),
                                     authorizer=user_authorizer,
                                     authorization_type=apigateway.AuthorizationType.COGNITO)

        # Create /metadata endpoint for adding metadata separately
        metadata_resource = api.root.add_resource("metadata")
        metadata_resource.add_method("POST", apigateway.LambdaIntegration(metadata_lambda))

        notification = s3n.LambdaDestination(process_upload_lambda)
        video_bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)

        transcode_lambda.add_event_source(lambda_event_sources.SqsEventSource(transcoding_queue))

        # Grant access to necessary resources
        video_bucket.grant_read_write(upload_lambda)
        video_bucket.grant_read(download_lambda)
        video_bucket.grant_read_write(process_upload_lambda)
        video_bucket.grant_read_write(transcode_lambda)

        transcoding_queue.grant_send_messages(process_upload_lambda)
        transcoding_queue.grant_consume_messages(process_upload_lambda)
        transcoding_queue.grant_send_messages(transcode_lambda)
        transcoding_queue.grant_consume_messages(transcode_lambda)

        # Grant permissions to read/write from the DynamoDB table
        metadata_table.grant_read_write_data(process_upload_lambda)
        metadata_table.grant_write_data(metadata_lambda)
        metadata_table.grant_read_write_data(metadata_lambda)
