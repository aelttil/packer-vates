#!/bin/bash
set -e

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

# Nettoyage des répertoires temporaires
rm -rf /tmp/*
rm -rf /var/tmp/*

# Réinitialisation de l'ID de machine
echo 'uninitialized' > /etc/machine-id
if [ -f /var/lib/dbus/machine-id ]; then
    rm /var/lib/dbus/machine-id
fi

# Configuration de cloud-init
cloud-init clean --logs || true
sed -i 's/lock_passwd: True/lock_passwd: False/g' /etc/cloud/cloud.cfg || true

# Nettoyage de l'historique du shell
cat /dev/null > ~/.bash_history && history -c || true
history -w || true

# Nettoyage de journald
journalctl --rotate || true
journalctl --vacuum-time=1s || true

echo "Nettoyage du système et configuration DHCP terminés."
