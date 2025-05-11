#!/bin/bash
# setup_motd.sh - Configure un MOTD personnalisé pour Cloud Temple
# À placer dans packer/common/

# Récupérer la date de build (sera remplacée par la date réelle lors de l'exécution)
BUILD_DATE=$(date +"%Y-%m-%d")

# Créer le fichier de couleurs
mkdir -p /etc/update-motd.d
cat > /etc/update-motd.d/colors << 'EOF'
#!/bin/bash
# Couleurs de base
NONE="\033[0m"
BOLD="\033[1m"
UNDERLINE="\033[4m"
BLINK="\033[5m"

# Couleurs normales
BLACK="\033[0;30m"
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
MAGENTA="\033[0;35m"
CYAN="\033[0;36m"
WHITE="\033[0;37m"

# Couleurs claires
LIGHT_BLACK="\033[1;30m"
LIGHT_RED="\033[1;31m"
LIGHT_GREEN="\033[1;32m"
LIGHT_YELLOW="\033[1;33m"
LIGHT_BLUE="\033[1;34m"
LIGHT_MAGENTA="\033[1;35m"
LIGHT_CYAN="\033[1;36m"
LIGHT_WHITE="\033[1;37m"

# Couleurs de fond
BG_BLACK="\033[40m"
BG_RED="\033[41m"
BG_GREEN="\033[42m"
BG_YELLOW="\033[43m"
BG_BLUE="\033[44m"
BG_MAGENTA="\033[45m"
BG_CYAN="\033[46m"
BG_WHITE="\033[47m"
EOF
chmod +x /etc/update-motd.d/colors

# Créer le script MOTD principal
cat > /etc/update-motd.d/10-cloud-temple << 'EOF'
#!/bin/bash

# Appel du fichier avec les variables de couleurs
. /etc/update-motd.d/colors

# Récupération des informations à afficher
# Informations sur le système
hostname=$(hostname)
os=$(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)
kernel=$(uname -r)
arch=$(uname -m)
shell=$SHELL
user=$(whoami)

# Récupération des infos sur le processeur
proc=$(cat /proc/cpuinfo | grep "model name" | head -n 1 | cut -d: -f2)
# Supprime les espaces dans Avant/Après
proc=$(echo "${proc}" | sed 's/^ *//g')
# Récupère le nombre de coeurs
coeurs=$(cat /proc/cpuinfo | grep -i "^processor" | wc -l)

# Récupère la mémoire RAM SWAP Libre et Total
memfree=$(cat /proc/meminfo | grep MemFree | awk {'print $2'})
memtotal=$(cat /proc/meminfo | grep MemTotal | awk {'print $2'})
swaptotal=$(cat /proc/meminfo | grep SwapTotal | awk {'print $2 " " $3'})
pourcentfree=$((($memfree * 100)/$memtotal))

# Récupère l'uptime du serveur
uptime=$(uptime -p)

# Récupère l'adresse IP du serveur
addrip=$(hostname -I | awk '{print $1}')

# Récupère le nombre de processus en exécution
process=$(ps ax | wc -l | tr -d " ")

# Récupère le nombre d'utilisateur connecté en SSH/Console
connecteduser=$(who | wc -l)

# Récupére l'utilisation des disques
diskused=$(df -h / | awk 'NR==2 {print $5 " of " $2}')

# Récupère les inodes utilisés
inodeused=$(df -i / | awk 'NR==2 {print $5}')

# Récupére le loadavg
read one five fifteen rest < /proc/loadavg

# Date de build (sera remplacée lors de l'installation)
build_date="BUILD_DATE_PLACEHOLDER"

# Affichage du header
printf "${LIGHT_BLUE}${BOLD}"
printf "  === CLOUD TEMPLE ===\n"
printf "${NONE}"
# Utiliser une variable pour le texte avec emoji pour éviter les problèmes d'échappement
welcome_text="Welcome to your Linux server 🚀"
printf "${LIGHT_YELLOW}  %s${NONE}\n\n" "$welcome_text"

# Affichage des informations système
printf "${LIGHT_CYAN}  System Information:${NONE}\n"
printf "${LIGHT_GREEN}  ▸ Hostname    :${NONE} $hostname\n"
printf "${LIGHT_GREEN}  ▸ User        :${NONE} $user\n"
printf "${LIGHT_GREEN}  ▸ OS          :${NONE} $os\n"
printf "${LIGHT_GREEN}  ▸ Kernel      :${NONE} $kernel\n"
printf "${LIGHT_GREEN}  ▸ Architecture:${NONE} $arch\n"
printf "${LIGHT_GREEN}  ▸ Shell       :${NONE} $shell\n"
printf "${LIGHT_GREEN}  ▸ Build Date  :${NONE} $build_date\n"

