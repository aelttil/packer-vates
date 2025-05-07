#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import datetime
import re
import hcl2
import boto3
from botocore.config import Config
from dotenv import load_dotenv

def run_packer(template_file, var_file, log_file):
    """Exécute Packer et capture la sortie dans un fichier log"""
    print(f"Exécution de Packer avec le template {template_file}...")
    
    cmd = ["packer", "build", "-var-file=" + var_file, template_file]
    
    with open(log_file, 'w') as f:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
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
    
    # Extraction des informations pertinentes du fichier HCL
    try:
        if isinstance(hcl_data, dict):
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
    except Exception as e:
        print(f"Avertissement: Impossible d'extraire les informations de la VM à partir du fichier HCL: {e}")
        print(f"Utilisation des valeurs par défaut")
    
    # Construction du JSON de métadonnées
    metadata = {
        "name": f"{vm_name} Cloud",
        "os": os_type,
        "version": f"{os_version}.0",
        "target_platform": "openiaas",
        "files": [s3_url],
        "description": f"Default password : TOTO {vm_description}, SSH activé, user cloud-init préconfiguré.",
        "logo_url": f"https://assets.symbios/logo-{os_type}.png",
        "publisher": "CLOUDTEMPLE",
        "tags": vm_tags,
        "release_date": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    
    metadata_file = f"metadata-{os_type}{os_version}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Fichier de métadonnées généré: {metadata_file}")
    return metadata_file

def upload_to_s3(file_path, object_name):
    """Télécharge un fichier vers S3 et retourne l'URL"""
    print(f"Téléchargement de {file_path} vers S3...")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Récupérer les variables depuis le fichier .env
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    bucket = os.getenv('S3_BUCKET')
    endpoint_url = os.getenv('S3_ENDPOINT_URL')
    make_public = os.getenv('S3_MAKE_PUBLIC', 'false').lower() == 'true'
    
    # Vérifier que les variables nécessaires sont définies
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Erreur: Les variables suivantes sont manquantes dans le fichier .env: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Configuration pour utiliser la signature S3 au lieu de SigV4
    s3_config = Config(
        signature_version='s3'  # Utiliser la signature S3 au lieu de SigV4
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
    
    try:
        # Vérifier si le bucket existe
        try:
            s3_client.head_bucket(Bucket=bucket)
        except Exception as e:
            print(f"Erreur: Le bucket {bucket} n'existe pas ou n'est pas accessible: {e}")
            sys.exit(1)
        
        # Télécharger le fichier
        s3_client.upload_file(file_path, bucket, object_name)
        
        # Configurer l'accès public en lecture (si demandé)
        if make_public:
            try:
                s3_client.put_object_acl(
                    Bucket=bucket,
                    Key=object_name,
                    ACL='public-read'
                )
            except Exception as e:
                print(f"Avertissement: Impossible de configurer l'accès public: {e}")
                print(f"Le fichier a été téléchargé mais n'est pas accessible publiquement.")
        
        # Générer l'URL publique
        if endpoint_url:
            public_url = f"{endpoint_url}/{bucket}/{object_name}"
        else:
            public_url = f"https://s3.amazonaws.com/{bucket}/{object_name}"
        
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
    
    # Créer un dossier pour ce build
    build_folder = f"templates/{os_type}{os_version}/{timestamp}"
    
    # Étape 4: Télécharger le fichier XVA vers S3
    s3_object_name = f"{build_folder}/{os_type}{os_version}.xva"
    s3_url = upload_to_s3(xva_file, s3_object_name)
    
    # Étape 5: Générer le fichier de métadonnées
    metadata_file = generate_metadata(template_file, hcl_data, xva_file, s3_url)
    
    # Étape 6: Télécharger le fichier de métadonnées vers S3
    metadata_s3_object = f"{build_folder}/metadata.json"
    metadata_url = upload_to_s3(metadata_file, metadata_s3_object)
    
    # Étape 7: Télécharger le fichier log vers S3
    log_s3_object = f"{build_folder}/build.log"
    log_url = upload_to_s3(log_file, log_s3_object)
    
    print("\n=== Processus terminé avec succès ===")
    print(f"Système d'exploitation: {os_type} {os_version}")
    print(f"Fichier XVA: {s3_url}")
    print(f"Métadonnées: {metadata_url}")
    print(f"Log: {log_url}")

if __name__ == "__main__":
    main()
