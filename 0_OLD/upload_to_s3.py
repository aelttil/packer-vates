#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
from dotenv import load_dotenv



def main():
    # Configurer le logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('upload_to_s3')
    
    # Charger les variables d'environnement depuis le fichier .env
    load_dotenv()
    
    # Vérifier les arguments
    if len(sys.argv) < 2:
        logger.error("Usage: python upload_to_s3.py <chemin_du_fichier> [nom_objet_s3]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    object_name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(file_path)
    
    # Récupérer les variables depuis le fichier .env
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    bucket = os.getenv('S3_BUCKET')
    endpoint_url = os.getenv('S3_ENDPOINT_URL')
    make_public = os.getenv('S3_MAKE_PUBLIC', 'false').lower() == 'true'
    
    # Vérifier que les variables nécessaires sont définies
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Erreur: Les variables suivantes sont manquantes dans le fichier .env: {', '.join(missing_vars)}")
        sys.exit(1)

    # Configuration pour utiliser la signature S3 au lieu de SigV4
    s3_config = Config(
        signature_version='s3'  # Utiliser la signature S3 au lieu de SigV4
    )
    
    s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            verify=False,
            config=s3_config  # Ajouter la configuration
        )
    

    try:
        response = s3.list_buckets()
        print("Buckets disponibles:")
        for b in response['Buckets']:
            print(f"  - {b['Name']}")
    except Exception as e:
        print(f"Erreur lors de la récupération de la liste des buckets: {e}")
        exit()

    try:

        logger.info(f"Téléchargement de {file_path} vers {bucket}/{object_name}...")
        s3.upload_file(file_path, bucket, object_name)
        logger.info(f"Fichier {file_path} téléchargé avec succès vers {bucket}/{object_name}")
        
        # Configurer l'accès public en lecture (si demandé)
        if make_public:
            try:
                logger.info(f"Configuration de l'accès public en lecture pour {object_name}...")
                s3.put_object_acl(
                    Bucket=bucket,
                    Key=object_name,
                    ACL='public-read'
                )
                
                # Générer et afficher l'URL publique
                public_url = f"{endpoint_url}/{bucket}/{object_name}"

                logger.info(f"Fichier configuré en accès public.")
                logger.info(f"URL publique: {public_url}")
            except Exception as e:
                logger.warning(f"Impossible de configurer l'accès public: {e}")
                logger.info(f"Le fichier a été téléchargé mais n'est pas accessible publiquement.")
        else:
            logger.info(f"Configuration de l'accès public désactivée (S3_MAKE_PUBLIC=false).")
    
    except FileNotFoundError:
        logger.error(f"Le fichier {file_path} n'a pas été trouvé")
        sys.exit(1)
    except NoCredentialsError:
        logger.error("Informations d'authentification non disponibles")
        sys.exit(1)
    except ClientError as e:
        logger.error(f"Erreur: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
