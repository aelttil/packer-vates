#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import datetime
import re
import tempfile
import hcl2
import boto3
from botocore.config import Config
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def run_packer(template_file, var_file, log_file):
    """Exécute Packer et capture la sortie dans un fichier log"""
    print(f"Exécution de Packer avec le template {template_file}...")
    
    cmd = ["packer", "build", "-debug", "-var-file=" + var_file, template_file]
    
    # Créer une copie de l'environnement actuel et ajouter PACKER_LOG=1
    env = os.environ.copy()
    env["PACKER_LOG"] = "1"
    
    with open(log_file, 'w') as f:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        
        # Capture la sortie en temps réel
        for line in process.stdout:
            sys.stdout.write(line)  # Affiche la sortie en temps réel
            f.write(line)  # Écrit dans le fichier log
        
        process.wait()
        
        if process.returncode != 0:
            print(f"Erreur: Packer a échoué avec le code {process.returncode}")
            sys.exit(1)
    
    print(f"Build Packer terminé, logs écrits dans {log_file}")
    return log_file

def parse_hcl_file(hcl_file):
    """Parse un fichier HCL et retourne un dictionnaire"""
    print(f"Parsing du fichier HCL {hcl_file}...")
    
    with open(hcl_file, 'r') as f:
        content = f.read()
    
    try:
        parsed = hcl2.loads(content)
        return parsed
    except Exception as e:
        print(f"Erreur lors du parsing du fichier HCL: {e}")
        sys.exit(1)

def extract_os_info_from_filename(template_file):
    """Extrait les informations OS du nom du fichier template"""
    filename = os.path.basename(template_file)
    
    # Patterns pour différentes distributions
    debian_pattern = re.compile(r'debian(\d+)')
    ubuntu_pattern = re.compile(r'ubuntu(\d+)')
    centos_pattern = re.compile(r'centos(\d+)')
    
    # Vérifier Debian
    match = debian_pattern.search(filename)
    if match:
        return "debian", match.group(1)
    
    # Vérifier Ubuntu
    match = ubuntu_pattern.search(filename)
    if match:
        return "ubuntu", match.group(1)
    
    # Vérifier CentOS
    match = centos_pattern.search(filename)
    if match:
        return "centos", match.group(1)
    
    # Par défaut
    return "linux", "unknown"

def extract_os_info_from_iso_url(iso_url):
    """Extrait les informations OS de l'URL ISO"""
    # Patterns pour différentes distributions
    debian_pattern = re.compile(r'debian-(\d+\.\d+)')
    ubuntu_pattern = re.compile(r'ubuntu-(\d+\.\d+)')
    
    # Vérifier Debian
    match = debian_pattern.search(iso_url)
    if match:
        version = match.group(1)
        major_version = version.split('.')[0]
        return "debian", major_version
    
    # Vérifier Ubuntu
    match = ubuntu_pattern.search(iso_url)
    if match:
        version = match.group(1)
        major_version = version.split('.')[0]
        return "ubuntu", major_version
    
    # Par défaut
    return "linux", "unknown"

def extract_os_info_from_path(template_file):
    """Extrait les informations OS du chemin du fichier template"""
    path_parts = template_file.split('/')
    
    # Chercher des indices dans le chemin
    for part in path_parts:
        if 'debian' in part.lower():
            # Chercher un numéro de version
            version_match = re.search(r'(\d+)', part)
            if version_match:
                return "debian", version_match.group(1)
            return "debian", "unknown"
        
        if 'ubuntu' in part.lower():
            version_match = re.search(r'(\d+)', part)
            if version_match:
                return "ubuntu", version_match.group(1)
            return "ubuntu", "unknown"
    
    # Par défaut
    return "linux", "unknown"

