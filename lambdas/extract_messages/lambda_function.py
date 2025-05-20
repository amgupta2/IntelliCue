
import boto3

s3 = boto3.client('s3')

# Define your destination bucket
DESTINATION_BUCKET = 'intellicue-feedback-reports'

def lambda_handler(event, context):
    for record in event['Records']:
        # Source bucket and file key
        source_bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        print(f"🔹 Triggered by s3://{source_bucket}/{object_key}")
        
        # Download the file
        response = s3.get_object(Bucket=source_bucket, Key=object_key)
        content = response['Body'].read()
        
        # Re-upload to destination bucket with the same key or a new one
        # later we add the system that we created to pre process and then use the insights llm 
        destination_key = f"processed/{object_key.split('/')[-1]}"  # change path if needed
        
        s3.put_object(
            Bucket='intellicue-feedback-reports',
            Key=destination_key,
            Body=content,
            ContentType=response.get('ContentType', 'application/octet-stream')
        )
        
        print(f"✅ Copied to s3://{'intellicue-feedback-reports'}/{destination_key}")
        
    return {
        'statusCode': 200,
        'body': 'File copied successfully.'
    }
