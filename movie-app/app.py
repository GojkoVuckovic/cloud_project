#!/usr/bin/env python3

import aws_cdk as cdk

from movie_app.movie_app_stack import MovieAppStack


app = cdk.App()
video_stack = MovieAppStack(app, "MovieAppStack")

app.synth()