def determine_os_info(template_file, hcl_data):
    """Détermine les informations OS en utilisant plusieurs méthodes"""
    # Méthode 1: Extraction à partir du nom du fichier
    os_type, os_version = extract_os_info_from_filename(template_file)
    if os_version != "unknown":
        return os_type, os_version
    
    # Méthode 2: Extraction à partir de l'URL ISO
    try:
        if isinstance(hcl_data, dict):
            source_data = hcl_data.get("source", {}).get("xenserver-iso", {})
            for source_name, source_config in source_data.items():
                iso_url = source_config.get("iso_url", "")
                if iso_url:
                    os_type, os_version = extract_os_info_from_iso_url(iso_url)
                    if os_version != "unknown":
                        return os_type, os_version
        elif isinstance(hcl_data, list):
            # Parcourir la liste pour trouver les informations de source
            for item in hcl_data:
                if isinstance(item, dict) and "source" in item:
                    source_data = item.get("source", {})
                    if "xenserver-iso" in source_data:
                        xenserver_data = source_data.get("xenserver-iso", {})
                        for key, value in xenserver_data.items():
                            iso_url = value.get("iso_url", "")
                            if iso_url:
                                os_type, os_version = extract_os_info_from_iso_url(iso_url)
                                if os_version != "unknown":
                                    return os_type, os_version
    except Exception as e:
        print(f"Avertissement: Impossible d'extraire les informations OS à partir de l'URL ISO: {e}")
    
    # Méthode 3: Extraction à partir du chemin
    os_type, os_version = extract_os_info_from_path(template_file)
    if os_version != "unknown":
        return os_type, os_version
    
    # Par défaut
    return "linux", "unknown"

def find_output_file(log_content, output_dir):
    """Trouve le chemin du fichier XVA généré par Packer"""
    print(f"Recherche du fichier de sortie dans {output_dir}...")
    
    # Recherche dans les logs pour trouver des informations sur le fichier de sortie
    # Cette partie peut nécessiter des ajustements selon le format exact des logs de Packer
    
    # Méthode 1: Recherche directe dans le répertoire de sortie
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".xva"):
                return os.path.join(root, file)
    
    # Méthode 2: Extraction à partir des logs
    xva_pattern = re.compile(r'Output: (.*\.xva)')
    match = xva_pattern.search(log_content)
    if match:
        return match.group(1)
    
    print("Erreur: Impossible de trouver le fichier XVA généré")
    sys.exit(1)

def generate_metadata(template_file, hcl_data, xva_file, s3_url):
    """Génère le fichier JSON de métadonnées à partir des données HCL"""
    print("Génération du fichier de métadonnées...")
    
    # Déterminer dynamiquement le système d'exploitation et la version
    os_type, os_version = determine_os_info(template_file, hcl_data)
    
    # Valeurs par défaut
    vm_name = f"{os_type}-{os_version}"
    vm_description = f"{os_type.capitalize()} {os_version} Template"
    vm_tags = [os_type, f"{os_type}{os_version}", "cloud-init"]
    template_logo_url = "NA"  # Valeur par défaut
    publisher_logo_url = "NA"  # Valeur par défaut
    publisher = "Cloud Temple"  # Valeur par défaut
    target_platform = "NA"  # Valeur par défaut
    
    # Extraction des informations pertinentes du fichier HCL
    try:
        if isinstance(hcl_data, dict):
            # Extraire les valeurs des variables
            if "variable" in hcl_data:
                variables = hcl_data["variable"]
                if "template_logo_url" in variables and "default" in variables["template_logo_url"]:
                    template_logo_url = variables["template_logo_url"]["default"]
                if "publisher_logo_url" in variables and "default" in variables["publisher_logo_url"]:
                    publisher_logo_url = variables["publisher_logo_url"]["default"]
                if "publisher" in variables and "default" in variables["publisher"]:
                    publisher = variables["publisher"]["default"]
                if "target_platform" in variables and "default" in variables["target_platform"]:
                    target_platform = variables["target_platform"]["default"]
            
            # Extraire les informations de la VM
            source_data = hcl_data.get("source", {}).get("xenserver-iso", {})
            first_source_key = next(iter(source_data.keys()), None)
            if first_source_key:
                source_config = source_data[first_source_key]
                vm_name = source_config.get("vm_name", vm_name)
                vm_description = source_config.get("vm_description", vm_description)
                if "vm_tags" in source_config:
                    vm_tags = source_config.get("vm_tags")
        elif isinstance(hcl_data, list):
            # Parcourir la liste pour trouver les informations de source
            for item in hcl_data:
                if isinstance(item, dict) and "source" in item:
                    source_data = item.get("source", {})
                    if "xenserver-iso" in source_data:
                        xenserver_data = source_data.get("xenserver-iso", {})
                        for key, value in xenserver_data.items():
                            if "vm_name" in value:
                                vm_name = value.get("vm_name")
                            if "vm_description" in value:
                                vm_description = value.get("vm_description")
                            if "vm_tags" in value:
                                vm_tags = value.get("vm_tags")
                            # Ne plus chercher ces valeurs dans la section source
    except Exception as e:
        print(f"Avertissement: Impossible d'extraire les informations de la VM à partir du fichier HCL: {e}")
        print(f"Utilisation des valeurs par défaut")
    
    # Construction du JSON de métadonnées
    metadata = {
        "name": f"{vm_name} Cloud",
        "os": os_type,
        "version": f"{os_version}.0",
        "target_platform": target_platform,
        "files": [s3_url],
        "description": f"{vm_description}",
        "template_logo_url": template_logo_url,
        "publisher_logo_url": publisher_logo_url,
        "publisher": publisher,
        "tags": vm_tags,
        "release_date": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    
    metadata_file = f"metadata-{os_type}{os_version}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Fichier de métadonnées généré: {metadata_file}")
    return metadata_file

