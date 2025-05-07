# Fichiers de métadonnées

Ce document explique les noms et emplacements des fichiers de métadonnées générés par le script `process_template.py`.

## Noms des fichiers de métadonnées

### Fichier local

Le script `process_template.py` génère un fichier de métadonnées localement avec le nom suivant:

```
metadata-{os_type}{os_version}-{timestamp}.json
```

Par exemple:
```
metadata-debian12-20250507-203054.json
```

Ce fichier est créé dans le répertoire courant où le script est exécuté.

### Fichier sur S3

Lorsque le fichier de métadonnées est téléchargé sur S3, il est renommé en `metadata.json` et placé dans le dossier correspondant au build:

```
templates/{os_type}{os_version}/{timestamp}/metadata.json
```

Par exemple:
```
templates/debian12/20250507-203054/metadata.json
```

## Contenu du fichier de métadonnées

Le fichier de métadonnées est au format JSON et contient les informations suivantes:

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

## Fichier d'exemple

Le fichier `metadata-example.json` est un exemple créé pour montrer à quoi ressemble le fichier de métadonnées. Ce n'est pas le nom du fichier généré par le script, mais simplement un exemple pour la documentation.

## Génération des métadonnées

Les métadonnées sont générées à partir des informations suivantes:

1. **Système d'exploitation et version**: Détectés automatiquement à partir du nom du fichier template, de l'URL ISO ou du chemin du fichier.

2. **Nom et description de la VM**: Extraits du fichier HCL, avec des valeurs par défaut si non spécifiés.

3. **Tags**: Extraits du fichier HCL (`vm_tags`), avec des valeurs par défaut si non spécifiés.

4. **URL du fichier XVA**: Générée à partir de l'URL S3 du fichier XVA téléchargé.

5. **Date de publication**: Date actuelle au format YYYY-MM-DD.

## Modification du format des métadonnées

Si vous souhaitez modifier le format des métadonnées, vous pouvez éditer la fonction `generate_metadata` dans le script `process_template.py`. Par exemple, pour ajouter un nouveau champ ou modifier un champ existant.
