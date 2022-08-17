"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import boto3
import logging
from crhelper import CfnResource
import json


cf = boto3.resource('cloudformation')
sts = boto3.client('sts')
glue = boto3.client('glue')
logger = logging.getLogger(__name__)
helper = CfnResource(
    json_logging=False,
    log_level='DEBUG',
    boto_level='CRITICAL'
)


@helper.create
def create(event, context):
    logger.info(f"Got Create {event}")
    create_or_update(event)
    return "GlueTagger"


@helper.update
def update(event, context):
    logger.info("Got Update")
    create_or_update(event)
    return "GlueTagger"


@helper.delete
def delete(event, context):
    logger.info("Got Delete")


def get_tags_from_stack(stack_id):
    stack = cf.Stack(stack_id)
    tags = stack.tags
    logger.info(f'Tags from stack {tags}')
    return tags


def get_tags_from_props(tags_from_props):
    logger.info(f'Tags from props {tags_from_props}')
    try:
        return(json.loads(tags_from_props))
    except ValueError as e:
        return tags_from_props


def get_tags(tags_from_props, tags_from_stack):
    def prepare_tags_for_tagging(tags):
        return {} if not tags else {tag['Key']: tag['Value'] for tag in tags}
    tags = [
        *tags_from_stack,
        *tags_from_props
    ]
    return prepare_tags_for_tagging(tags)


def get_resource_arns(resource_arns):
    return resource_arns if isinstance(resource_arns, list) else [resource_arns]


def create_or_update(event):
    try:
        stack_id = event['StackId']
        properties = event['ResourceProperties']

        # Get and prepare tags to be added to the resources
        tags_from_props = get_tags_from_props(properties.get('Tags', {}))
        tags_from_stack = get_tags_from_stack(stack_id)
        tags = get_tags(tags_from_props, tags_from_stack)
        if not tags:
            logger.warning('No tags have been provided to the stack nor to the application. Nothing tagged')
            return

        # Get and prepare resource arns to be tagged
        resource_arns = get_resource_arns(properties.get('ResourceArn', []))
        if not resource_arns:
            logger.warning('No ARNs have been provided to the stack. Nothing tagged')
            return

        # Tag resources
        for resource_arn in resource_arns:
            glue.tag_resource(
                ResourceArn=resource_arn,
                TagsToAdd=tags
            )
    except:
        logger.exception('on create error')


def lambda_handler(event, context):
    helper(event, context)
