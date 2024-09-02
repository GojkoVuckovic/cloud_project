from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
)

class MovieAppStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create S3 bucket
        bucket = s3.Bucket(self, "MovieBucket")

        # Create Lambda functions
        upload_lambda = _lambda.Function(self, "UploadVideoFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="upload_video.handler",
            code=_lambda.Code.from_asset("lambdas"),
            environment={
                "BUCKET_NAME": bucket.bucket_name
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

        # Grant Lambda functions permissions to access the S3 bucket
        bucket.grant_read_write(upload_lambda)
        bucket.grant_read(download_lambda)

        # Create API Gateway with binary media types
        api = apigateway.RestApi(self, "MovieApi",
            rest_api_name="Movie Service",
            binary_media_types=["video/mp4"],  # Define the media type to handle binary data
        )

        upload_integration = apigateway.LambdaIntegration(upload_lambda)
        download_integration = apigateway.LambdaIntegration(download_lambda)

        api.root.add_resource("upload").add_method("POST", upload_integration)
        api.root.add_resource("download").add_method("GET", download_integration)

