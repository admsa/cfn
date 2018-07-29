import boto3 as aws

from troposphere import Output, Ref, Template
from troposphere.s3 import Bucket

### Save as yaml file ###
def save_as_yaml(file_name, contents=None):
  with open(file_name+".yaml", "w") as text:
    text.write(contents)

### Generate shared s3 bucket ###
def shared_s3_template():

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

### Created shared s3 cloudformation stack ###
def create_shared_s3_stack(BucketName, TemplateBody):
  try:

    cloudFormation   = aws.client('cloudformation')
    cfnS3SharedStack = cloudFormation.create_stack(StackName=BucketName, TemplateBody=TemplateBody)

    waiter = cloudFormation.get_waiter('stack_create_complete')
    return waiter.wait(StackName=BucketName)

  except Exception as e:
    return False

### Upload zipped cloudformation template to shared s3 bucket
def upload_template_to_s3(FilePath, BucketName, FileName):
  s3 = aws.client('s3')
  with open(FilePath, 'rb') as data:
      s3.upload_fileobj(data, BucketName, FileName)
  return None

### When file is run directly. Not imported ###
if __name__ == "__main__":

  sharedS3      = shared_s3_template()
  sharedS3Stack = create_shared_s3_stack(sharedS3['bucketName'], sharedS3['templateBody'])

  if sharedS3Stack is None:
    print(sharedS3Stack)
