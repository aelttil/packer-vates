#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import boto3
import urllib3
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
from botocore.config import Config

# Désactiver les warnings HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Charger les variables d’environnement
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket = os.getenv('S3_BUCKET')
endpoint_url = os.getenv('S3_ENDPOINT_URL')

# Configurer le client S3
s3 = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    verify=False,
    config=Config(signature_version='s3v4')
)

def list_json_files(bucket_name):
    paginator = s3.get_paginator('list_objects_v2')
    operation_parameters = {'Bucket': bucket_name}
    json_files = []

    for page in paginator.paginate(**operation_parameters):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if key.endswith('-metadata.json'):
                json_files.append(key)
    return json_files

def extract_metadata_from_json(json_str, key_name):
    data = json.loads(json_str)

    os_name = data.get("os")
    version = data.get("version")
    if not os_name or not version:
        raise ValueError("Champ 'os' ou 'version' manquant")

    # Extraire timestamp depuis le nom du fichier
    base = os.path.basename(key_name)
    try:
        parts = base.split("-")
        ts_str = parts[1] + parts[2]  # '20250508' + '124037'
        timestamp = datetime.strptime(ts_str, "%Y%m%d%H%M%S")
    except Exception as e:
        raise ValueError(f"Impossible d'extraire le timestamp depuis {key_name}: {e}")

    return os_name, timestamp, data

def generate_full_structure(json_keys):
    grouped = defaultdict(list)

    for key in json_keys:
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            body = response['Body'].read().decode('utf-8')
            os_name, ts, data = extract_metadata_from_json(body, key)
            grouped[os_name].append((ts, data))
        except Exception as e:
            print(f"⚠️ Erreur sur {key} : {e}")

    result = {}
    for os_name, builds in grouped.items():
        sorted_builds = sorted(builds, key=lambda x: x[0], reverse=True)
        result[os_name] = {
            "latest": sorted_builds[0][1],
            "history": [build[1] for build in sorted_builds]
        }

    return result

def save_global_summary(data, filename="global_summary.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Fichier '{filename}' généré avec succès.")

def main():
    print("📦 Récupération des fichiers JSON...")
    json_files = list_json_files(bucket)
    print(f"✔️ {len(json_files)} fichiers metadata trouvés.")

    structured_data = generate_full_structure(json_files)
    save_global_summary(structured_data)

if __name__ == "__main__":
    main()