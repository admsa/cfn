from troposphere import (
  Template,
  Parameter,
  Ref,
  Output,
  GetAtt,
  Sub,
  Base64,
  Join,
  FindInMap
)

from troposphere.s3 import Bucket
import troposphere.ec2 as ec2

def SimpleWebApp():

  template = Template()

  template.add_mapping("RegionMap", {
    "us-east-1": {
      "AMI" : "ami-c481fad3"
    },
    "us-east-2": {
      "AMI" : "ami-71ca9114"
    }
  })

  KeyName = template.add_parameter(Parameter(
    "KeyName",
    Type="AWS::EC2::KeyPair::KeyName",
    Description="The EC2 Key Pair to allow SSH access to the instance"
  ))

  cfnSecurityGroup = template.add_resource(ec2.SecurityGroup(
    "cfnSecurityGroup",
    GroupDescription="Open HTTP and SSH ports",
    SecurityGroupIngress=[
      ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="22",
        ToPort="22",
        CidrIp="0.0.0.0/0",
      ),
      ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="80",
        ToPort="80",
        CidrIp="0.0.0.0/0",
      )
    ]
  ))
  cfnEC2 = template.add_resource(ec2.Instance(
    "cfnEC2",
    SecurityGroups=[Ref(cfnSecurityGroup)],
    KeyName=Ref(KeyName),
    InstanceType="t2.micro",
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    UserData=Base64(Join("", [
        "#!/bin/bash \n",
        "yum update -y aws-cfn-bootstrap \n",
        "/opt/aws/bin/cfn-init -v --stack ",
        Ref("AWS::StackName"),
        " --resource cfnEC2 --configsets cfnInit --region ",
        Ref("AWS::Region"), "\n"
      ]
    ))
  ))

  return template.to_yaml()
