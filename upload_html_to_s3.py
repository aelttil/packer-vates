#!/usr/bin/env python3
import os
import sys
import boto3
from botocore.config import Config
import urllib3
import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def upload_html_to_s3():
    """Télécharge le fichier HTML vers S3 avec les paramètres spécifiés"""
    # Créer un fichier de log
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upload_log.txt")
    with open(log_file, "w") as f:
        f.write(f"{datetime.datetime.now()} - Début du script\n")
        
        # Chemin du fichier HTML
        html_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html_templates", "index.html")
        f.write(f"{datetime.datetime.now()} - Chemin du fichier HTML: {html_file_path}\n")
        
        # Vérifier que le fichier existe
        if not os.path.exists(html_file_path):
            f.write(f"{datetime.datetime.now()} - Erreur: Le fichier HTML n'existe pas: {html_file_path}\n")
            return
        else:
            f.write(f"{datetime.datetime.now()} - Le fichier HTML existe: {html_file_path}\n")
        
        # Récupérer les variables S3 depuis les variables d'environnement
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket = os.environ.get('S3_BUCKET')
        endpoint_url = os.environ.get('S3_ENDPOINT_URL')
        
        f.write(f"{datetime.datetime.now()} - AWS_ACCESS_KEY_ID: {access_key[:4]}...{access_key[-4:] if len(access_key) > 8 else ''}\n")
        f.write(f"{datetime.datetime.now()} - AWS_SECRET_ACCESS_KEY: {secret_key[:4]}...{secret_key[-4:] if len(secret_key) > 8 else ''}\n")
        f.write(f"{datetime.datetime.now()} - S3_BUCKET: {bucket}\n")
        f.write(f"{datetime.datetime.now()} - S3_ENDPOINT_URL: {endpoint_url}\n")
        
        # Configuration pour utiliser la signature S3
        s3_config = Config(
            signature_version='s3'  # Utiliser la signature S3
        )
        
        # Créer une session S3
        try:
            f.write(f"{datetime.datetime.now()} - Création de la session S3...\n")
            s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                endpoint_url=endpoint_url,
                verify=False,
                config=s3_config
            )
            f.write(f"{datetime.datetime.now()} - Session S3 créée avec succès\n")
        except Exception as e:
            f.write(f"{datetime.datetime.now()} - Erreur lors de la création de la session S3: {e}\n")
            return
        
        # Nom de l'objet S3
        key = "index.html"
        
        try:
            # Lire le contenu du fichier HTML
            with open(html_file_path, 'rb') as html_file:
                f.write(f"{datetime.datetime.now()} - Téléchargement du fichier vers S3: {bucket}/{key}\n")
                # Télécharger le fichier vers S3 avec les paramètres spécifiés
                s3_client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=html_file,
                    ContentType='text/html',
                    ContentDisposition='inline',
                    ACL='public-read'
                )
            
            # Générer l'URL publique
            public_url = f"{endpoint_url}/{bucket}/{key}"
            
            f.write(f"{datetime.datetime.now()} - Fichier HTML téléchargé avec succès: {public_url}\n")
            return public_url
        
        except Exception as e:
            f.write(f"{datetime.datetime.now()} - Erreur lors du téléchargement du fichier HTML: {e}\n")
            return

if __name__ == "__main__":
    upload_html_to_s3()
    print("Script terminé. Vérifiez le fichier upload_log.txt pour plus de détails.")
