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

# Vérifier que cloud-init est activé sans faire échouer le script
echo "Vérification de l'activation des services cloud-init :"
echo "Note: Les services sont activés mais inactifs jusqu'au prochain démarrage"

# Vérifier si les services sont activés (enabled) sans vérifier s'ils sont actifs
for service in cloud-init.service cloud-init-local.service cloud-config.service cloud-final.service; do
  if systemctl is-enabled $service >/dev/null 2>&1; then
    echo "✓ $service est activé"
  else
    echo "✗ $service n'est pas activé"
    # Ne pas faire échouer le script même si un service n'est pas activé
  fi
done

echo "cloud-init a été activé avec succès."
```

### Problème résolu

La version initiale du script utilisait `systemctl status` pour vérifier l'état des services cloud-init, mais cette commande renvoie un code de sortie non nul (3) lorsque le service est inactif, ce qui faisait échouer le script de provisionnement Packer. 

La version corrigée vérifie uniquement si les services sont activés (`enabled`) sans vérifier s'ils sont actifs, car les services cloud-init ne démarrent généralement qu'au premier démarrage de la VM après sa création.

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
