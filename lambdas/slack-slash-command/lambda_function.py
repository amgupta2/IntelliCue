import json
import boto3
import os
import hmac
import hashlib
import urllib.parse
from datetime import datetime


def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    # Handle missing headers
    headers = event.get('headers') or {}
    body = event.get('body', '')

    # Check if this is a real Slack request
    is_slack_request = (
        'x-slack-signature' in headers or
        'x-slack-request-timestamp' in headers or
        (body and
         ('token=' in body or 'team_id=' in body or 'user_id=' in body))
    )

    # If not a Slack request, return test response
    if not is_slack_request:
        print("Test request detected - returning test response")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'text': 'Test successful - API Gateway and Lambda are working'
            })
        }

    print("Slack request detected - processing normally")

    # Verify Slack signature for real requests
    signing_secret = os.environ.get('SLACK_SIGNING_SECRET', '')
    slack_signature = headers.get('x-slack-signature', '')
    timestamp = headers.get('x-slack-request-timestamp', '')

    if signing_secret and slack_signature and timestamp:
        if not verify_slack_signature(signing_secret, body, timestamp,
                                      slack_signature):
            print("Signature verification failed")
            return {'statusCode': 401, 'body': 'Unauthorized'}
        print("Signature verified successfully")
    else:
        print("Warning: Signature verification skipped")

    # Parse form data
    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({'text': 'Missing request body'})
        }

    body_params = urllib.parse.parse_qs(body)
    print(f"Parsed body: {body_params}")

    # Extract data for all queues
    team_id = body_params.get('team_id', ['unknown'])[0]
    current_timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    # Send to SQS for message extraction
    sqs = boto3.client('sqs')
    message = {
        'channel_id': body_params.get('channel_id', ['unknown'])[0],
        'user_id': body_params.get('user_id', ['unknown'])[0],
        'response_url': body_params.get('response_url', [''])[0],
        'team_id': team_id,
        'timestamp': datetime.utcnow().isoformat()
    }

    try:
        # Send to message extraction queue
        response = sqs.send_message(
            QueueUrl=os.environ['QUEUE_URL'],
            MessageBody=json.dumps(message)
        )
        print(f"Message sent to extraction SQS: {response['MessageId']}")

        # Send to ML processing queue with delay
        ml_queue_url = os.environ.get(
            'ML_QUEUE_URL',
            'https://sqs.us-east-2.amazonaws.com/822218735328/'
            'ml-processing-queue'
        )
        ml_message = {
            'team_id': team_id,
            's3_key': (f'extractions/{team_id}/'
                       f'{current_timestamp}_messages.json'),
            'trigger_source': 'slack_command',
            'extraction_timestamp': current_timestamp,
            'original_request': {
                'channel_id': body_params.get('channel_id', ['unknown'])[0],
                'user_id': body_params.get('user_id', ['unknown'])[0],
                'response_url': body_params.get('response_url', [''])[0]
            }
        }

        ml_response = sqs.send_message(
            QueueUrl=ml_queue_url,
            MessageBody=json.dumps(ml_message),
            DelaySeconds=60
        )
        print(f"ML processing message sent to SQS: "
              f"{ml_response['MessageId']})")

        insights_queue_url = os.environ.get(
            'INSIGHTS_QUEUE_URL',
            'https://sqs.us-east-2.amazonaws.com/822218735328/'
            'insights-processing-queue'
        )
        insights_message = {
            'bucket': 'slack-message-extract',
            'key': (f'preprocessed/{team_id}/'
                    f'{current_timestamp}_preprocessed.json'),
            'team_id': team_id,
            'extraction_timestamp': current_timestamp,
            'trigger_source': 'slack_command'
        }

        insights_response = sqs.send_message(
            QueueUrl=insights_queue_url,
            MessageBody=json.dumps(insights_message),
            DelaySeconds=180
        )
        print(f"Insights processing message sent to SQS: "
              f"{insights_response['MessageId']} (delayed 8 minutes)")

        pdf_queue_url = os.environ.get(
            'PDF_QUEUE_URL',
            'https://sqs.us-east-2.amazonaws.com/822218735328/'
            'pdf-processing-queue'
        )
        pdf_message = {
            'bucket': 'slack-message-extract',
            'key': f'insights/{team_id}/{current_timestamp}_insights.json',
            'team_id': team_id,
            'extraction_timestamp': current_timestamp,
            'trigger_source': 'slack_command'
        }

        pdf_response = sqs.send_message(
            QueueUrl=pdf_queue_url,
            MessageBody=json.dumps(pdf_message),
            DelaySeconds=300
        )
        print(f"PDF processing message sent to SQS: "
              f"{pdf_response['MessageId']} (delayed 12 minutes)")

    except Exception as e:
        print(f"Error sending to SQS: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'text': 'Internal error occurred'})
        }

    response_text = ('🚀 Starting complete pipeline: message extraction → '
                     'ML analysis → executive insights → PDF report '
                     'generation... This will take about 12-15 minutes! '
                     'The complete executive intelligence report will be '
                     'automatically generated.')

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'text': response_text,
            'response_type': 'ephemeral'
        })
    }


def verify_slack_signature(signing_secret, body, timestamp, slack_signature):
    if not all([signing_secret, body, timestamp, slack_signature]):
        return False

    sig_basestring = f'v0:{timestamp}:{body}'
    my_signature = 'v0=' + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, slack_signature)
