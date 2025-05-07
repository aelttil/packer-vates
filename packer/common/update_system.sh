#!/bin/bash
set -e

echo "Mise à jour du système..."
apt-get update
apt-get -y dist-upgrade
apt-get -y --purge autoremove
apt-get -y clean
echo "Mise à jour du système terminée."
