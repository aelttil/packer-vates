# Stockage sur S3

Ce document explique ce qui est envoyé sur S3 par le script `process_template.py`.

## Structure des fichiers sur S3

Le script organise tous les fichiers liés à un template dans un même dossier sur S3, avec la structure suivante:

```
templates/
└── {os_type}{os_version}/
    └── {timestamp}/
        ├── {os_type}{os_version}.xva
        ├── metadata.json
        └── build.log
```

Par exemple, pour un template Debian 12 construit le 7 mai 2025 à 20:30:54, la structure serait:

```
templates/
└── debian12/
    └── 20250507-203054/
        ├── debian12.xva
        ├── metadata.json
        └── build.log
```

## Fichiers envoyés sur S3

### 1. Fichier XVA

Le fichier XVA est l'image de la machine virtuelle générée par Packer. Il est envoyé sur S3 à l'emplacement:

```
templates/{os_type}{os_version}/{timestamp}/{os_type}{os_version}.xva
```

Par exemple:
```
templates/debian12/20250507-203054/debian12.xva
```

### 2. Fichier de métadonnées

Le fichier JSON de métadonnées contient des informations sur le template, comme le système d'exploitation, la version, les tags, etc. Il est envoyé sur S3 à l'emplacement:

```
templates/{os_type}{os_version}/{timestamp}/metadata.json
```

Par exemple:
```
templates/debian12/20250507-203054/metadata.json
```

Le contenu du fichier de métadonnées ressemble à:

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

### 3. Fichier log

Le fichier log contient la sortie de Packer pendant la construction du template. Il est envoyé sur S3 à l'emplacement:

```
templates/{os_type}{os_version}/{timestamp}/build.log
```

Par exemple:
```
templates/debian12/20250507-203054/build.log
```

## Configuration S3

La configuration de l'accès S3 se fait via le fichier `.env` (ou les secrets GitHub pour la CI/CD), qui doit contenir les variables suivantes:

```
AWS_ACCESS_KEY_ID=votre_cle_acces
AWS_SECRET_ACCESS_KEY=votre_cle_secrete
S3_BUCKET=nom_du_bucket
S3_ENDPOINT_URL=https://s3.fr1.cloud-temple.com
S3_MAKE_PUBLIC=true
```

La variable `S3_MAKE_PUBLIC` est optionnelle et permet de rendre les fichiers publics en lecture. Par défaut, elle est à `false`.

## Vérifications avant l'envoi

Avant d'envoyer les fichiers sur S3, le script effectue les vérifications suivantes:

1. Vérification que les variables d'environnement nécessaires sont définies
2. Vérification que le bucket S3 existe et est accessible
3. Vérification que le fichier à envoyer existe

Si l'une de ces vérifications échoue, le script s'arrête avec un message d'erreur.

## URLs générées

Après l'envoi des fichiers sur S3, le script génère des URLs pour accéder aux fichiers:

```
https://{endpoint_url}/{bucket}/templates/{os_type}{os_version}/{timestamp}/{os_type}{os_version}.xva
https://{endpoint_url}/{bucket}/templates/{os_type}{os_version}/{timestamp}/metadata.json
https://{endpoint_url}/{bucket}/templates/{os_type}{os_version}/{timestamp}/build.log
```

Ces URLs sont affichées dans la console à la fin de l'exécution du script.
