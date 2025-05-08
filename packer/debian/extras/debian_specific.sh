#!/bin/bash
set -e

echo "Application des configurations spécifiques à Debian..."

# Configuration d'APT
cat > /etc/apt/apt.conf.d/99custom << EOF
APT::Get::Assume-Yes "true";
APT::Get::AutomaticRemove "true";
Acquire::Languages "none";
EOF

# Installation de paquets spécifiques à Debian
apt-get update
apt-get install -y apt-transport-https ca-certificates

# Configuration de sources.list pour inclure non-free et contrib
sed -i 's/main$/main contrib non-free/g' /etc/apt/sources.list

echo "Configurations spécifiques à Debian terminées."
