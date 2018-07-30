from src import BasicPipeline

### When file is run directly. Not imported ###
if __name__ == "__main__":

  """
  sharedS3      = shared_s3_template()
  sharedS3Stack = create_shared_s3_stack(sharedS3['bucketName'], sharedS3['templateBody'])

  if sharedS3Stack is None:
    print(sharedS3Stack)
  """
  tpl = BasicPipeline.YAMLTemplate()
  print(tpl['templateBody'])
