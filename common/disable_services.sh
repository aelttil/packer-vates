#!/bin/bash
set -e

echo "Désactivation des services inutiles..."
systemctl disable bluetooth.service || true
systemctl disable avahi-daemon.service || true
systemctl disable cups.service || true
systemctl mask bluetooth.service || true
echo "Désactivation des services inutiles terminée."
