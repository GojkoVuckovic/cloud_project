from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    RemovalPolicy
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

        # 4. Grant permissions to Lambda functions to access S3 bucket
        video_bucket.grant_read_write(upload_lambda)
        video_bucket.grant_read(download_lambda)

        # 5. API Gateway setup
        api = apigateway.RestApi(self, 
                                 "VideoApi",
                                 rest_api_name="Video Service API",
                                 description="API for uploading and downloading videos")

        # 6. Create /upload and /download endpoints
        upload_resource = api.root.add_resource("upload")
        upload_resource.add_method("GET", apigateway.LambdaIntegration(upload_lambda))

        download_resource = api.root.add_resource("download")
        download_resource.add_method("GET", apigateway.LambdaIntegration(download_lambda))