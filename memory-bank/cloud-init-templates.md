# Configuration de Cloud-Init dans les Templates

Ce document détaille la configuration et l'activation de cloud-init dans les templates générés par Packer.

## Problème Identifié

Sur les templates Ubuntu 22.04, Ubuntu 24.04 et Debian 12, cloud-init est installé par défaut mais désactivé. Cela signifie que même si les templates sont marqués comme "cloud-init-ready", les services cloud-init ne démarrent pas automatiquement lors du premier démarrage d'une VM créée à partir de ces templates.

## Solution Implémentée

Un script d'activation de cloud-init a été ajouté au processus de build des templates. Ce script :

1. S'assure que cloud-init est installé
2. Active tous les services cloud-init nécessaires
3. Vérifie que les services sont correctement activés

Des scripts `enable_cloud_init.sh` ont été ajoutés aux répertoires `packer/ubuntu/extras/` et `packer/debian/extras/` et sont exécutés pendant le processus de provisionnement des templates Ubuntu 22.04, Ubuntu 24.04 et Debian 12.

## Contenu du Script

```bash
#!/bin/bash
set -e

echo "Activation de cloud-init..."

# S'assurer que cloud-init est installé
apt-get update
apt-get install -y cloud-init

# Activer les services cloud-init
systemctl enable cloud-init.service
systemctl enable cloud-init-local.service
systemctl enable cloud-config.service
systemctl enable cloud-final.service

# Vérifier que cloud-init est activé
echo "Statut des services cloud-init :"
systemctl status cloud-init.service --no-pager
systemctl status cloud-init-local.service --no-pager
systemctl status cloud-config.service --no-pager
systemctl status cloud-final.service --no-pager

echo "cloud-init a été activé avec succès."
```

## Modifications des Fichiers Packer

Les fichiers de configuration Packer pour Ubuntu 22.04 et 24.04 ont été modifiés pour inclure l'exécution du script `enable_cloud_init.sh` dans le processus de provisionnement :

```hcl
provisioner "shell" {
  inline = [
    "chmod +x /tmp/*.sh",

    # Scripts communs
    "sudo /tmp/update_system.sh",
    "sudo /tmp/harden_ssh.sh",
    "sudo /tmp/harden_system.sh",
    "sudo /tmp/setup_motd.sh",
    
    # Scripts spécifiques à Ubuntu
    "sudo /tmp/ubuntu_specific.sh",
    
    # Activation de cloud-init
    "sudo /tmp/enable_cloud_init.sh",

    # Suppression des scripts
    "rm -f /tmp/*.sh"
  ]
}
```

## Vérification

Après la génération des templates avec ces modifications, les VMs créées à partir de ces templates auront cloud-init correctement activé et configuré pour démarrer automatiquement. Cela permettra :

1. L'application correcte des configurations cloud-init lors du premier démarrage
2. La configuration automatique du réseau, des utilisateurs, etc.
3. L'exécution des scripts personnalisés fournis via cloud-init

## Remarques Importantes

- Les templates générés avant cette modification n'ont pas cloud-init activé par défaut
- Pour les VMs existantes créées à partir d'anciens templates, il est nécessaire d'activer manuellement cloud-init en exécutant les commandes d'activation des services
- La configuration réseau dans les fichiers user-data doit utiliser le nom d'interface correct (`enX0`) pour fonctionner correctement
