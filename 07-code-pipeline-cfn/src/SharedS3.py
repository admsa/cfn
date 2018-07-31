import boto3 as aws

from troposphere import Template, Ref, Output
from troposphere.s3 import Bucket

### Generate shared s3 bucket ###
def YAMLTemplate():

  s3BucketOutputName = "cfnS3SharedBucketName"

  template = Template()
  s3Bucket = template.add_resource(Bucket("cfnSharedS3Bucket", DeletionPolicy="Delete"))
  template.add_output(Output(s3BucketOutputName, Value=Ref(s3Bucket)))

  return {
    'outputBucketKey' : s3BucketOutputName,
    'templateBody'    : template.to_yaml()
  }
