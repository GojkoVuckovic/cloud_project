from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_lambda_event_sources as lambda_event_sources,
    Duration,
    aws_sqs as sqs,
    aws_dynamodb as dynamodb
)

class MovieAppStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket(self, "MovieBucket")

        video_queue = sqs.Queue(self, "VideoQueue",
            visibility_timeout=Duration.minutes(5)
        )

        transcoding_queue = sqs.Queue(
            self, "TranscodingQueue",
            visibility_timeout=Duration.seconds(300)
        )

        table = dynamodb.Table(
            self, "VideoMetadataTable",
            partition_key=dynamodb.Attribute(name="video_id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )


        upload_lambda = _lambda.Function(self, "UploadVideoFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="upload_video.handler",
            code=_lambda.Code.from_asset("lambdas"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "METADATA_TABLE_NAME": table.table_name,
                "TRANSCODE_QUEUE_URL": transcoding_queue.queue_url
            }
        )

        download_lambda = _lambda.Function(self, "DownloadVideoFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="download_video.handler",
            code=_lambda.Code.from_asset("lambdas"),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            }
        )

        transcode_lambda = _lambda.Function(self, "TranscodeVideoFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="transcode_video.handler",
            code=_lambda.Code.from_asset("lambdas"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "TABLE_NAME": table.table_name
            }
        )

        bucket.grant_read_write(upload_lambda)
        bucket.grant_read(download_lambda)
        bucket.grant_read_write(transcode_lambda)
        table.grant_read_write_data(upload_lambda)
        table.grant_read_write_data(transcode_lambda)
        transcoding_queue.grant_send_messages(upload_lambda)
        transcoding_queue.grant_consume_messages(transcode_lambda)

        transcode_lambda.add_event_source(lambda_event_sources.SqsEventSource(transcoding_queue))

        api = apigateway.RestApi(self, "MovieApi",
            rest_api_name="Movie Service",
            binary_media_types=["*/*"],
        )

        upload_integration = apigateway.LambdaIntegration(upload_lambda)
        download_integration = apigateway.LambdaIntegration(download_lambda)

        api.root.add_resource("upload").add_method("POST", upload_integration)
        api.root.add_resource("download").add_method("GET", download_integration)

