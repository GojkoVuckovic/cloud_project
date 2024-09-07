#!/usr/bin/env python3

import aws_cdk as cdk

from movie_app.new_stack import NewStack


app = cdk.App()
video_stack = NewStack(app, "NewStack")

app.synth()