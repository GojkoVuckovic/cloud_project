from aws_cdk import (
    Duration,
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    RemovalPolicy,
    aws_sqs as sqs,
    aws_s3_notifications as s3n,
    aws_lambda_event_sources as lambda_event_sources,
    aws_dynamodb as dynamodb
)
from constructs import Construct

class VideoAppStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 1. Create S3 Bucket for storing videos
        video_bucket = s3.Bucket(self, 
                                 "VideoBucket",
                                 removal_policy=RemovalPolicy.DESTROY,
                                 cors=[s3.CorsRule(
                                     allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.DELETE],
                                     allowed_origins=["*"],
                                     allowed_headers=["*"]
                                 )]
                                )

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
        
        # API Gateway setup
        api = apigateway.RestApi(self, 
                                 "VideoApi",
                                 rest_api_name="Video Service API",
                                 description="API for uploading and downloading videos")

        # Create /upload and /download endpoints
        upload_resource = api.root.add_resource("upload")
        upload_resource.add_method("GET", apigateway.LambdaIntegration(upload_lambda))

        download_resource = api.root.add_resource("download")
        download_resource.add_method("GET", apigateway.LambdaIntegration(download_lambda))

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