# Affichage des informations matérielles
printf "\n${LIGHT_CYAN}  Hardware Information:${NONE}\n"
printf "${LIGHT_GREEN}  ▸ Processor   :${NONE} $proc ($coeurs cores)\n"
printf "${LIGHT_GREEN}  ▸ CPU Load    :${NONE} $one (1min) / $five (5min) / $fifteen (15min)\n"
# Stocker le texte formaté dans une variable pour éviter les problèmes d'échappement
mem_text="$(($memfree/1024)) MB free ($pourcentfree%) / $(($memtotal/1024)) MB total"
printf "${LIGHT_GREEN}  ▸ Memory      :${NONE} %s\n" "$mem_text"
printf "${LIGHT_GREEN}  ▸ Swap        :${NONE} $swaptotal\n"

# Affichage des informations système
printf "\n${LIGHT_CYAN}  Usage Information:${NONE}\n"
printf "${LIGHT_GREEN}  ▸ Processes   :${NONE} $process\n"
printf "${LIGHT_GREEN}  ▸ Users logged :${NONE} $connecteduser\n"
# Stocker le texte formaté dans une variable pour éviter les problèmes d'échappement
disk_text="$diskused"
printf "${LIGHT_GREEN}  ▸ Disk Usage  :${NONE} %s\n" "$disk_text"
# Stocker le texte formaté dans une variable pour éviter les problèmes d'échappement
inode_text="$inodeused"
printf "${LIGHT_GREEN}  ▸ Inodes Used :${NONE} %s\n" "$inode_text"
printf "${LIGHT_GREEN}  ▸ IP Address  :${LIGHT_RED} $addrip${NONE}\n"
printf "${LIGHT_GREEN}  ▸ Uptime      :${NONE} $uptime\n"

# Affichage du footer
# Utiliser des variables pour le texte avec caractères spéciaux pour éviter les problèmes d'échappement
footer_text1="Deployed with ♥ by Cloud Temple – Innovation by Design"
footer_text2="Generated from a Cloud Temple automated template"
printf "\n${LIGHT_BLUE}  ▸ %s${NONE}\n" "$footer_text1"
printf "${LIGHT_BLUE}  ▸ %s${NONE}\n\n" "$footer_text2"
EOF
chmod +x /etc/update-motd.d/10-cloud-temple

# Remplacer le placeholder par la date de build réelle
sed -i "s/BUILD_DATE_PLACEHOLDER/$BUILD_DATE/g" /etc/update-motd.d/10-cloud-temple

# Configurer le système pour afficher le MOTD à chaque connexion
if [ -d /etc/update-motd.d ]; then
    # Pour les systèmes basés sur Ubuntu qui utilisent update-motd.d
    # Désactiver les scripts MOTD par défaut
    chmod -x /etc/update-motd.d/00-header 2>/dev/null || true
    chmod -x /etc/update-motd.d/10-help-text 2>/dev/null || true
    chmod -x /etc/update-motd.d/50-motd-news 2>/dev/null || true
    chmod -x /etc/update-motd.d/80-livepatch 2>/dev/null || true
    chmod -x /etc/update-motd.d/90-updates-available 2>/dev/null || true
    chmod -x /etc/update-motd.d/91-release-upgrade 2>/dev/null || true
    chmod -x /etc/update-motd.d/95-hwe-eol 2>/dev/null || true
    chmod -x /etc/update-motd.d/98-fsck-at-reboot 2>/dev/null || true
    chmod -x /etc/update-motd.d/98-reboot-required 2>/dev/null || true
else
    # Pour les systèmes qui utilisent directement /etc/motd
    # Créer un lien symbolique pour exécuter notre script au login
    ln -sf /etc/update-motd.d/10-cloud-temple /etc/profile.d/motd.sh
    
    # Vider le fichier /etc/motd pour éviter l'affichage en double
    echo "" > /etc/motd
fi

# Supprimer les autres fichiers MOTD qui pourraient interférer
[ -f /etc/motd.dynamic ] && rm /etc/motd.dynamic
[ -f /etc/motd.tail ] && rm /etc/motd.tail

echo "MOTD Cloud Temple configuré avec succès."
