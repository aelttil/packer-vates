#!/usr/bin/env python3
import os
import sys
import boto3
from botocore.config import Config
import urllib3
import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def upload_file_to_s3(s3_client, local_file, bucket, key, content_type):
    """Télécharge un fichier vers S3"""
    try:
        with open(local_file, 'rb') as file_data:
            print(f"{datetime.datetime.now()} - Téléchargement du fichier vers S3: {bucket}/{key}")
            
            s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=file_data,
                ContentType=content_type,
                ContentDisposition='inline',
                ACL='public-read'
            )
        return True
    except Exception as e:
        print(f"{datetime.datetime.now()} - Erreur lors du téléchargement du fichier {local_file}: {e}")
        return False

def upload_html_to_s3():
    """Télécharge le fichier HTML vers S3 avec les paramètres spécifiés"""
    print(f"{datetime.datetime.now()} - Début du script")
    
    # Chemin du fichier HTML
    html_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html_templates", "index.html")
    print(f"{datetime.datetime.now()} - Chemin du fichier HTML: {html_file_path}")
    
    # Vérifier que le fichier existe
    if not os.path.exists(html_file_path):
        print(f"{datetime.datetime.now()} - Erreur: Le fichier HTML n'existe pas: {html_file_path}")
        return
    else:
        print(f"{datetime.datetime.now()} - Le fichier HTML existe: {html_file_path}")
    
    # Récupérer les variables S3 depuis les variables d'environnement
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket = os.environ.get('S3_BUCKET')
    endpoint_url = os.environ.get('S3_ENDPOINT_URL')
    
    # Pour les tests, si les variables ne sont pas définies, utiliser des valeurs par défaut
    if not access_key:
        print(f"{datetime.datetime.now()} - Variable AWS_ACCESS_KEY_ID non définie, utilisation d'une valeur par défaut pour les tests")
        access_key = "test_access_key"
    
    if not secret_key:
        print(f"{datetime.datetime.now()} - Variable AWS_SECRET_ACCESS_KEY non définie, utilisation d'une valeur par défaut pour les tests")
        secret_key = "test_secret_key"
    
    if not bucket:
        print(f"{datetime.datetime.now()} - Variable S3_BUCKET non définie, utilisation d'une valeur par défaut pour les tests")
        bucket = "packer-vates"
    
    if not endpoint_url:
        print(f"{datetime.datetime.now()} - Variable S3_ENDPOINT_URL non définie, utilisation d'une valeur par défaut pour les tests")
        endpoint_url = "https://reks2ee2b1.s3.fr1.cloud-temple.com"
    
    print(f"{datetime.datetime.now()} - AWS_ACCESS_KEY_ID: {access_key[:4]}...{access_key[-4:] if len(access_key) > 8 else ''}")
    print(f"{datetime.datetime.now()} - AWS_SECRET_ACCESS_KEY: {secret_key[:4]}...{secret_key[-4:] if len(secret_key) > 8 else ''}")
    print(f"{datetime.datetime.now()} - S3_BUCKET: {bucket}")
    print(f"{datetime.datetime.now()} - S3_ENDPOINT_URL: {endpoint_url}")
    
    # Configuration pour utiliser la signature S3
    s3_config = Config(
        signature_version='s3'  # Utiliser la signature S3
    )
    
    # Créer une session S3
    try:
        print(f"{datetime.datetime.now()} - Création de la session S3...")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            verify=False,
            config=s3_config
        )
        print(f"{datetime.datetime.now()} - Session S3 créée avec succès")
    except Exception as e:
        print(f"{datetime.datetime.now()} - Erreur lors de la création de la session S3: {e}")
        return
    
    # Nom de l'objet S3
    key = "index.html"
    
    # Télécharger le fichier HTML principal
    success = upload_file_to_s3(
        s3_client, 
        html_file_path, 
        bucket, 
        key, 
        'text/html'
    )
    
    if not success:
        print(f"{datetime.datetime.now()} - Erreur lors du téléchargement du fichier HTML principal")
        return
    
    # Générer l'URL publique
    public_url = f"{endpoint_url}/{bucket}/{key}"
    print(f"{datetime.datetime.now()} - Fichier HTML téléchargé avec succès: {public_url}")
    
    # Télécharger les fichiers d'images par défaut
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html_templates", "images")
    if os.path.exists(images_dir):
        print(f"{datetime.datetime.now()} - Téléchargement des fichiers d'images par défaut depuis: {images_dir}")
        
        # Télécharger les fichiers HTML par défaut
        for filename in os.listdir(images_dir):
            if filename.endswith('.html'):
                local_file = os.path.join(images_dir, filename)
                s3_key = f"images/{filename}"
                
                success = upload_file_to_s3(
                    s3_client, 
                    local_file, 
                    bucket, 
                    s3_key, 
                    'text/html'
                )
                
                if success:
                    print(f"{datetime.datetime.now()} - Image HTML par défaut téléchargée avec succès: {s3_key}")
                else:
                    print(f"{datetime.datetime.now()} - Erreur lors du téléchargement de l'image HTML par défaut: {s3_key}")
        
        # Télécharger les images spécifiques
        specific_images = [
            ('debian.png', 'image/png'),
            ('logo-cloudtemple-footer.svg', 'image/svg+xml')
        ]
        
        for filename, content_type in specific_images:
            local_file = os.path.join(images_dir, filename)
            if os.path.exists(local_file):
                s3_key = f"images/{filename}"
                
                success = upload_file_to_s3(
                    s3_client,
                    local_file,
                    bucket,
                    s3_key,
                    content_type
                )
                
                if success:
                    print(f"{datetime.datetime.now()} - Image spécifique téléchargée avec succès: {s3_key}")
                else:
                    print(f"{datetime.datetime.now()} - Erreur lors du téléchargement de l'image spécifique: {s3_key}")
            else:
                print(f"{datetime.datetime.now()} - Image spécifique non trouvée: {local_file}")
    else:
        print(f"{datetime.datetime.now()} - Répertoire d'images par défaut non trouvé: {images_dir}")
    
    print(f"{datetime.datetime.now()} - Script terminé avec succès")
    return public_url

if __name__ == "__main__":
    upload_html_to_s3()
