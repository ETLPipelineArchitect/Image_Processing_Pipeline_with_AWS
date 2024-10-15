import json
import boto3
import re


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    rekognition = boto3.client('rekognition')
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # Extract metadata
        response = s3.head_object(Bucket=bucket, Key=key)
        metadata = response.get('Metadata', {})
        
        # Use Rekognition to detect labels
        rekog_response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10
        )
        labels = [label['Name'] for label in rekog_response['Labels']]
        
        # Clean and format metadata using regex
        creator = metadata.get('creator', 'unknown')
        creator = re.sub(r'[^A-Za-z0-9 ]+', '', creator)
        
        # Prepare metadata record
        metadata_record = {
            'image_key': key,
            'creator': creator,
            'labels': labels
        }
        
        # Save metadata to S3
        metadata_bucket = 'your-bucket'
        metadata_key = f'metadata/{key.split('/')[-1].split('.')[0]}.json'
        s3.put_object(
            Bucket=metadata_bucket,
            Key=metadata_key,
            Body=json.dumps(metadata_record)
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Metadata extraction complete.')
    }
