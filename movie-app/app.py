#!/usr/bin/env python3

import aws_cdk as cdk

from movie_app.video_app_stack import VideoAppStack


app = cdk.App()
video_stack = VideoAppStack(app, "VideoAppStack")

app.synth()