def cleanup_local_files(log_file, metadata_file, output_dir):
    """Nettoie les fichiers locaux après le téléchargement vers S3"""
    print("Nettoyage des fichiers locaux...")
    
    # Supprimer le fichier log
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"Fichier log supprimé: {log_file}")
    
    # Supprimer le fichier de métadonnées
    if os.path.exists(metadata_file):
        os.remove(metadata_file)
        print(f"Fichier de métadonnées supprimé: {metadata_file}")
    
    # Supprimer le répertoire de sortie Packer
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
        print(f"Répertoire de sortie supprimé: {output_dir}")

def upload_to_s3(file_path, object_name, content_type=None, s3_client=None, bucket=None, endpoint_url=None):
    """Télécharge un fichier vers S3 et retourne l'URL"""
    print(f"Téléchargement de {file_path} vers S3...")
    
    # Si les variables S3 ne sont pas passées en paramètres, les récupérer depuis les variables d'environnement
    if s3_client is None or bucket is None or endpoint_url is None:
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket = os.environ.get('S3_BUCKET')
        endpoint_url = os.environ.get('S3_ENDPOINT_URL')
        
        # Afficher les variables pour le débogage
        print("=== INFORMATIONS DE DÉBOGAGE S3 ===")
        print(f"AWS_ACCESS_KEY_ID: {access_key[:4]}...{access_key[-4:] if access_key else 'Non défini'}")
        print(f"AWS_SECRET_ACCESS_KEY: {secret_key[:4]}...{secret_key[-4:] if secret_key else 'Non défini'}")
        print(f"S3_BUCKET: {bucket}")
        print(f"S3_ENDPOINT_URL: {endpoint_url}")
        print(f"Fichier à télécharger: {file_path}")
        print(f"Nom de l'objet S3: {object_name}")
        
        # Vérifier que les variables nécessaires sont définies
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET', 'S3_ENDPOINT_URL']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            print(f"Erreur: Les variables suivantes sont manquantes: {', '.join(missing_vars)}")
            print("Vérifiez que ces variables sont définies dans le fichier .env ou comme variables d'environnement.")
            sys.exit(1)
        
        # Configuration pour utiliser la signature S3
        s3_config = Config(
            signature_version='s3'  # Utiliser la signature S3
        )
        
        # Créer une session S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            verify=False,
            config=s3_config
        )
    else:
        print(f"Utilisation des variables S3 passées en paramètres")
        print(f"Bucket: {bucket}")
        print(f"Endpoint URL: {endpoint_url}")
        print(f"Fichier à télécharger: {file_path}")
        print(f"Nom de l'objet S3: {object_name}")
    
    try:
        # Préparer les arguments supplémentaires
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        # Toujours configurer l'accès public en lecture et la visualisation en ligne
        extra_args['ACL'] = 'public-read'
        extra_args['ContentDisposition'] = 'inline'
        
        # Télécharger le fichier
        print(f"Téléchargement du fichier {file_path} vers {bucket}/{object_name}...")
        s3_client.upload_file(file_path, bucket, object_name, ExtraArgs=extra_args)
        print("Téléchargement réussi.")
        print("Accès public configuré.")
        
        # Générer l'URL publique
        public_url = f"{endpoint_url}/{bucket}/{object_name}"
        
        print(f"Fichier téléchargé avec succès: {public_url}")
        return public_url
    except Exception as e:
        print(f"Erreur lors du téléchargement vers S3: {e}")
        sys.exit(1)

