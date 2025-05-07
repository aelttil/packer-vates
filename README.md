# Script d'upload vers S3

Ce script Python permet de télécharger un fichier vers un bucket S3 compatible avec AWS, comme Cloud Temple.

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
# Informations d'authentification AWS/S3
AWS_ACCESS_KEY_ID=VOTRE_CLE_ACCES
AWS_SECRET_ACCESS_KEY=VOTRE_CLE_SECRETE

# Configuration S3
S3_BUCKET=nom-du-bucket
S3_ENDPOINT_URL=https://s3.fr1.cloud-temple.com
S3_MAKE_PUBLIC=false
```

Variables:
- `AWS_ACCESS_KEY_ID`: Votre clé d'accès S3
- `AWS_SECRET_ACCESS_KEY`: Votre clé secrète S3
- `S3_BUCKET`: Le nom du bucket S3 (sans le préfixe s3://)
- `S3_ENDPOINT_URL`: L'URL de l'endpoint S3 (pour les fournisseurs non-AWS)
- `S3_MAKE_PUBLIC`: Si "true", tente de configurer l'accès public en lecture (nécessite des permissions spécifiques)

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


## Fonctionnalités

- Téléchargement de fichiers vers S3
- Support des endpoints S3 personnalisés (compatible avec les fournisseurs non-AWS)
- Utilisation du "path style" pour les URLs S3 (nécessaire pour Cloud Temple)
- Option pour configurer l'accès public en lecture (si les permissions le permettent)
- Système de journalisation intégré
- Gestion robuste des erreurs

## Sécurité

**Attention**: Les fichiers rendus publics sont accessibles à tous sans authentification. Assurez-vous de ne pas exposer de données sensibles.

## Résolution de problèmes

### Erreur XAmzContentSHA256Mismatch

Si vous rencontrez cette erreur:
```
An error occurred (XAmzContentSHA256Mismatch) when calling the PutObject operation: The Content-SHA256 you specified did not match what we received
```

Le script utilise déjà la signature S3 au lieu de SigV4 pour éviter ce problème avec les fournisseurs S3 compatibles comme Cloud Temple.

### Erreur AccessDenied lors de la configuration de l'accès public

Si vous rencontrez cette erreur:
```
An error occurred (AccessDenied) when calling the PutObjectAcl operation: Access Denied
```

Cela signifie que votre utilisateur n'a pas les permissions nécessaires pour modifier les ACLs des objets. Vous pouvez:
1. Désactiver cette fonctionnalité en mettant `S3_MAKE_PUBLIC=false` dans votre fichier `.env`
2. Demander à l'administrateur du bucket de vous accorder les permissions nécessaires

## Bonnes pratiques

- Utilisez un environnement virtuel Python pour isoler les dépendances
- Ne committez jamais le fichier `.env` contenant vos clés d'accès
- Utilisez des clés d'accès avec les permissions minimales nécessaires
- Pour les environnements de production, considérez l'activation de la vérification SSL (`verify=True`)
