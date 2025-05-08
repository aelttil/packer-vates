import boto3
from dotenv import load_dotenv
import os
from botocore.config import Config


# Config S3
bucket = "packer-vates"
key = "index.html"
local_file_path = "/Users/alt/Documents/git.ctie.lan/alt/packer-vates/html_templates/index.html"  # Assure-toi que le fichier existe localement

load_dotenv()


# Configuration pour utiliser la signature S3
s3_config = Config(signature_version='s3'  # Utiliser la signature S3
)
    


s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    endpoint_url=os.environ['S3_ENDPOINT_URL'],  # ex: https://s3.fr1.cloud-temple.com
        verify=False,
        config=s3_config
)

# Ré-upload avec les bons headers
with open(local_file_path, 'rb') as f:
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=f,
        ContentType='text/html',
        ContentDisposition='inline',
        ACL='public-read'
    )

print(f"✅ Fichier {key} mis à jour avec Content-Type text/html et disposition inline")