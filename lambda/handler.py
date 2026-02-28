"""
WhatsApp EC2 Control Bot - Lambda Handler

This Lambda function processes WhatsApp messages via Twilio webhook
and controls EC2 instances based on tags.
"""

import json
import os
import hmac
import hashlib
import base64
import boto3
from urllib.parse import parse_qs, urlencode
from botocore.exceptions import ClientError


# Initialize AWS clients
ec2 = boto3.client('ec2')
secrets_manager = boto3.client('secretsmanager')

# Cache for secrets (Lambda container reuse)
_secrets_cache = {}


def get_secrets():
    """Retrieve secrets from AWS Secrets Manager with caching."""
    if _secrets_cache:
        return _secrets_cache

    try:
        response = secrets_manager.get_secret_value(
            SecretId='whatsapp-ec2-control/twilio'
        )
        secrets = json.loads(response['SecretString'])
        _secrets_cache.update(secrets)
        return secrets
    except ClientError as e:
        print(f"Error retrieving secrets: {e}")
        raise


def validate_twilio_signature(request_url, params, signature, auth_token):
    """
    Validate that the request came from Twilio.
    https://www.twilio.com/docs/usage/security#validating-requests
    """
    # Sort parameters and create validation string
    sorted_params = sorted(params.items())
    param_string = ''.join(f"{k}{v}" for k, v in sorted_params)
    validation_string = request_url + param_string

    # Create HMAC-SHA1 signature
    computed_signature = base64.b64encode(
        hmac.new(
            auth_token.encode('utf-8'),
            validation_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('utf-8')

    return hmac.compare_digest(computed_signature, signature)


def is_phone_allowed(phone_number, allowed_numbers):
    """Check if the phone number is in the allowlist."""
    allowed_list = [n.strip() for n in allowed_numbers.split(',')]
    return phone_number in allowed_list


def get_instances_by_tag(tag_key, tag_value):
    """Get EC2 instances matching a specific tag."""
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
                {'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'pending', 'stopping']}
            ]
        )

        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                name = 'Unnamed'
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break

                instances.append({
                    'id': instance['InstanceId'],
                    'name': name,
                    'state': instance['State']['Name'],
                    'type': instance['InstanceType']
                })

        return instances
    except ClientError as e:
        print(f"Error describing instances: {e}")
        return []


def stop_instances_by_tag(tag_key, tag_value):
    """Stop all running instances matching a tag."""
    instances = get_instances_by_tag(tag_key, tag_value)
    running_instances = [i for i in instances if i['state'] == 'running']

    if not running_instances:
        return f"No running instances found with {tag_key}={tag_value}"

    instance_ids = [i['id'] for i in running_instances]

    try:
        ec2.stop_instances(InstanceIds=instance_ids)
        names = ', '.join([i['name'] for i in running_instances])
        return f"Stopping {len(instance_ids)} instance(s): {names}"
    except ClientError as e:
        return f"Error stopping instances: {str(e)}"


def start_instances_by_tag(tag_key, tag_value):
    """Start all stopped instances matching a tag."""
    instances = get_instances_by_tag(tag_key, tag_value)
    stopped_instances = [i for i in instances if i['state'] == 'stopped']

    if not stopped_instances:
        return f"No stopped instances found with {tag_key}={tag_value}"

    instance_ids = [i['id'] for i in stopped_instances]

    try:
        ec2.start_instances(InstanceIds=instance_ids)
        names = ', '.join([i['name'] for i in stopped_instances])
        return f"Starting {len(instance_ids)} instance(s): {names}"
    except ClientError as e:
        return f"Error starting instances: {str(e)}"


def get_status():
    """Get status of all controllable instances."""
    status_lines = []

    # Check Dev environment instances
    dev_instances = get_instances_by_tag('Environment', 'Dev')
    if dev_instances:
        status_lines.append("*Environment=Dev:*")
        for i in dev_instances:
            emoji = "🟢" if i['state'] == 'running' else "🔴"
            status_lines.append(f"  {emoji} {i['name']} ({i['type']}): {i['state']}")

    # Check AutoStop instances
    auto_instances = get_instances_by_tag('AutoStop', 'True')
    if auto_instances:
        status_lines.append("\n*AutoStop=True:*")
        for i in auto_instances:
            emoji = "🟢" if i['state'] == 'running' else "🔴"
            status_lines.append(f"  {emoji} {i['name']} ({i['type']}): {i['state']}")

    if not status_lines:
        return "No controllable instances found. Make sure instances are tagged with Environment=Dev or AutoStop=True"

    return '\n'.join(status_lines)


def get_help():
    """Return help message with available commands."""
    return """*Available Commands:*

*stop dev* - Stop all Dev environment instances
*start dev* - Start all Dev environment instances

*stop auto* - Stop all AutoStop instances
*start auto* - Start all AutoStop instances

*status* - Show all controllable instances

*help* - Show this message"""


def process_command(message):
    """Process the incoming WhatsApp message and return a response."""
    command = message.lower().strip()

    if command == 'help':
        return get_help()

    if command == 'status':
        return get_status()

    if command == 'stop dev':
        return stop_instances_by_tag('Environment', 'Dev')

    if command == 'start dev':
        return start_instances_by_tag('Environment', 'Dev')

    if command == 'stop auto':
        return stop_instances_by_tag('AutoStop', 'True')

    if command == 'start auto':
        return start_instances_by_tag('AutoStop', 'True')

    return f"Unknown command: '{command}'\n\nSend *help* for available commands."


def create_twiml_response(message):
    """Create TwiML response for Twilio."""
    # Escape XML special characters
    escaped_message = (
        message
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{escaped_message}</Message>
</Response>"""


def lambda_handler(event, context):
    """
    Main Lambda handler for WhatsApp webhook.
    """
    print(f"Received event: {json.dumps(event)}")

    try:
        secrets = get_secrets()
    except Exception as e:
        print(f"Failed to get secrets: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal server error'
        }

    # Parse the incoming request
    body = event.get('body', '')
    is_base64 = event.get('isBase64Encoded', False)

    if is_base64:
        body = base64.b64decode(body).decode('utf-8')

    # Parse form data from Twilio
    params = parse_qs(body)
    # Flatten the params (parse_qs returns lists)
    params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

    # Validate Twilio signature (security check)
    headers = event.get('headers', {})
    # Header names might be lowercase in API Gateway
    twilio_signature = headers.get('X-Twilio-Signature') or headers.get('x-twilio-signature', '')

    # Construct the full URL for signature validation
    # You'll need to set this as an environment variable
    webhook_url = os.environ.get('WEBHOOK_URL', '')

    if webhook_url and twilio_signature:
        if not validate_twilio_signature(webhook_url, params, twilio_signature, secrets['TWILIO_AUTH_TOKEN']):
            print("Invalid Twilio signature")
            return {
                'statusCode': 403,
                'body': 'Forbidden'
            }

    # Check if phone number is allowed
    from_number = params.get('From', '')
    allowed_numbers = secrets.get('ALLOWED_PHONE_NUMBERS', '')

    if allowed_numbers and not is_phone_allowed(from_number, allowed_numbers):
        print(f"Unauthorized phone number: {from_number}")
        return {
            'statusCode': 403,
            'headers': {'Content-Type': 'application/xml'},
            'body': create_twiml_response("Sorry, you're not authorized to use this service.")
        }

    # Process the message
    incoming_message = params.get('Body', '')
    print(f"Processing message from {from_number}: {incoming_message}")

    response_message = process_command(incoming_message)
    print(f"Response: {response_message}")

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/xml'
        },
        'body': create_twiml_response(response_message)
    }
