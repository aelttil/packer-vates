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

# Vérifier que cloud-init est activé
echo "Statut des services cloud-init :"
systemctl status cloud-init.service --no-pager
systemctl status cloud-init-local.service --no-pager
systemctl status cloud-config.service --no-pager
systemctl status cloud-final.service --no-pager

echo "cloud-init a été activé avec succès sur Debian."
