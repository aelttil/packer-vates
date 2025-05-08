#!/bin/bash
set -e

echo "Installation des outils Xen Guest Agent pour Ubuntu..."

# Ajout du dépôt officiel
echo "deb [trusted=yes] https://gitlab.com/api/v4/projects/xen-project%252Fxen-guest-agent/packages/generic/deb-amd64/ release/" > /etc/apt/sources.list.d/xen-guest-agent.list

# Mise à jour des dépôts et installation du paquet
apt-get update
apt-get install -y xen-guest-agent

# Vérification que le service est activé et démarré
systemctl enable xen-guest-agent
systemctl start xen-guest-agent

echo "Installation des outils Xen Guest Agent terminée."
