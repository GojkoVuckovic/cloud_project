from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)

class NewStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket for video uploads
        video_bucket = s3.Bucket(self, 
                                 "VideoBucket",
                                 removal_policy=RemovalPolicy.DESTROY)  # Bucket is destroyed when stack is deleted

        # Define the Lambda function for uploading videos
        upload_video_lambda = _lambda.Function(self, 
                                               "UploadVideoLambda",
                                               runtime=_lambda.Runtime.PYTHON_3_9,
                                               handler="upload_video.handler",
                                               code=_lambda.Code.from_asset("lambdas"),  # Folder where the Lambda code is stored
                                               environment={
                                                   "BUCKET_NAME": video_bucket.bucket_name
                                               })

        # Define the Lambda function for downloading videos
        download_video_lambda = _lambda.Function(self, 
                                                 "DownloadVideoLambda",
                                                 runtime=_lambda.Runtime.PYTHON_3_9,
                                                 handler="download_video.handler",
                                                 code=_lambda.Code.from_asset("lambdas"),
                                                 environment={
                                                     "BUCKET_NAME": video_bucket.bucket_name
                                                 })

        # Grant S3 permissions to the Lambda functions
        video_bucket.grant_read_write(upload_video_lambda)
        video_bucket.grant_read(download_video_lambda)

        # Create an API Gateway REST API
        api = apigateway.RestApi(self, 
                                 "VideoApi",
                                 rest_api_name="Video Service",
                                 description="This service handles video uploads and downloads.")

        # Create a resource and method for uploading videos
        upload_resource = api.root.add_resource("upload")
        upload_resource.add_method("GET", apigateway.LambdaIntegration(upload_video_lambda))

        # Create a resource and method for downloading videos
        download_resource = api.root.add_resource("download")
        download_resource.add_method("GET", apigateway.LambdaIntegration(download_video_lambda))
