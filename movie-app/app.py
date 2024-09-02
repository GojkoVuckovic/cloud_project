#!/usr/bin/env python3

import aws_cdk as cdk

from movie_app.video_stack import VideoStack


app = cdk.App()
video_stack = VideoStack(app, "VideoStack")

app.synth()