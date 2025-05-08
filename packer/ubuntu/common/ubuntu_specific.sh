#!/bin/bash
set -e

echo "Application des configurations spécifiques à Ubuntu..."

# Configuration d'APT
cat > /etc/apt/apt.conf.d/99custom << EOF
APT::Get::Assume-Yes "true";
APT::Get::AutomaticRemove "true";
Acquire::Languages "none";
EOF

# Installation de paquets spécifiques à Ubuntu
apt-get update
apt-get install -y apt-transport-https ca-certificates

# Configuration des dépôts Ubuntu
# Ubuntu utilise universe/multiverse au lieu de contrib/non-free
add-apt-repository universe -y
add-apt-repository multiverse -y

# Mise à jour après l'ajout des dépôts
apt-get update

echo "Configurations spécifiques à Ubuntu terminées."
