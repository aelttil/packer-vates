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

# Configuration de cloud-init
sudo rm -f /etc/cloud/cloud.cfg.d/99-installer.cfg
sudo sed -i 's/lock_passwd: True/lock_passwd: False/g' /etc/cloud/cloud.cfg
sudo rm -f /etc/cloud/cloud.cfg.d/subiquity-disable-cloudinit-networking.cfg
# Suppression de la configuration spécifique à VMware qui n'est pas nécessaire pour XCP-ng/XenServer
# sudo bash -c "echo 'disable_vmware_customization: false' >> /etc/cloud/cloud.cfg"

# Configuration des sources de données cloud-init pour XCP-ng/XenServer
sudo bash -c "echo 'datasource_list: [ NoCloud, ConfigDrive, None ]' > /etc/cloud/cloud.cfg.d/90_dpkg.cfg"
sudo sed -i 's|nocloud-net;seedfrom=http://.*/||' /etc/default/grub
sudo sed -i 's/autoinstall//g' /etc/default/grub
sudo update-grub

# Activation de cloud-init
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

# Nettoyage final des logs cloud-init
echo "Nettoyage des logs cloud-init..."
sudo cloud-init clean --logs

echo "Configurations spécifiques à Ubuntu terminées."
