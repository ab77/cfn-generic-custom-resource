#!/usr/bin/env python

import os
import sys
import boto3


class AUTOSCALING:

    def __init__(self, *args, **kwargs):
        self.verbose = bool(int(os.getenv('VERBOSE', 0)))
        if self.verbose: print(
            'args: {}, kwargs: {}'.format(args, kwargs),
            file=sys.stderr
        )


    def filter_launch_configuration(self, *args, **kwargs):
        if self.verbose: print(
            'args: {}, kwargs: {}'.format(args, kwargs),
            file=sys.stderr
        )

        kwargs['launch_template_data'].pop('LaunchConfigurationName', None)
        kwargs['launch_template_data'].pop('LaunchConfigurationARN', None)
        kwargs['launch_template_data'].pop('ClassicLinkVPCSecurityGroups', None)
        kwargs['launch_template_data'].pop('RamdiskId', None)
        kwargs['launch_template_data'].pop('InstanceMonitoring', None)
        kwargs['launch_template_data'].pop('CreatedTime', None)
        kwargs['launch_template_data'].pop('KernelId', None)
        instance_profile_name = kwargs['launch_template_data']['IamInstanceProfile']

        client = boto3.client('iam')
        response = client.get_instance_profile(
            InstanceProfileName=instance_profile_name
        )

        if self.verbose: print(
            'response: {}'.format(response),
            file=sys.stderr
        )

        instance_profile_arn = response['InstanceProfile']['Arn']
        kwargs['launch_template_data'].pop('IamInstanceProfile', None)
        kwargs['launch_template_data']['IamInstanceProfile'] = {}
        kwargs['launch_template_data']['IamInstanceProfile']['Arn'] = instance_profile_arn
        #kwargs['launch_template_data']['IamInstanceProfile']['Name'] = instance_profile_name
        return kwargs['launch_template_data']


    def describe_launch_configuration(self, *args, **kwargs):
        if self.verbose: print(
            'args: {}, kwargs: {}'.format(args, kwargs),
            file=sys.stderr
        )

        client = boto3.client('autoscaling')
        response = client.describe_launch_configurations(
            LaunchConfigurationNames=[kwargs['launch_configuration_name']]
        )

        if self.verbose: print(
            'response: {}'.format(response),
            file=sys.stderr
        )

        return response['LaunchConfigurations'][:1][0]


    def create_launch_template_from_configuration(self, *args, **kwargs):
        if self.verbose: print(
            'args: {}, kwargs: {}'.format(args, kwargs),
            file=sys.stderr
        )

        launch_template_data = self.describe_launch_configuration(
            launch_configuration_name=kwargs['LaunchConfigurationName']
        )

        tag_specifications = kwargs['TagSpecifications']
        launch_template_name = kwargs['LaunchTemplateName']
        description = kwargs['Description']

        client = boto3.client('ec2')
        response = client.create_launch_template(
            LaunchTemplateName=launch_template_name,
            VersionDescription=description,
            LaunchTemplateData=self.filter_launch_configuration(
                launch_template_data=launch_template_data
            ),
            TagSpecifications=tag_specifications
        )

        if self.verbose: print(
            'response: {}'.format(response),
            file=sys.stderr
        )

        return response['LaunchTemplate']


    def delete_launch_template(self, *args, **kwargs):
        if self.verbose: print(
            'args: {}, kwargs: {}'.format(args, kwargs),
            file=sys.stderr
        )

        client = boto3.client('ec2')
        response = client.delete_launch_template(**kwargs)

        if self.verbose: print(
            'response: {}'.format(response),
            file=sys.stderr
        )

        return response['LaunchTemplate']


    def update_auto_scaling_group(self, *args, **kwargs):
        if self.verbose: print(
            'args: {}, kwargs: {}'.format(args, kwargs),
            file=sys.stderr
        )

        auto_scaling_group_name = kwargs['AutoScalingGroupName']
        mixed_instances_policy = kwargs['MixedInstancesPolicy']

##        mixed_instances_policy=$(echo '{
##          "LaunchTemplate": {
##            "LaunchTemplateSpecification": {
##              "LaunchTemplateId": "lt-abcdef1234567890",
##              "Version": "1"
##            },
##            "Overrides": [
##              {
##                "InstanceType": "t3.medium"
##              },
##              {
##                "InstanceType": "t3a.medium"
##              },
##              ...
##            ]
##          },
##          "InstancesDistribution": {
##            "OnDemandBaseCapacity": 1,
##            "OnDemandPercentageAboveBaseCapacity": 50
##          }

        client = boto3.client('autoscaling')
        response = client.update_auto_scaling_group(
            AutoScalingGroupName=auto_scaling_group_name,
            MixedInstancesPolicy=mixed_instances_policy
        )

        if self.verbose: print(
            'response: {}'.format(response),
            file=sys.stderr
        )

        return response