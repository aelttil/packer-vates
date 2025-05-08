# Technical Context

Ce document décrit le contexte technique du projet d'automatisation de templates Packer, incluant les technologies utilisées, les dépendances, et les contraintes techniques.

## Technologies principales

### Packer

[Packer](https://www.packer.io/) est l'outil central de ce projet, utilisé pour créer des images de machines virtuelles identiques pour plusieurs plateformes à partir d'une seule configuration source.

- **Version**: Dernière version stable recommandée
- **Plugins**: Plugin XenServer/XCP-ng requis
- **Configuration**: Fichiers HCL (HashiCorp Configuration Language)

### XCP-ng/XenServer

[XCP-ng](https://xcp-ng.org/) est une plateforme de virtualisation open source basée sur XenServer.

- **Compatibilité**: XCP-ng 8.2+ / XenServer 7.0+
- **Format d'image**: XVA (Xen Virtual Appliance)
- **Accès**: Nécessite un accès administrateur (root) au serveur XCP-ng

### GitHub Actions

[GitHub Actions](https://github.com/features/actions) est utilisé pour l'automatisation CI/CD du projet.

- **Runner**: Auto-hébergé avec le label `self-hosted`
- **Déclencheurs**: Push sur main, pull requests, manuel
- **Secrets**: Stockage sécurisé des informations d'authentification

### Stockage S3

Un stockage compatible S3 est utilisé pour stocker les templates générés.

- **Compatibilité**: API Amazon S3 standard
- **Authentification**: Clés d'accès et clés secrètes
- **Organisation**: Structure hiérarchique par OS, version et timestamp

## Dépendances

### Dépendances Python

```
boto3==1.26.153
python-dotenv==1.0.0
pyhcl2==0.3.5
```

### Dépendances système

- Python 3.6+
- Packer
- Accès réseau au serveur XCP-ng
- Accès réseau au stockage S3

## Architecture technique

### Flux de travail

1. **Déclenchement**: Via GitHub Actions (automatique ou manuel)
2. **Préparation**: Création des fichiers de configuration
3. **Construction**: Exécution de Packer pour créer le template
4. **Post-traitement**: Détection de l'OS, génération des métadonnées
5. **Déploiement**: Téléchargement vers S3

### Structure des fichiers

```
.
├── packer/
│   ├── common/          # Scripts communs à tous les templates
│   │   ├── cleanup.sh
│   │   ├── harden_ssh.sh
│   │   ├── harden_system.sh
│   │   └── update_system.sh
│   └── debian/          # Templates spécifiques à Debian
│       ├── debian12.pkr.hcl
│       ├── common/
│       │   ├── debian_specific.sh
│       │   └── install_xen_tools.sh
│       └── http/
│           └── preseed.cfg
├── process_template.py  # Script principal d'automatisation
├── .github/workflows/   # Configuration GitHub Actions
│   └── build-template.yml
└── requirements.txt     # Dépendances Python
```

## Contraintes techniques

### Sécurité

- **Secrets**: Stockés dans GitHub Secrets, jamais en clair dans le code
- **Authentification**: Clés d'accès avec privilèges minimaux
- **Vérification SSL**: Désactivée pour certains endpoints S3 (à activer si possible)

### Performance

- **Taille des images**: Les templates peuvent être volumineux (plusieurs GB)
- **Temps de construction**: Variable selon l'OS (10-30 minutes)
- **Bande passante**: Nécessite une bonne connexion pour le téléchargement des ISOs et l'upload des templates

### Compatibilité

- **Versions d'OS**: Principalement Debian/Ubuntu, extensible à d'autres distributions
- **Fournisseurs S3**: Compatible avec AWS S3 et autres fournisseurs compatibles (Cloud Temple, etc.)
- **Environnements**: Fonctionne sur Linux, macOS, Windows avec les dépendances appropriées

## Configuration requise

### Pour le runner GitHub Actions

- **Système d'exploitation**: Linux recommandé
- **RAM**: 4GB minimum
- **Stockage**: 20GB minimum
- **Réseau**: Accès au serveur XCP-ng et au stockage S3
- **Logiciels**: Python 3.6+, Packer, Git

### Pour l'exécution locale

- **Système d'exploitation**: Linux, macOS, Windows
- **RAM**: 2GB minimum
- **Stockage**: 10GB minimum
- **Réseau**: Accès au serveur XCP-ng et au stockage S3
- **Logiciels**: Python 3.6+, Packer, Git
