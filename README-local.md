# Exécution locale du projet

Ce document explique comment exécuter le projet en local, sans utiliser GitHub Actions.

## Prérequis

- Python 3.6 ou supérieur
- Packer installé et accessible dans le PATH
- Accès à un serveur XCP-ng/XenServer
- Accès à un bucket S3 (optionnel, pour le téléchargement des templates)

## Installation

1. Cloner ce dépôt:
   ```bash
   git clone <URL_DU_REPO>
   cd <NOM_DU_REPO>
   ```

2. Installer les dépendances Python:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialiser les plugins Packer:
   ```bash
   cd packer/debian
   packer init debian12.pkr.hcl
   cd ../..
   ```

## Configuration

### Configuration de Packer

Créez un fichier `credentials.pkrvars.hcl` à la racine du projet avec les informations d'accès à votre serveur XCP-ng:

```hcl
remote_host = "10.183.1.131"
remote_username = "root"
remote_password = "votre_mot_de_passe"
sr_iso_name = "ISO"
sr_name = "Local storage"
network_names = ["REKS-LAN"]
```

### Configuration S3 (optionnel)

Pour télécharger les templates vers S3, définissez les variables d'environnement suivantes:

```bash
export AWS_ACCESS_KEY_ID="votre_cle_acces"
export AWS_SECRET_ACCESS_KEY="votre_cle_secrete"
export S3_BUCKET="nom_du_bucket"
export S3_ENDPOINT_URL="https://s3.fr1.cloud-temple.com"
```

## Exécution

Pour construire un template et le télécharger vers S3:

```bash
python3 process_template.py packer/debian/debian12.pkr.hcl credentials.pkrvars.hcl
```

Le script effectuera les opérations suivantes:
1. Détection du système d'exploitation
2. Exécution de Packer
3. Téléchargement du fichier XVA vers S3 (si configuré)
4. Génération et téléchargement des métadonnées

## Exécution sans téléchargement S3

Si vous ne souhaitez pas télécharger les templates vers S3, vous pouvez exécuter Packer directement:

```bash
cd packer/debian
packer build -var-file=../../credentials.pkrvars.hcl debian12.pkr.hcl
```

Le fichier XVA sera généré dans le répertoire de sortie spécifié dans le fichier HCL.

## Détails techniques

### Détection du système d'exploitation

Le script détecte automatiquement le système d'exploitation et sa version en utilisant plusieurs méthodes:

1. Analyse du nom du fichier template (ex: `debian12.pkr.hcl`)
2. Analyse de l'URL ISO dans le fichier HCL
3. Analyse du chemin du fichier template

### Génération des métadonnées

Les métadonnées sont générées à partir des informations suivantes:

1. **Système d'exploitation et version**: Détectés automatiquement
2. **Nom et description de la VM**: Extraits du fichier HCL, avec des valeurs par défaut si non spécifiés
3. **Tags**: Extraits du fichier HCL (`vm_tags`), avec des valeurs par défaut si non spécifiés
4. **URL du fichier XVA**: Générée à partir de l'URL S3 du fichier XVA téléchargé
5. **Date de publication**: Date actuelle au format YYYY-MM-DD

### Noms des fichiers générés

Le script génère plusieurs fichiers:

1. **Fichier XVA**: Généré par Packer dans le répertoire de sortie
2. **Fichier de métadonnées local**: `metadata-{os_type}{os_version}-{timestamp}.json`
3. **Fichier log**: `packer-build-{os_type}{os_version}-{timestamp}.log`

## Dépannage

### Problèmes d'accès à XCP-ng

Si vous rencontrez des problèmes de connexion à XCP-ng:
- Vérifiez que le serveur XCP-ng est accessible depuis votre machine
- Vérifiez que les informations d'authentification sont correctes
- Vérifiez que l'utilisateur a les permissions nécessaires

### Problèmes d'accès S3

Si vous rencontrez des problèmes de téléchargement vers S3:
- Vérifiez que les variables d'environnement sont correctement définies
- Vérifiez que les clés d'accès S3 ont les permissions nécessaires
- Vérifiez que l'endpoint S3 est accessible depuis votre machine
