# Packer Templates Automation

Automatisation de la création et du déploiement de templates Packer pour XCP-ng/XenServer avec GitHub Actions.

## Présentation du projet

Ce projet permet d'automatiser la création de templates de machines virtuelles pour XCP-ng/XenServer en utilisant Packer et GitHub Actions. Le processus comprend:

1. Construction de templates avec Packer
2. Détection automatique du système d'exploitation
3. Génération de métadonnées
4. Téléchargement des templates vers S3
5. Intégration CI/CD avec GitHub Actions

## Structure du projet

- `packer/`: Contient les templates Packer et les scripts de provisionnement
  - `debian/`: Templates pour Debian
  - `common/`: Scripts communs à tous les templates
- `process_template.py`: Script principal d'automatisation
- `.github/workflows/`: Configuration GitHub Actions

## Workflow GitHub Actions

Le workflow GitHub Actions (`build-template.yml`) automatise la construction et le déploiement des templates. Il s'exécute sur un runner auto-hébergé et est configuré pour:

1. S'exécuter automatiquement lors d'un push sur la branche `main` qui modifie des fichiers dans `packer/`
2. S'exécuter automatiquement lors d'une pull request vers la branche `main`
3. Être déclenché manuellement via l'interface GitHub Actions

### Configuration des secrets

Pour utiliser le workflow, configurez les secrets suivants dans votre dépôt GitHub:

| Nom du secret | Description |
|---------------|-------------|
| `REMOTE_HOST` | Adresse IP ou nom d'hôte de votre serveur XCP-ng |
| `REMOTE_PASSWORD` | Mot de passe pour l'utilisateur root de XCP-ng |
| `SR_NAME` | Nom du SR (Storage Repository) de stockage |
| `NETWORK_NAME` | Nom du réseau XCP-ng à utiliser |
| `AWS_ACCESS_KEY_ID` | Clé d'accès pour l'API S3 |
| `AWS_SECRET_ACCESS_KEY` | Clé secrète pour l'API S3 |
| `S3_BUCKET` | Nom du bucket S3 |
| `S3_ENDPOINT_URL` | URL de l'endpoint S3 |

Pour configurer ces secrets:
1. Accédez à votre dépôt GitHub
2. Cliquez sur **Settings** > **Secrets and variables** > **Actions**
3. Cliquez sur **New repository secret**
4. Entrez le nom et la valeur du secret
5. Répétez pour tous les secrets nécessaires

### Configuration du runner auto-hébergé

Le workflow est configuré pour s'exécuter sur un runner auto-hébergé avec le label `self-hosted`. Pour configurer un runner:

1. Dans votre dépôt GitHub, allez dans **Settings > Actions > Runners**
2. Cliquez sur **New self-hosted runner**
3. Suivez les instructions pour installer et configurer le runner
4. Installez les dépendances nécessaires sur le runner:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3 python3-pip packer
   
   # Installer les dépendances Python
   cd /chemin/vers/le/projet
   pip install -r requirements.txt
   
   # Initialiser les plugins Packer
   cd packer/debian
   packer init debian12.pkr.hcl
   cd ../..
   ```

## Fonctionnement du script principal

Le script `process_template.py` gère l'ensemble du processus:

1. Détecte automatiquement le système d'exploitation et sa version
2. Exécute Packer pour construire le template
3. Télécharge le fichier XVA vers S3
4. Génère un fichier JSON de métadonnées
5. Télécharge les métadonnées et les logs vers S3

### Structure des fichiers sur S3

Les fichiers sont organisés sur S3 avec la structure suivante:

```
templates/
└── {os_type}{os_version}/
    └── {timestamp}/
        ├── {os_type}{os_version}.xva
        ├── metadata.json
        └── build.log
```

Par exemple, pour un template Debian 12 construit le 7 mai 2025 à 20:30:54:

```
templates/
└── debian12/
    └── 20250507-203054/
        ├── debian12.xva
        ├── metadata.json
        └── build.log
```

### Format du fichier de métadonnées

Le script génère un fichier JSON de métadonnées avec le format suivant:

```json
{
  "name": "template-debian-12 Cloud",
  "os": "debian",
  "version": "12.0",
  "target_platform": "openiaas",
  "files": [
    "https://s3.fr1.cloud-temple.com/bucket/templates/debian12/20250507-203054/debian12.xva"
  ],
  "description": "Default password : TOTO Template Debian 12, SSH activé, user cloud-init préconfiguré.",
  "logo_url": "https://assets.symbios/logo-debian.png",
  "publisher": "CLOUDTEMPLE",
  "tags": ["debian", "cloud-init", "linux"],
  "release_date": "2025-05-07"
}
```

## Déclenchement du workflow

Le workflow peut être déclenché de trois façons:

1. **Automatiquement** lors d'un push sur la branche `main` qui modifie des fichiers dans le dossier `packer/`
2. **Automatiquement** lors d'une pull request vers la branche `main`
3. **Manuellement** via l'interface GitHub Actions:
   - Allez dans l'onglet "Actions" de votre dépôt GitHub
   - Cliquez sur "Build and Upload Template"
   - Cliquez sur "Run workflow"
   - Sélectionnez la branche sur laquelle vous voulez exécuter le workflow
   - Entrez le nom du template à construire (par défaut: `debian12`)
   - Cliquez sur "Run workflow"

## Ajout d'un nouveau template

Pour ajouter un nouveau template (par exemple Ubuntu 22.04):

1. Créez le fichier template HCL dans `packer/ubuntu/ubuntu22.pkr.hcl`
2. Assurez-vous que le template inclut des `vm_tags` appropriés
3. Exécutez le workflow GitHub Actions manuellement ou via un push

## Dépannage

### Problèmes de détection du système d'exploitation

Si le script ne détecte pas correctement le système d'exploitation:
- Nommez votre fichier template de manière explicite (ex: `debian12.pkr.hcl`)
- Utilisez un chemin explicite (ex: `packer/debian/debian12.pkr.hcl`)
- Assurez-vous que l'URL ISO contient des informations sur la distribution et la version

### Problèmes avec GitHub Actions

Si le workflow GitHub Actions échoue:
- Vérifiez que tous les secrets sont correctement configurés
- Vérifiez que le runner auto-hébergé est en ligne et correctement configuré
- Examinez les logs du workflow pour identifier l'erreur

## Exécution locale

Pour exécuter le projet en local sans utiliser GitHub Actions, consultez le fichier [README-local.md](README-local.md).
