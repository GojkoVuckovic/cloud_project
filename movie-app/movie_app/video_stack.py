from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    Stack,
    RemovalPolicy
)
from constructs import Construct

class VideoStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3 bucket for storing videos
        video_bucket = s3.Bucket(
            self, 
            "VideoBucket",
        )

        # Lambda function for uploading video files
        upload_lambda = _lambda.Function(
            self,
            "UploadVideoFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="upload.handler",
            code=_lambda.Code.from_asset("lambdas"),
            environment={
                "BUCKET_NAME": video_bucket.bucket_name
            }
        )

        # Lambda function for downloading video files
        download_lambda = _lambda.Function(
            self,
            "DownloadVideoFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="download.handler",
            code=_lambda.Code.from_asset("lambdas"),
            environment={
                "BUCKET_NAME": video_bucket.bucket_name
            }
        )

        # Lambda function for streaming video files
        stream_lambda = _lambda.Function(
            self,
            "StreamVideoFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="stream.handler",
            code=_lambda.Code.from_asset("lambdas"),
            environment={
                "BUCKET_NAME": video_bucket.bucket_name
            }
        )

        video_bucket.grant_read_write(upload_lambda)
        video_bucket.grant_read(download_lambda)

        # Define API Gateway
        api = apigateway.RestApi(self, 
                                 "VideoApi",
                                 binary_media_types=["*/*"])

        # Upload endpoint
        upload_integration = apigateway.LambdaIntegration(upload_lambda)
        upload_resource = api.root.add_resource("upload")
        upload_resource.add_method("POST", upload_integration)

        # Download endpoint
        download_integration = apigateway.LambdaIntegration(download_lambda)
        download_resource = api.root.add_resource("download")
        download_resource.add_method("GET", download_integration)

        # Stream endpoint
        stream_integration = apigateway.LambdaIntegration(stream_lambda)
        stream_resource = api.root.add_resource("stream")
        stream_resource.add_method("GET", stream_integration)
