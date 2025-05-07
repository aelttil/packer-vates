# Client S3 avec support d'accès public

Ce script Python fournit une classe `S3Client` qui permet d'interagir avec des buckets S3, notamment pour télécharger des fichiers et les configurer en accès public (lecture seule sans authentification).

## Prérequis

- Python 3.6 ou supérieur
- Accès à un bucket S3 (AWS ou compatible comme Cloud Temple)
- Clés d'accès avec les permissions nécessaires pour télécharger des fichiers et modifier les ACLs

## Installation

1. Cloner ce dépôt ou télécharger les fichiers
2. Installer les dépendances:

```bash
pip install -r requirements.txt
```

3. Créer un fichier `.env` basé sur `.env.example`:

```bash
cp .env.example .env
```

4. Modifier le fichier `.env` avec vos informations d'authentification et de configuration

## Configuration

Le fichier `.env` doit contenir les variables suivantes:

```
# Informations d'authentification AWS
AWS_ACCESS_KEY_ID=VOTRE_CLE_ACCES
AWS_SECRET_ACCESS_KEY=VOTRE_CLE_SECRETE

# Configuration S3
S3_BUCKET_URL=s3://votre-bucket/prefix
S3_ENDPOINT_URL=https://endpoint-s3.votre-fournisseur.com
```

## Utilisation

### En ligne de commande

```bash
python upload_to_s3.py <chemin_du_fichier> [nom_objet_s3]
```

Exemples:

```bash
# Télécharger un fichier en conservant son nom
python upload_to_s3.py /chemin/vers/mon_fichier.txt

# Télécharger un fichier en spécifiant un nom différent
python upload_to_s3.py /chemin/vers/mon_fichier.txt nouveau_nom.txt
```

### En tant que module dans votre code

```python
from upload_to_s3 import S3Client

# Créer une instance du client S3
s3_client = S3Client(
    access_key="VOTRE_CLE_ACCES",
    secret_key="VOTRE_CLE_SECRETE",
    endpoint_url="https://s3.fr1.cloud-temple.com"
)

# Télécharger un fichier avec accès public
s3_client.upload_file(
    local_file="/chemin/vers/mon_fichier.txt",
    bucket="nom-du-bucket",
    s3_file="dossier/nom_fichier.txt",
    public=True
)

# Lire un fichier depuis S3
content = s3_client.read_file(
    bucket="nom-du-bucket",
    s3_file="dossier/nom_fichier.txt"
)

# Lister les objets dans un bucket
objects = s3_client.list_objects(
    bucket="nom-du-bucket",
    prefix="dossier/"  # Optionnel
)
```

## Fonctionnalités

- **Classe S3Client** avec méthodes pour:
  - Télécharger des fichiers (`upload_file`)
  - Lire des fichiers (`read_file`)
  - Lister les objets dans un bucket (`list_objects`)
- Configuration automatique de l'accès public en lecture
- Support des endpoints S3 personnalisés (compatible avec les fournisseurs non-AWS)
- Utilisation du "path style" pour les URLs S3 (nécessaire pour de nombreux fournisseurs S3 compatibles)
- Gestion des préfixes dans les URLs de bucket
- Système de journalisation intégré
- Gestion robuste des erreurs

## Sécurité

**Attention**: Les fichiers rendus publics sont accessibles à tous sans authentification. Assurez-vous de ne pas exposer de données sensibles.

## Bonnes pratiques

- Utilisez un environnement virtuel Python pour isoler les dépendances
- Ne committez jamais le fichier `.env` contenant vos clés d'accès
- Utilisez des clés d'accès avec les permissions minimales nécessaires
- Considérez l'utilisation de rôles IAM plutôt que des clés d'accès lorsque c'est possible
- Pour les environnements de production, considérez l'activation de la vérification SSL (`verify=True`)
