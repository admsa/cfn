import boto3 as aws
import zipfile, os

### Upload zipped cloudformation template to shared s3 bucket ###
def UploadToBucket(FilePath, BucketName, FileName):
  s3 = aws.client('s3')
  with open(FilePath, 'rb') as data:
      s3.upload_fileobj(data, BucketName, FileName)
  return None

### Created shared s3 cloudformation stack ###
def CreateStack(StackName, TemplateBody):
  try:

    cloudFormation   = aws.client('cloudformation')
    cfnS3SharedStack = cloudFormation.create_stack(StackName=StackName, TemplateBody=TemplateBody)

    waiter = cloudFormation.get_waiter('stack_create_complete')
    return waiter.wait(StackName=StackName)

  except Exception as e:
    return False

### Zip files ###
# [stackoverflow]/questions/35937121/python-zip-folder-without-including-current-directory
def zip(BasePath, ZipName, Files=[]):
  base_dir  = os.path.abspath(BasePath)
  base_path = os.path.normpath(base_dir)
  with zipfile.ZipFile(os.path.join(BasePath, ZipName), "w", compression=zipfile.ZIP_DEFLATED) as zip:
    for dirpath, dirnames, filenames in os.walk(base_dir):
      for name in filenames:
        path = os.path.normpath(os.path.join(dirpath, name))
        file = os.path.relpath(path, base_path)
        if os.path.isfile(path) and file in Files:
          zip.write(path, os.path.relpath(path, base_path))

### Save to a file ###
def SaveText(Path, File, Contents=None):
  with open(os.path.join(Path, File), "w") as text:
    text.write(Contents)

### Read contents of a file ###
def ReadFileContents(Path):
  with open(Path, 'r') as content:
      contents = content.read()
  return contents