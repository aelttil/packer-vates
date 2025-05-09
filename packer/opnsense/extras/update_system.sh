#!/bin/sh
set -e

echo "Mise à jour du système OPNsense..."

# Mise à jour des dépôts
pkg update -f

# Mise à jour des paquets installés
pkg upgrade -y

# Mise à jour du système OPNsense lui-même
# Note: Cette commande peut varier selon la version d'OPNsense
opnsense-update

echo "Mise à jour du système OPNsense terminée."


echo "Installation du plugin net/frr -- The FRRouting Protocol Suite"

pkg install os-frr

echo "Installation des plugin terminé."
