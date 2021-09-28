# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Export environment variables
export S3_BUCKET_ASSETS=<CHANGE_ME>

# Install lambda dependencies
cd infrastructure/glue_tagger_cr && pip install -r requirements.txt --target . && cd ../

# Package CloudFormation template
aws cloudformation package \
  --template-file glue_tagger.yaml \
  --output-template-file packaged_glue_tagger.yaml \
  --s3-bucket $S3_BUCKET_ASSETS

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file packaged_glue_tagger.yaml \
  --stack-name cr-glue-tagger \
  --capabilities CAPABILITY_IAM
