from troposphere import Template, Parameter, Ref, Output, GetAtt, Sub
from troposphere.s3 import Bucket, VersioningConfiguration
from troposphere.sns import Subscription, Topic
from troposphere.iam import Role, Policy
from troposphere.codepipeline import (
    Pipeline, Stages, Actions, ActionTypeId, OutputArtifacts, InputArtifacts,
    ArtifactStore, DisableInboundStageTransitions)


### Basic code pipeline template ###
def YAMLTemplate():

  template = Template()

  template.add_metadata({
    "AWS::CloudFormation::Interface": {
      "ParameterGroups": [
        {
          "Label": {
            "default": "CodePipeline Settings"
          },
          "Parameters": [
            "PipelineName",
            "S3Bucket",
            "SourceS3Key",
            "Email"
          ]
        },
        {
          "Label": {
            "default": "Test Stack Settings"
          },
          "Parameters": [
            "TestStackName",
            "TemplateFileName",
            "TestStackConfig"
          ]
        },
        {
          "Label": {
            "default": "Production Stack Settings"
          },
          "Parameters": [
            "ChangeSetName",
            "ProdStackName",
            "ProdStackConfig"
          ]
        }
      ]
    }
  })

  PipelineName = template.add_parameter(Parameter(
    "PipelineName",
    Type="String",
    Description="A name for pipeline"
  ))

  S3Bucket = template.add_parameter(Parameter(
    "S3Bucket",
    Type="String",
    Description="The name of the S3 bucket that contains the source artifact, which must be in the same region as this stack"
  ))

  SourceS3Key = template.add_parameter(Parameter(
    "SourceS3Key",
    Type="String",
    Default="wordpress-single-instance.zip",
    Description="The file name of the source artifact, such as myfolder/myartifact.zip"
  ))

  TemplateFileName = template.add_parameter(Parameter(
    "TemplateFileName",
    Type="String",
    Default="wordpress-single-instance.yaml",
    Description="The file name of the WordPress template"
  ))

  TestStackName = template.add_parameter(Parameter(
    "TestStackName",
    Type="String",
    Default="Test-MyWordPressSite",
    Description="A name for the test WordPress stack"
  ))

  TestStackConfig = template.add_parameter(Parameter(
    "TestStackConfig",
    Type="String",
    Default="test-stack-configuration.json",
    Description="The configuration file name for the test WordPress stack"
  ))

  ProdStackName = template.add_parameter(Parameter(
    "ProdStackName",
    Type="String",
    Default="Prod-MyWordPressSite",
    Description="A name for the production WordPress stack"
  ))

  ProdStackConfig = template.add_parameter(Parameter(
    "ProdStackConfig",
    Type="String",
    Default="prod-stack-configuration.json",
    Description="The configuration file name for the production WordPress stack"
  ))

  ChangeSetName = template.add_parameter(Parameter(
    "ChangeSetName",
    Type="String",
    Default="UpdatePreview-MyWordPressSite",
    Description="A name for the production WordPress stack change set"
  ))

  Email = template.add_parameter(Parameter(
    "Email",
    Type="String",
    Description="The email address where CodePipeline sends pipeline notifications"
  ))

  #------------Template Resources------------#
  ArtifactStoreBucket = template.add_resource(Bucket(
    "ArtifactStoreBucket",
    VersioningConfiguration=VersioningConfiguration(Status="Enabled")
  ))

  CodePipelineSNSTopic = template.add_resource(Topic(
    "CodePipelineSNSTopic",
    Subscription=[
      Subscription(Protocol="email", Endpoint=Ref(Email))
    ]
  ))

  CFNRole = template.add_resource(Role(
    "CFNRole",
    Path="/",
    Policies=[Policy(
      PolicyName="CloudFormationRole",
      PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["ec2:*"],
            "Effect": "Allow",
            "Resource": "*"
        }]
      }
    )],
    AssumeRolePolicyDocument={
      "Version": "2012-10-17",
      "Statement": [{
        "Action": ["sts:AssumeRole"],
        "Effect": "Allow",
        "Principal": {
          "Service": ["cloudformation.amazonaws.com"]
        }
      }]
    }
  ))

  PipelineRole = template.add_resource(Role(
    "PipelineRole",
    Path="/",
    Policies=[Policy(
      PolicyName="CodePipelineAccess",
      PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": [
              "s3:*",
              "cloudformation:CreateStack",
              "cloudformation:DescribeStacks",
              "cloudformation:DeleteStack",
              "cloudformation:UpdateStack",
              "cloudformation:CreateChangeSet",
              "cloudformation:ExecuteChangeSet",
              "cloudformation:DeleteChangeSet",
              "cloudformation:DescribeChangeSet",
              "cloudformation:SetStackPolicy",
              "iam:PassRole",
              "sns:Publish"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }]
      }
    )],
    AssumeRolePolicyDocument={
      "Version": "2012-10-17",
      "Statement": [{
        "Action": ["sts:AssumeRole"],
        "Effect": "Allow",
        "Principal": {
          "Service": ["codepipeline.amazonaws.com"]
        }
      }]
    }
  ))

  cfnPipeline = template.add_resource(Pipeline(
    "Pipeline",
    ArtifactStore=ArtifactStore(
      Type="S3",
      Location=Ref(ArtifactStoreBucket)
    ),
    DisableInboundStageTransitions=[],
    RoleArn=GetAtt(PipelineRole, "Arn"),
    Stages=[
      Stages(
        Name="S3Source",
        Actions=[
          Actions(
            Name="TemplateSource",
            ActionTypeId=ActionTypeId(
              Category="Source",
              Provider="S3",
              Owner="AWS",
              Version="1"
            ),
            Configuration={
              "S3Bucket": Ref(S3Bucket),
              "S3ObjectKey": Ref(SourceS3Key)
            },
            OutputArtifacts=[
              OutputArtifacts(
                Name="TemplateSource"
              )
            ],
            RunOrder="1"
          )
        ]
      ),
      Stages(
        Name="TestStage",
        Actions=[
          Actions(
            Name="CreateStack",
            ActionTypeId=ActionTypeId(
              Category="Deploy",
              Provider="CloudFormation",
              Owner="AWS",
              Version="1"
            ),
            InputArtifacts=[
              InputArtifacts(
                Name="TemplateSource"
              )
            ],
            Configuration={
              "ActionMode": "REPLACE_ON_FAILURE",
              "RoleArn": GetAtt(CFNRole, "Arn"),
              "StackName": Ref(TestStackName),
              "TemplateConfiguration": Sub("TemplateSource::${TestStackConfig}"),
              "TemplatePath": Sub("TemplateSource::${TemplateFileName}")
            },
            RunOrder="1"
          ),
          Actions(
            Name="ApproveTestStack",
            ActionTypeId=ActionTypeId(
              Category="Approval",
              Provider="Manual",
              Owner="AWS",
              Version="1"
            ),
            Configuration={
              "NotificationArn": Ref(CodePipelineSNSTopic),
              "CustomData": Sub("Do you want to create a change set against the production stack and delete the ${TestStackName} stack?")
            },
            RunOrder="2"
          ),
          Actions(
            Name="DeleteTestStack",
            ActionTypeId=ActionTypeId(
              Category="Deploy",
              Provider="CloudFormation",
              Owner="AWS",
              Version="1"
            ),
            Configuration={
              "ActionMode": "DELETE_ONLY",
              "RoleArn": GetAtt(CFNRole, "Arn"),
              "StackName": Ref(TestStackName)
            },
            RunOrder="3"
          )
        ]
      ),
      Stages(
        Name="ProdStage",
        Actions=[
          Actions(
            Name="CreateChangeSet",
            ActionTypeId=ActionTypeId(
              Category="Deploy",
              Provider="CloudFormation",
              Owner="AWS",
              Version="1"
            ),
            InputArtifacts=[
              InputArtifacts(
                Name="TemplateSource"
              )
            ],
            Configuration={
              "ActionMode": "CHANGE_SET_REPLACE",
              "RoleArn": GetAtt(CFNRole, "Arn"),
              "StackName": Ref(ProdStackName),
              "TemplateConfiguration": Sub("TemplateSource::${ProdStackConfig}"),
              "TemplatePath": Sub("TemplateSource::${TemplateFileName}")
            },
            RunOrder="1"
          ),
          Actions(
            Name="ApproveChangeSet",
            ActionTypeId=ActionTypeId(
              Category="Approval",
              Provider="Manual",
              Owner="AWS",
              Version="1"
            ),
            Configuration={
              "NotificationArn": Ref(CodePipelineSNSTopic),
              "CustomData": Sub("A new change set was created for the ${ProdStackName} stack. Do you want to implement the changes?")
            },
            RunOrder="2"
          ),
          Actions(
            Name="ExecuteChangeSet",
            ActionTypeId=ActionTypeId(
              Category="Deploy",
              Provider="CloudFormation",
              Owner="AWS",
              Version="1"
            ),
            Configuration={
              "ActionMode": "CHANGE_SET_EXECUTE",
              "RoleArn": GetAtt(CFNRole, "Arn"),
              "StackName": Ref(ProdStackName),
              "ChangeSetName": Ref(ChangeSetName)
            },
            RunOrder="3"
          )
        ]
      )
    ]
  ))

  return {
    'templateBody': template.to_yaml()
  }


