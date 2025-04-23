import os
import json
import boto3


def create_s3_client(access_key=None, secret_key=None):
    access_key = access_key or os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = secret_key or os.getenv('AWS_SECRET_ACCESS_KEY')

    if access_key and secret_key:
        return boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
    else:
        print('AWS credentials not found')
        return boto3.client('s3')


def save_to_s3(data, s3_uri, s3_client=None):
    if not s3_client:
        s3_client = create_s3_client()

    if not s3_uri.startswith('s3://'):
        raise ValueError("S3 uri must be correct format: s3://bucket/key")

    bucket_name, key = s3_uri[5:].split('/', 1)
    
    if key.endswith('.json'):
        data = json.dumps(data, indent=4).encode('utf-8')
    
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)


def save_to_file(data, file_path):
    
    if file_path.endswith('.json'):
        data = json.dumps(data, indent=4).encode('utf-8')

    with open(file_path, 'wb') as file:
        file.write(data)
