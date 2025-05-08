#!/bin/bash
set -e

echo "Application des configurations spécifiques à Ubuntu..."

echo "Nettoyage du système et configuration DHCP..."

# Configuration de l'interface réseau en DHCP
echo "Configuration de l'interface réseau en DHCP..."
cat > /etc/network/interfaces << EOF
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
allow-hotplug enX0
iface enX0 inet dhcp
EOF


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
