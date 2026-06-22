#!/bin/sh
set -eu

###
### Script to deploy S3 bucket in cloudformation stack
###

#### CONFIGURATION SECTION ####
aws_profile="KalebDE" # e.g. sot-academy, for the aws credentials
team_name="roamingrhubarbs" # e.g. rory-gilmore (WITH DASHES), for the stack name
region="eu-west-1"
#### CONFIGURATION SECTION ####

# Deploy the stack
echo ""
echo "Doing deployment stack deployment..."
echo ""
aws cloudformation deploy --stack-name ${team_name}-deployment-stack \
    --template-file deployment-stack.yml --region ${region} \
    --capabilities CAPABILITY_NAMED_IAM \
    --profile ${aws_profile};

DEPLOYMENT_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name ${team_name}-deployment-stack \
    --region ${region} \
    --profile ${aws_profile} \
    --query "Stacks[0].Outputs[?OutputKey=='DeploymentBucketName'].OutputValue" \
    --output text)

echo ""
echo "...all done!"
echo ""

echo "Packaging Lambda Function"
cd lambda
zip lambda.zip lambda_function.py
cd ..
echo "Packaged Lambda Function"

echo "Uploading Lambda"
aws s3 cp \
lambda/lambda.zip \
s3://$DEPLOYMENT_BUCKET/lambda.zip \
--region ${region} \
--profile ${aws_profile};
echo "Uploaded Lambda"


echo ""
echo "Doing etl stack deployment..."
echo ""
aws cloudformation deploy --stack-name ${team_name}-ETL-stack \
    --template-file etl-stack.yml \
    --region eu-west-1 \
    --capabilities CAPABILITY_NAMED_IAM \
    --profile ${aws_profile} \
    --parameter-overrides \
      DeploymentBucketName="${DEPLOYMENT_BUCKET}";


echo ""
echo "...all done!"
echo ""
