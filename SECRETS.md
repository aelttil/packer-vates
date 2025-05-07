# Secrets nécessaires pour la CI/CD

Ce document détaille les secrets GitHub nécessaires pour l'exécution du workflow CI/CD.

## Configuration des secrets GitHub

Pour utiliser le workflow GitHub Actions, vous devez configurer les secrets suivants dans votre dépôt GitHub:

### 1. Secrets pour l'accès à XCP-ng

| Nom du secret | Description | Exemple |
|---------------|-------------|---------|
| `REMOTE_HOST` | Adresse IP ou nom d'hôte de votre serveur XCP-ng | `10.183.1.131` |
| `REMOTE_PASSWORD` | Mot de passe pour l'utilisateur root de XCP-ng | `votre_mot_de_passe` |
| `SR_NAME` | Nom du SR (Storage Repository) de stockage | `Local storage` |
| `NETWORK_NAME` | Nom du réseau XCP-ng à utiliser | `REKS-LAN` |

### 2. Secrets pour l'accès S3

| Nom du secret | Description | Exemple |
|---------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | Clé d'accès pour l'API S3 | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Clé secrète pour l'API S3 | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `S3_BUCKET` | Nom du bucket S3 | `templates-bucket` |
| `S3_ENDPOINT_URL` | URL de l'endpoint S3 (pour les fournisseurs non-AWS) | `https://s3.fr1.cloud-temple.com` |

## Comment configurer les secrets GitHub

1. Accédez à votre dépôt GitHub
2. Cliquez sur **Settings** (Paramètres)
3. Dans le menu de gauche, cliquez sur **Secrets and variables** > **Actions**
4. Cliquez sur **New repository secret**
5. Entrez le nom du secret (ex: `REMOTE_HOST`)
6. Entrez la valeur du secret
7. Cliquez sur **Add secret**
8. Répétez pour tous les secrets nécessaires

## Sécurité des secrets

Les secrets GitHub sont:
- Chiffrés avant d'être stockés
- Masqués dans les logs
- Jamais accessibles en clair dans les workflows
- Accessibles uniquement pendant l'exécution du workflow

## Utilisation des secrets dans le workflow

Les secrets sont utilisés dans le workflow pour:
1. Créer le fichier `credentials.pkrvars.hcl` avec les informations d'accès à XCP-ng
2. Créer le fichier `.env` avec les informations d'accès S3

Exemple d'utilisation dans le workflow:

```yaml
- name: Create credentials file
  run: |
    cat > credentials.pkrvars.hcl << EOF
    remote_host = "${{ secrets.REMOTE_HOST }}"
    remote_username = "root"
    remote_password = "${{ secrets.REMOTE_PASSWORD }}"
    sr_iso_name = "ISO"
    sr_name = "${{ secrets.SR_NAME }}"
    network_names = ["${{ secrets.NETWORK_NAME }}"]
    EOF
```

## Vérification des secrets

Pour vérifier que tous les secrets nécessaires sont configurés, vous pouvez exécuter le workflow manuellement via l'interface GitHub Actions. Si des secrets sont manquants, le workflow échouera avec un message d'erreur.
