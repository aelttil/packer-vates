#!/bin/bash

# Script pour construire un template Packer et générer les métadonnées

# Vérifier les arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <template_file> [var_file]"
    echo "Example: $0 packer/debian/debian12.pkr.hcl credentials.pkrvars.hcl"
    exit 1
fi

TEMPLATE_FILE=$1
VAR_FILE=${2:-credentials.pkrvars.hcl}

# Vérifier si le fichier template existe
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Erreur: Le fichier template '$TEMPLATE_FILE' n'existe pas."
    exit 1
fi

# Vérifier si le fichier de variables existe
if [ ! -f "$VAR_FILE" ]; then
    echo "Erreur: Le fichier de variables '$VAR_FILE' n'existe pas."
    exit 1
fi

# Vérifier si le script Python existe
if [ ! -f "process_template.py" ]; then
    echo "Erreur: Le script 'process_template.py' n'existe pas."
    exit 1
fi

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    echo "Attention: Le fichier '.env' n'existe pas. Les téléchargements S3 pourraient échouer."
    echo "Voulez-vous créer un fichier .env maintenant? (o/n)"
    read -r response
    if [[ "$response" =~ ^([oO][uU][iI]|[oO])$ ]]; then
        echo "AWS_ACCESS_KEY_ID=" > .env
        echo "AWS_SECRET_ACCESS_KEY=" >> .env
        echo "S3_BUCKET=" >> .env
        echo "S3_ENDPOINT_URL=" >> .env
        echo "Fichier .env créé. Veuillez le modifier avec vos informations d'accès S3."
        exit 1
    fi
fi

# Initialiser Packer
echo "Initialisation de Packer..."
TEMPLATE_DIR=$(dirname "$TEMPLATE_FILE")
TEMPLATE_NAME=$(basename "$TEMPLATE_FILE")
(cd "$TEMPLATE_DIR" && packer init "$TEMPLATE_NAME")

# Exécuter le script Python
echo "Démarrage de la construction du template $TEMPLATE_FILE..."
python3 process_template.py "$TEMPLATE_FILE" "$VAR_FILE"

exit $?
