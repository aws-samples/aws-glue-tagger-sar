#!/bin/bash

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# verify params
if [ -z "$S3_BUCKET_ASSETS" ]; then echo "Environment variable S3_BUCKET_ASSETS is not set"; exit; fi;
if [ -z "$S3_PREFIX_ASSETS" ]; then echo "Environment variable S3_PREFIX_ASSETS is not set"; exit; fi;

# Install lambda dependencies
cd infrastructure/glue_tagger_cr && pip install -r requirements.txt --target . && cd ../

# Package CloudFormation template
aws cloudformation package \
  --template-file glue_tagger.yaml \
  --output-template-file packaged_glue_tagger.yaml \
  --s3-bucket "$S3_BUCKET_ASSETS" \
  --s3-prefix "$S3_PREFIX_ASSETS"

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file packaged_glue_tagger.yaml \
  --stack-name cr-glue-tagger \
  --capabilities CAPABILITY_IAM
