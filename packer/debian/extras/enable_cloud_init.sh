#!/bin/bash
set -e

echo "Activation de cloud-init pour Debian..."

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

echo "cloud-init a été activé avec succès sur Debian."
