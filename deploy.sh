#!/bin/bash

# Configuration
STACK_NAME="alarm-manager-stack"
S3_BUCKET="alarm-manager-deployment-$(date +%s)"
MONITORED_FUNCTIONS="my-lambda-1,my-lambda-2,my-lambda-3"

echo "Creating S3 bucket for deployment..."
aws s3 mb s3://$S3_BUCKET

echo "Packaging SAM application..."
sam package \
  --template-file template.yaml \
  --output-template-file packaged.yaml \
  --s3-bucket $S3_BUCKET

echo "Deploying stack..."
sam deploy \
  --template-file packaged.yaml \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides MonitoredFunctions=$MONITORED_FUNCTIONS

echo "Getting API URL..."
API_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

echo "Getting Website Bucket..."
WEBSITE_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Resources[?LogicalResourceId==`WebsiteBucket`].PhysicalResourceId' \
  --output text)

echo "Updating index.html with API URL..."
sed "s|YOUR_API_GATEWAY_URL|$API_URL|g" index.html > index_updated.html

echo "Uploading website to S3..."
aws s3 cp index_updated.html s3://$WEBSITE_BUCKET/index.html --content-type "text/html"

WEBSITE_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`WebsiteUrl`].OutputValue' \
  --output text)

echo "=========================================="
echo "Deployment Complete!"
echo "API URL: $API_URL"
echo "Website URL: $WEBSITE_URL"
echo "=========================================="
