import boto3 as aws

### Save as yaml file ###
def SaveAsYAML(file_name, contents=None):
  with open(file_name+".yaml", "w") as text:
    text.write(contents)

### Upload zipped cloudformation template to shared s3 bucket ###
def UploadToBucket(FilePath, BucketName, FileName):
  s3 = aws.client('s3')
  with open(FilePath, 'rb') as data:
      s3.upload_fileobj(data, BucketName, FileName)
  return None

### Created shared s3 cloudformation stack ###
def CreateStack(BucketName, TemplateBody):
  try:

    cloudFormation   = aws.client('cloudformation')
    cfnS3SharedStack = cloudFormation.create_stack(StackName=BucketName, TemplateBody=TemplateBody)

    waiter = cloudFormation.get_waiter('stack_create_complete')
    return waiter.wait(StackName=BucketName)

  except Exception as e:
    return False