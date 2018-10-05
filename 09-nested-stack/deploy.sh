#!/bin/bash

#./deploy.sh create-stack
    #--parent-template parent-cfn.yaml
    #--bucket-name cf-templates-uahyo2oen0xe-us-east-1
    #--region us-east-1

AWS_REGION=""
S3_BUCKET=""
PARENT_TEMPLATE=""
STACK_NAME=""
CFN_ACTION=""

TEMP_DIR="templates"
PATTERN="*cfn.yaml"

function execute() {
  mkdir $TEMP_DIR

  find . -name "${PATTERN}"|while read fname; do
    cp --parents $fname $TEMP_DIR
  done

  echo "Uploading template to S3 Bucket..."

  find $TEMP_DIR -name "${PATTERN}"|while read fname; do
    sed -i -e "s/{TEMPLATE_BUCKET}/${S3_BUCKET}/g" $fname
    #aws --region ${AWS_REGION:-us-east-1} s3 cp $(readlink -f "${fname}") s3://${S3_BUCKET}/ --acl public-read --recursive
  done

  aws --region ${AWS_REGION:-us-east-1} s3 cp $TEMP_DIR s3://${S3_BUCKET}/ --acl public-read --recursive

  echo "Processing CloudFormation stack..."
  aws --region ${AWS_REGION:-us-east-1} cloudformation ${CFN_ACTION} \
      --stack-name ${STACK_NAME:-serverless-stack} \
      --template-url https://s3.amazonaws.com/${S3_BUCKET}/${PARENT_TEMPLATE} \
      --capabilities CAPABILITY_IAM

  rm -rf $TEMP_DIR
}

function help() {
cat << EOF
Usage: ${0} create-stack|update-stack (-s|-p|-c|-b|-r)

COMMANDS:
  create-stack              Create CloudFormation stack
  update-stack              Update CloudFormation stack
  help                      Show help message

OPTIONS:
  -s|--stack-name           CloudFormation stack name
  -p|--parent-template      Parent template body
  -b|--bucket-name          S3 bucket name
  -r|--region               AWS region


EXAMPLES:
  Show help message:
    $ deploy help

  Creating CloudFormation stack:
    $ deploy create-stack --stack-name sample-stack
      --parent-template file://./parent-cfn.yaml
      --bucket-name sample-bucket

  Updating CloudFormation stack:
    $ deploy update-stack --stack-name sample-stack
      --parent-template file://./parent-cfn.yaml
      --bucket-name sample-bucket
EOF
}

function options() {
  while [[ $1 > 0 ]]
  do
  case "${1}" in
    -s|--stack-name)
    #stack_name "${2}" #as parameter
    STACK_NAME=${2}
    shift
    ;;
    -p|--parent-template)
    PARENT_TEMPLATE=${2}
    shift
    ;;
    -b|--bucket-name)
    S3_BUCKET=${2}
    shift
    ;;
    -r|--region)
    AWS_REGION=${2}
    shift
    ;;
  esac
  shift
  done

  # Execute command
  execute

}

while [[ $# > 0 ]]
do
case "${1}" in
  create-stack)
  CFN_ACTION="${1}"
  echo 'Creating stack'
  shift
  options $@
  break
  ;;
  update-stack)
  CFN_ACTION="${1}"
  echo 'Updating stack'
  shift
  options $@
  break
  ;;
  help)
  help
  break
  ;;
  *)
  echo "${1} is not a valid flag, try running: ${0} --help"
  ;;
esac
done

