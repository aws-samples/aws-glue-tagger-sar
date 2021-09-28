"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import boto3
import logging
from crhelper import CfnResource


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


def prepare_tags_before_tagging(tags):
    return {tag['Key']: tag['Value'] for tag in tags}


def get_tags_from_stack(stack_id):
    stack = cf.Stack(stack_id)
    tags = stack.tags
    logger.info(f'Tags from stack {tags}')
    return tags


def get_tags_from_props(tags_from_props):
    tags = [{'Key': parts[0], 'Value': parts[1]} for tag in tags_from_props if (parts := tag.split("="))]
    logger.info(f'Tags from props {tags}')
    return tags


def create_or_update(event):
    try:
        stack_id = event['StackId']
        properties = event['ResourceProperties']
        resource_arns = properties.get('ResourceArn')
        tags_from_props = properties.get('Tags')

        if not resource_arns:
            logger.warning('No ARNs have been provided to the stack. Nothing tagged')
            return

        resource_arns = resource_arns if isinstance(resource_arns, list) else [resource_arns]

        if tags_from_props:
            tags = get_tags_from_props(tags_from_props)
        else:
            tags = get_tags_from_stack(stack_id)

        if not tags:
            logger.warning('No tags have been provided to the stack nor to the application. Nothing tagged')
            return

        tags_to_add = prepare_tags_before_tagging(tags)
        for resource_arn in resource_arns:
            glue.tag_resource(
                ResourceArn=resource_arn,
                TagsToAdd=tags_to_add
            )
    except:
        logger.exception('on create error')


def lambda_handler(event, context):
    helper(event, context)
