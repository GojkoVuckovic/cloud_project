#!/usr/bin/env python3

import aws_cdk as cdk

from movie_app.movie_app_stack import MovieAppStack


app = cdk.App()
MovieAppStack(app, "MovieAppStack")

app.synth()
