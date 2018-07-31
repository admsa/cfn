from src import Helpers
import json, os

### Config file ###
def config():
  config = Helpers.ReadFileContents(".config")
  return json.loads(config)

### Zip the config files ###
def zipConfigs(config):

  base_dir = "./templates/ec2-instance"
  files = ["test-stack-configuration.json", "prod-stack-configuration.json", "simple-web-app.yaml"]

  # Save to temporary directory
  for file in files:
    Helpers.SaveText(config["temp_directory"], file, Helpers.ReadFileContents(os.path.join(base_dir, file)))

  # Zip the files
  Helpers.zip(config["temp_directory"], config["zip_name"], files)

  # Removed individual files
  for file in files:
    os.remove(os.path.join(config["temp_directory"], file))

  return os.path.join(config["temp_directory"], config["zip_name"])

### When file is run directly. Not imported ###
if __name__ == "__main__":
  config = config()
  zipPath = zipConfigs(config)
  print(zipPath)
