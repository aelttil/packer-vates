#!/bin/bash
set -e

echo "Configuration SSH..."
# Permettre l'authentification par mot de passe (pour faciliter l'accès initial)
sed -i 's/^#*PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config

# Désactiver la connexion root directe
sed -i 's/^#*PermitRootLogin yes/PermitRootLogin no/g' /etc/ssh/sshd_config

# Configurations de sécurité supplémentaires
sed -i 's/^#*\(MaxAuthTries\) .*/\1 3/' /etc/ssh/sshd_config
sed -i 's/^#*\(ClientAliveInterval\) .*/\1 300/' /etc/ssh/sshd_config
sed -i 's/^#*\(ClientAliveCountMax\) .*/\1 0/' /etc/ssh/sshd_config
sed -i 's/^#*\(PermitEmptyPasswords\) .*/\1 no/' /etc/ssh/sshd_config
sed -i 's/^#*\(X11Forwarding\) .*/\1 no/' /etc/ssh/sshd_config

echo "Configuration SSH terminée."
