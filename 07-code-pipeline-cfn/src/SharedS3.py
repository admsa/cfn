import boto3 as aws

from troposphere import Template, Ref, Output
from troposphere.s3 import Bucket

### Generate shared s3 bucket ###
def YAMLTemplate():

  s3Resource         = "cfnSharedS3Bucket"
  s3BucketOutputName = "cfnS3SharedBucketName"

  template = Template()
  s3Bucket = template.add_resource(Bucket(s3Resource, DeletionPolicy="Delete"))
  template.add_output(Output(s3BucketOutputName, Value=Ref(s3Bucket)))

  return {
    'bucketName'       : s3Resource,
    'outputBucketName' : s3BucketOutputName,
    'templateBody'     : template.to_yaml()
  }
