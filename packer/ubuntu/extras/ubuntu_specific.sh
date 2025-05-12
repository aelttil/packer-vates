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

sudo rm -f /etc/cloud/cloud.cfg.d/99-installer.cfg
sudo sed -i 's/lock_passwd: True/lock_passwd: False/g' /etc/cloud/cloud.cfg
sudo rm -f /etc/cloud/cloud.cfg.d/subiquity-disable-cloudinit-networking.cfg
sudo bash -c "echo 'disable_vmware_customization: false' >> /etc/cloud/cloud.cfg"
sudo bash -c "echo 'datasource_list: [ NoCloud, VMware, OVF, None ]' > /etc/cloud/cloud.cfg.d/90_dpkg.cfg"
sudo sed -i 's|nocloud-net;seedfrom=http://.*/||' /etc/default/grub
sudo sed -i 's/autoinstall//g' /etc/default/grub
sudo update-grub
sudo cloud-init clean --logs

echo "Configurations spécifiques à Ubuntu terminées."
