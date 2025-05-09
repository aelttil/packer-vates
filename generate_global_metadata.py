#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import boto3
import sys
import urllib3
import tempfile
from datetime import datetime
from collections import defaultdict
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

    # Nouvelle structure avec operating_systems comme liste
    result = {"operating_systems": []}
    
    for os_name, builds in grouped.items():
        sorted_builds = sorted(builds, key=lambda x: x[0], reverse=True)
        os_data = {
            "os": os_name,
            "latest": sorted_builds[0][1],
            "history": [build[1] for build in sorted_builds]
        }
        result["operating_systems"].append(os_data)

    return result

def save_global_summary(data, filename="global_summary.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Fichier '{filename}' généré avec succès.")
    return filename

def make_public(local_file_path, s3_key):
    """Configure l'accès public pour un fichier sur S3"""
    print(f"Configuration de l'accès public pour {s3_key}...")
    
    # Récupérer les variables S3 depuis les variables d'environnement
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket = os.environ.get('S3_BUCKET')
    endpoint_url = os.environ.get('S3_ENDPOINT_URL')
    
    # Vérifier que les variables nécessaires sont définies
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET', 'S3_ENDPOINT_URL']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Erreur: Les variables suivantes sont manquantes: {', '.join(missing_vars)}")
        print("Définissez ces variables d'environnement avant d'exécuter le script.")
        sys.exit(1)
    
    # Afficher les informations de connexion (masquées)
    print(f"AWS_ACCESS_KEY_ID: {access_key[:4]}...{access_key[-4:] if access_key else 'Non défini'}")
    print(f"S3_BUCKET: {bucket}")
    print(f"S3_ENDPOINT_URL: {endpoint_url}")
    
    # Configuration pour utiliser la signature S3
    s3_config = Config(
        signature_version='s3'  # Utiliser la signature S3
    )
    
    # Créer une session S3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url,
        verify=False,
        config=s3_config
    )
    
    try:
        # Télécharger le fichier avec l'accès public
        s3_client.upload_file(
            local_file_path, 
            bucket, 
            s3_key,
            ExtraArgs={
                'ContentType': 'application/json',
                'ContentDisposition': 'inline',  # Pour visualisation directe dans le navigateur
                'ACL': 'public-read'
            }
        )
        
        # Vérifier que l'accès public a été configuré
        try:
            acl = s3_client.get_object_acl(Bucket=bucket, Key=s3_key)
            print("ACL configurée:")
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                permission = grant.get('Permission', '')
                if 'URI' in grantee and grantee['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    print(f"  - Accès public: {permission}")
        except Exception as e:
            print(f"Impossible de vérifier l'ACL: {e}")
        
        print(f"URL du fichier: {endpoint_url}/{bucket}/{s3_key}")
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def main():
    print("📦 Récupération des fichiers JSON...")
    json_files = list_json_files(bucket)
    print(f"✔️ {len(json_files)} fichiers metadata trouvés.")

    # Générer et sauvegarder le fichier global_summary.json
    structured_data = generate_full_structure(json_files)
    local_file = save_global_summary(structured_data)
    
    # Télécharger le fichier global_summary.json vers S3
    success = make_public(local_file, "global_summary.json")
    
    if success:
        print("✅ Fichier global_summary.json téléchargé avec succès vers S3")
    else:
        print("❌ Erreur lors du téléchargement du fichier global_summary.json vers S3")
    
    # Supprimer le fichier local après le téléchargement
    if os.path.exists(local_file):
        os.remove(local_file)
        print(f"🗑️ Fichier local {local_file} supprimé")

if __name__ == "__main__":
    main()
