#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
from dotenv import load_dotenv


class S3Client:
    def __init__(self, access_key, secret_key, endpoint_url=None, logger_level=logging.INFO):
        """
        Initialise le client S3
        
        :param access_key: Clé d'accès AWS/S3
        :param secret_key: Clé secrète AWS/S3
        :param endpoint_url: URL de l'endpoint S3 personnalisé (pour les fournisseurs non-AWS)
        :param logger_level: Niveau de journalisation
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url
        
        # Configuration du logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logger_level)
        
        # Ajouter un handler pour afficher les logs dans la console
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.debug(f"{__name__} est initialisé !")
    
    def _get_s3_client(self):
        """
        Crée et retourne un client S3
        
        :return: Client S3 boto3
        """
        # Configuration pour forcer le path style
        s3_config = Config(
            s3={'addressing_style': 'path'}
        )
        
        return boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
            config=s3_config,
            verify=True  # Mettre à False si nécessaire pour les environnements de test
        )
    
    def upload_file(self, local_file, bucket, s3_file, public=False):
        """
        Télécharge un fichier vers S3
        
        :param local_file: Chemin du fichier local à télécharger
        :param bucket: Nom du bucket S3
        :param s3_file: Nom du fichier dans S3
        :param public: Si True, configure le fichier en accès public
        :return: True si le téléchargement réussit, False sinon
        """
        s3_client = self._get_s3_client()
        
        try:
            self.logger.info(f"Téléchargement de {local_file} vers {bucket}/{s3_file}...")
            s3_client.upload_file(local_file, bucket, s3_file)
            
            if public:
                self.logger.info(f"Configuration de l'accès public en lecture pour {s3_file}...")
                s3_client.put_object_acl(
                    Bucket=bucket,
                    Key=s3_file,
                    ACL='public-read'
                )
                
                # Générer et afficher l'URL publique (en path style)
                if self.endpoint_url:
                    public_url = f"{self.endpoint_url}/{bucket}/{s3_file}"
                else:
                    public_url = f"https://s3.amazonaws.com/{bucket}/{s3_file}"
                
                self.logger.info(f"Fichier téléchargé avec succès et configuré en accès public.")
                self.logger.info(f"URL publique: {public_url}")
            else:
                self.logger.info(f"Fichier téléchargé avec succès.")
            
            return True
            
        except FileNotFoundError:
            self.logger.error(f"Le fichier {local_file} n'a pas été trouvé")
            return False
        except NoCredentialsError:
            self.logger.error("Informations d'authentification non disponibles")
            return False
        except ClientError as e:
            self.logger.error(f"Erreur: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur inattendue: {e}")
            return False
    
    def read_file(self, bucket, s3_file):
        """
        Lit un fichier depuis S3
        
        :param bucket: Nom du bucket S3
        :param s3_file: Nom du fichier dans S3
        :return: Contenu du fichier ou None en cas d'erreur
        """
        s3_client = self._get_s3_client()
        
        try:
            self.logger.info(f"Lecture de {bucket}/{s3_file}...")
            s3_object = s3_client.get_object(Bucket=bucket, Key=s3_file)
            
            if 'Body' not in s3_object:
                self.logger.error(f"La clé {s3_file} n'existe pas.")
                return None
                
            s3_object_data = s3_object['Body'].read().decode('utf-8')
            return s3_object_data
            
        except ClientError as e:
            self.logger.error(f"Erreur lors de la lecture du fichier: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur inattendue: {e}")
            return None
    
    def list_objects(self, bucket, prefix=None):
        """
        Liste les objets dans un bucket
        
        :param bucket: Nom du bucket S3
        :param prefix: Préfixe pour filtrer les objets (optionnel)
        :return: Liste des objets ou liste vide en cas d'erreur
        """
        s3_client = self._get_s3_client()
        
        try:
            params = {'Bucket': bucket}
            if prefix:
                params['Prefix'] = prefix
                
            self.logger.info(f"Listage des objets dans {bucket}{f'/{prefix}' if prefix else ''}...")
            response = s3_client.list_objects_v2(**params)
            
            if 'Contents' in response:
                return response['Contents']
            return []
            
        except ClientError as e:
            self.logger.error(f"Erreur lors du listage des objets: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Erreur inattendue: {e}")
            return []

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
    
    # Vérifier que les variables nécessaires sont définies
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Erreur: Les variables suivantes sont manquantes dans le fichier .env: {', '.join(missing_vars)}")
        sys.exit(1)
    
    try:

        # Créer le client S3
        s3_client = S3Client(
            access_key=access_key,
            secret_key=secret_key,
            endpoint_url=endpoint_url,
            logger_level=logging.INFO
        )

        # Télécharger le fichier
        success = s3_client.upload_file(
            local_file=file_path,
            bucket=bucket,
            s3_file=object_name,
            public=True
        )
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
