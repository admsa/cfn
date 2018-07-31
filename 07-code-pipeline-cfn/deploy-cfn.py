from src import BasicPipeline, SharedS3, Helpers, SimpleWebApp
import json
import os

### Config file ###
def config():
  config = Helpers.ReadFileContents(".config")
  return json.loads(config)

### Zip the config files ###
def zipConfigs(config):

  testStackConfig = {
    "fileName"   : "test-stack-configuration.json",
    "content": json.dumps(config['TestStackConfiguration'])
  }

  prodStackConfig = {
    "fileName"   : "prod-stack-configuration.json",
    "content": json.dumps(config['ProdStackConfiguration'])
  }

  Helpers.SaveText(config["TempDirectory"], testStackConfig["fileName"], testStackConfig["content"])
  Helpers.SaveText(config["TempDirectory"], prodStackConfig["fileName"], prodStackConfig["content"])

  Helpers.zip(
    config["TempDirectory"],
    config["WebServerZip"],
    [prodStackConfig["fileName"], testStackConfig["fileName"]]
  )

  os.remove(os.path.join(config["TempDirectory"], testStackConfig["fileName"]))
  os.remove(os.path.join(config["TempDirectory"], prodStackConfig["fileName"]))

  return os.path.join(config["TempDirectory"], config["WebServerZip"])

### When file is run directly. Not imported ###
if __name__ == "__main__":

  print(SimpleWebApp.SimpleWebApp())

  #sharedS3      = SharedS3.YAMLTemplate()
  #config = config()
  #zipPath = zipConfigs(config)

  #print(zipPath)

  """
  sharedS3      = SharedS3.YAMLTemplate()
  stackName     = sharedS3['bucketName']
  s3TemplateBody= sharedS3['templateBody']
  sharedS3Stack = Helpers.CreateStack(stackName, s3TemplateBody)

  if sharedS3Stack is None:
    print(sharedS3Stack)
  """
  #tpl = BasicPipeline.YAMLTemplate()
  #print(tpl['templateBody'])
