import boto3
import os
from slack_sdk import WebClient


def lambda_handler(event, context):
    """
    Simple Lambda function triggered by S3 events to send PDFs to Slack
    """
    # Get Slack token from environment variable
    slack_token = os.environ['SLACK_BOT_TOKEN']
    slack_channel = os.environ['SLACK_CHANNEL_ID']

    # Initialize clients
    s3 = boto3.client('s3')
    slack = WebClient(token=slack_token)

    # Process each S3 event
    for record in event['Records']:
        # Get bucket and file info from S3 event
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        print(f"Processing: {bucket}/{key}")

        # Skip if not a PDF
        if not key.endswith('.pdf'):
            print(f"Skipping non-PDF file: {key}")
            continue

        try:
            # Download file from S3
            response = s3.get_object(Bucket=bucket, Key=key)
            file_content = response['Body'].read()

            # Extract just the filename from the full S3 key
            filename = key.split('/')[-1]

            # Send to Slack
            slack.files_upload_v2(
                channel=slack_channel,
                content=file_content,
                filename=filename,
                title=filename.replace('.pdf', '').replace('_', ' ').title()
            )

            print(f"Successfully sent {filename} to Slack channel")

        except Exception as e:
            print(f"Error processing {key}: {str(e)}")
            raise e

    return {
        'statusCode': 200,
        'body': 'Files processed successfully'
    }
