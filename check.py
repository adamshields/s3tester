import boto3
from botocore.client import Config
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3 needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# AWS S3 credentials and endpoint
aws_access_key = 'FOO'
aws_secret_access_key = 'TBAR'
endpoint_url = 'https://s3.amazonaws.com'
bucket_name = 'test'

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=endpoint_url,
    config=Config(signature_version='s3v4'),
    verify=False
)

def check_bucket_exists():
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f'Bucket "{bucket_name}" exists and is accessible.')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_bucket_exists()