def main():
    """Fonction principale"""
    if len(sys.argv) < 3:
        print("Usage: python process_template.py <template_file> <var_file>")
        sys.exit(1)
    
    template_file = sys.argv[1]
    var_file = sys.argv[2]
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Récupérer les variables S3 depuis les variables d'environnement
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket = os.environ.get('S3_BUCKET')
    endpoint_url = os.environ.get('S3_ENDPOINT_URL')
    
    # Vérifier que les variables nécessaires sont définies
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET', 'S3_ENDPOINT_URL']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Erreur: Les variables suivantes sont manquantes: {', '.join(missing_vars)}")
        print("Vérifiez que ces variables sont définies dans le fichier .env ou comme variables d'environnement.")
        sys.exit(1)
    
    # Configuration pour utiliser la signature S3
    s3_config = Config(
        signature_version='s3'  # Utiliser la signature S3
    )
    
    # Créer une session S3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url,
        verify=False,
        config=s3_config
    )
    
    # Étape 1: Parser le fichier HCL
    hcl_data = parse_hcl_file(template_file)
    
    # Déterminer le système d'exploitation et la version
    os_type, os_version = determine_os_info(template_file, hcl_data)
    print(f"Système d'exploitation détecté: {os_type} {os_version}")
    
    # Étape 2: Exécuter Packer
    log_file = f"packer-build-{os_type}{os_version}-{timestamp}.log"
    run_packer(template_file, var_file, log_file)
    
    # Étape 3: Trouver le fichier XVA généré
    with open(log_file, 'r') as f:
        log_content = f.read()
    
    # Déterminer le répertoire de sortie à partir du fichier HCL
    # Gérer le cas où hcl_data est une liste ou un dictionnaire
    output_dir = f"packer-template-{os_type}-{os_version}"
    
    try:
        if isinstance(hcl_data, dict):
            source_data = hcl_data.get("source", {}).get("xenserver-iso", {})
            first_source_key = next(iter(source_data.keys()), None)
            if first_source_key:
                output_dir = source_data[first_source_key].get("output_directory", output_dir)
        elif isinstance(hcl_data, list):
            # Parcourir la liste pour trouver les informations de source
            for item in hcl_data:
                if isinstance(item, dict) and "source" in item:
                    source_data = item.get("source", {})
                    if "xenserver-iso" in source_data:
                        xenserver_data = source_data.get("xenserver-iso", {})
                        for key, value in xenserver_data.items():
                            if "output_directory" in value:
                                output_dir = value.get("output_directory")
                                break
    except Exception as e:
        print(f"Avertissement: Impossible de déterminer le répertoire de sortie à partir du fichier HCL: {e}")
        print(f"Utilisation du répertoire par défaut: {output_dir}")
    
    xva_file = find_output_file(log_content, output_dir)
    
    # Utiliser le nom de l'OS comme dossier pour ce build
    build_folder = f"{os_type}"
    
    # Étape 4: Télécharger le fichier XVA vers S3
    s3_object_name = f"{build_folder}/{os_type}{os_version}-{timestamp}.xva"
    s3_url = upload_to_s3(xva_file, s3_object_name, s3_client=s3_client, bucket=bucket, endpoint_url=endpoint_url)
    
    # Étape 5: Générer le fichier de métadonnées
    metadata_file = generate_metadata(template_file, hcl_data, xva_file, s3_url)
    
    # Étape 6: Télécharger le fichier de métadonnées vers S3
    metadata_s3_object = f"{build_folder}/{os_type}{os_version}-{timestamp}-metadata.json"
    metadata_url = upload_to_s3(
        metadata_file, 
        metadata_s3_object, 
        content_type='application/json; charset=utf-8', 
        s3_client=s3_client, 
        bucket=bucket, 
        endpoint_url=endpoint_url
    )
    
    # Étape 7: Télécharger le fichier log vers S3
    log_s3_object = f"{build_folder}/{os_type}{os_version}-{timestamp}-build.log"
    log_url = upload_to_s3(
        log_file, 
        log_s3_object, 
        content_type='text/plain; charset=utf-8', 
        s3_client=s3_client, 
        bucket=bucket, 
        endpoint_url=endpoint_url
    )
    
    # Étape 8: Nettoyer les fichiers locaux
    cleanup_local_files(log_file, metadata_file, output_dir)
    
    print("\n=== Processus terminé avec succès ===")
    print(f"Système d'exploitation: {os_type} {os_version}")
    print(f"Fichier XVA: {s3_url}")
    print(f"Métadonnées: {metadata_url}")
    print(f"Log: {log_url}")
    print(f"Les fichiers locaux ont été nettoyés")

if __name__ == "__main__":
    main()
