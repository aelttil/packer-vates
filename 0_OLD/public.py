#!/usr/bin/env python3
import os
import sys
import json
import tempfile
from dotenv import load_dotenv

import boto3
from botocore.config import Config
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def make_template_metadata_public():
    """Configure l'accès public pour le fichier template-os-metadata.json sur S3"""
    print("Configuration de l'accès public pour template-os-metadata.json...")
    
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
    
    # Nom du fichier global de métadonnées
    global_metadata_key = "template-os-metadata.json"
    
    try:
        # Vérifier si le fichier existe
        try:
            print(f"Vérification de l'existence du fichier {global_metadata_key}...")
            response = s3_client.get_object(Bucket=bucket, Key=global_metadata_key)
            global_metadata = json.loads(response['Body'].read().decode('utf-8'))
            print(f"Fichier existant trouvé: {global_metadata_key}")
            file_exists = True
        except Exception as e:
            print(f"Le fichier n'existe pas ou n'est pas accessible: {e}")
            print("Création d'un nouveau fichier...")
            global_metadata = {}
            file_exists = False
        
        # Si le fichier n'existe pas ou si on veut le mettre à jour
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(global_metadata, temp_file, indent=2)
            temp_file_path = temp_file.name
        
        # Télécharger le fichier avec l'accès public
        print(f"Configuration de l'accès public pour {global_metadata_key}...")
        s3_client.upload_file(
            temp_file_path, 
            bucket, 
            global_metadata_key,
            ExtraArgs={
                'ContentType': 'application/json',
                'ACL': 'public-read'
            }
        )
        
        # Supprimer le fichier temporaire
        os.remove(temp_file_path)
        
        # Vérifier que l'accès public a été configuré
        try:
            acl = s3_client.get_object_acl(Bucket=bucket, Key=global_metadata_key)
            print("ACL configurée:")
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                permission = grant.get('Permission', '')
                if 'URI' in grantee and grantee['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    print(f"  - Accès public: {permission}")
        except Exception as e:
            print(f"Impossible de vérifier l'ACL: {e}")
        
        print(f"\nOpération terminée avec succès!")
        print(f"URL du fichier: {endpoint_url}/{bucket}/{global_metadata_key}")
        
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Charger les variables d'environnement depuis le fichier .env
    load_dotenv()
    
    make_template_metadata_public()
