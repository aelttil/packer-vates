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
    
    # Réinitialiser le fichier known_hosts pour éviter les erreurs SSH
    print("Réinitialisation du fichier ~/.ssh/known_hosts...")
    try:
        # Utiliser > pour vider le fichier (ou le créer s'il n'existe pas)
        subprocess.run("cat /dev/null > ~/.ssh/known_hosts", shell=True, check=True)
        print("Fichier ~/.ssh/known_hosts réinitialisé avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Avertissement: Impossible de réinitialiser le fichier ~/.ssh/known_hosts: {e}")
    
    cmd = ["packer", "build", "-var-file=" + var_file, template_file]
    
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
    
    # Patterns pour différentes distributions avec version complète
    debian_pattern = re.compile(r'debian(\d+(?:\.\d+)?)')
    ubuntu_pattern = re.compile(r'ubuntu(\d+(?:\.\d+)?)')
    centos_pattern = re.compile(r'centos(\d+(?:\.\d+)?)')
    
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

def extract_output_dir_from_logs(log_content):
    """Extrait le répertoire de sortie directement des logs Packer"""
    # Rechercher des lignes comme "VM files in directory: packer-template-ubuntu-24.04"
    output_dir_pattern = re.compile(r'VM files in directory: ([^\s]+)')
    match = output_dir_pattern.search(log_content)
    if match:
        return match.group(1)
    return None

def find_output_file(log_content, output_dir):
    """Trouve le chemin du fichier XVA généré par Packer"""
    print(f"Recherche du fichier de sortie dans {output_dir}...")
    
    # Méthode 1: Recherche directe dans le répertoire de sortie
    if os.path.exists(output_dir):
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith(".xva"):
                    return os.path.join(root, file)
    
    # Méthode 2: Extraction du répertoire de sortie à partir des logs
    output_dir_from_logs = extract_output_dir_from_logs(log_content)
    if output_dir_from_logs and os.path.exists(output_dir_from_logs):
        print(f"Répertoire de sortie trouvé dans les logs: {output_dir_from_logs}")
        for root, dirs, files in os.walk(output_dir_from_logs):
            for file in files:
                if file.endswith(".xva"):
                    return os.path.join(root, file)
    
    # Méthode 3: Recherche récursive dans le répertoire courant pour les fichiers XVA récents
    print("Recherche récursive des fichiers XVA récents...")
    # Chercher les fichiers XVA créés dans les dernières 30 minutes
    import time
    current_time = time.time()
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(".xva"):
                file_path = os.path.join(root, file)
                file_creation_time = os.path.getctime(file_path)
                if current_time - file_creation_time < 1800:  # 30 minutes en secondes
                    print(f"Fichier XVA récent trouvé: {file_path}")
                    return file_path
    
    # Méthode 4: Extraction à partir des logs
    xva_pattern = re.compile(r'Output: (.*\.xva)')
    match = xva_pattern.search(log_content)
    if match:
        xva_path = match.group(1)
        if os.path.exists(xva_path):
            return xva_path
    
    print("Erreur: Impossible de trouver le fichier XVA généré")
    sys.exit(1)

def extract_vm_description_from_source(hcl_data):
    """Extrait la description de la VM depuis la section source, quelle que soit sa structure"""
    vm_description = None
    
    # Fonction récursive pour parcourir la structure de données
    def search_vm_description(data):
        nonlocal vm_description
        
        if vm_description:  # Si déjà trouvé, ne pas continuer
            return
            
        if isinstance(data, dict):
            # Chercher directement vm_description dans ce dictionnaire
            if "vm_description" in data:
                vm_description = data["vm_description"]
                return
                
            # Sinon, parcourir récursivement toutes les valeurs
            for key, value in data.items():
                search_vm_description(value)
                
        elif isinstance(data, list):
            # Parcourir récursivement tous les éléments de la liste
            for item in data:
                search_vm_description(item)
    
    # Commencer par chercher dans la section "source" si elle existe
    if isinstance(hcl_data, dict) and "source" in hcl_data:
        search_vm_description(hcl_data["source"])
    else:
        # Sinon, chercher dans toute la structure
        search_vm_description(hcl_data)
        
    return vm_description

def generate_metadata(template_file, hcl_data, xva_file, s3_url):
    """Génère le fichier JSON de métadonnées à partir des données HCL"""
    print("Génération du fichier de métadonnées...")
    
    # Débogage: Afficher la structure de hcl_data
    print("Structure de hcl_data:")
    import pprint
    pprint.pprint(hcl_data, depth=2)
    
    # Déterminer dynamiquement le système d'exploitation et la version
    os_type, os_version = determine_os_info(template_file, hcl_data)
    
    # Valeurs par défaut améliorées
    vm_name = f"{os_type}-{os_version}"
    vm_description = f"{os_type.capitalize()} {os_version} Template"
    vm_tags = [os_type, f"{os_type}{os_version}", "cloud-init"]
    template_logo_url = "images/default-os.png"  # Valeur par défaut améliorée
    publisher_logo_url = "images/cloudtemple.svg"  # Valeur par défaut améliorée
    publisher = "Cloud Temple"  # Valeur par défaut
    target_platform = "openiaas"  # Valeur par défaut améliorée
    
    # Extraction de vm_description directement depuis la section source
    extracted_description = extract_vm_description_from_source(hcl_data)
    if extracted_description:
        vm_description = extracted_description
        # Remplacer les caractères d'échappement par des espaces
        vm_description = vm_description.replace("\\n", " ")
        print(f"vm_description extrait: {vm_description}")
    
    # Extraction améliorée des informations du fichier HCL
    try:
        # Extraction des variables
        if isinstance(hcl_data, dict) and "variable" in hcl_data:
            variables = hcl_data["variable"]
            
            # Débogage: Afficher les variables
            print("Variables trouvées:")
            pprint.pprint(variables, depth=2)
            
            # Extraction plus robuste des valeurs
            if "template_logo_url" in variables:
                template_logo_url_var = variables["template_logo_url"]
                if isinstance(template_logo_url_var, dict) and "default" in template_logo_url_var:
                    template_logo_url = template_logo_url_var["default"]
                    print(f"template_logo_url extrait: {template_logo_url}")
            
            if "publisher_logo_url" in variables:
                publisher_logo_url_var = variables["publisher_logo_url"]
                if isinstance(publisher_logo_url_var, dict) and "default" in publisher_logo_url_var:
                    publisher_logo_url = publisher_logo_url_var["default"]
                    print(f"publisher_logo_url extrait: {publisher_logo_url}")
            
            if "publisher" in variables:
                publisher_var = variables["publisher"]
                if isinstance(publisher_var, dict) and "default" in publisher_var:
                    publisher = publisher_var["default"]
                    print(f"publisher extrait: {publisher}")
            
            if "target_platform" in variables:
                target_platform_var = variables["target_platform"]
                if isinstance(target_platform_var, dict) and "default" in target_platform_var:
                    target_platform = target_platform_var["default"]
                    print(f"target_platform extrait: {target_platform}")
        
        # Extraction des informations de la VM
        if isinstance(hcl_data, dict) and "source" in hcl_data:
            sources = hcl_data["source"]
            if "xenserver-iso" in sources:
                xenserver_sources = sources["xenserver-iso"]
                
                # Débogage: Afficher les sources
                print("Sources trouvées:")
                pprint.pprint(xenserver_sources, depth=2)
                
                # Parcourir toutes les sources
                for source_name, source_config in xenserver_sources.items():
                    if "vm_name" in source_config:
                        vm_name = source_config["vm_name"]
                        print(f"vm_name extrait: {vm_name}")
                    
                    if "vm_description" in source_config:
                        vm_description = source_config["vm_description"]
                        print(f"vm_description extrait: {vm_description}")
                    
                    if "vm_tags" in source_config:
                        vm_tags = source_config["vm_tags"]
                        print(f"vm_tags extraits: {vm_tags}")
        
        # Gestion alternative pour les structures de données différentes
        elif isinstance(hcl_data, list):
            print("hcl_data est une liste, parcours des éléments...")
            for item in hcl_data:
                if isinstance(item, dict):
                    # Recherche des variables
                    if "variable" in item:
                        var_item = item["variable"]
                        print(f"Variable trouvée dans la liste: {var_item.keys() if isinstance(var_item, dict) else 'non dict'}")
                        
                        if isinstance(var_item, dict):
                            if "template_logo_url" in var_item and "default" in var_item["template_logo_url"]:
                                template_logo_url = var_item["template_logo_url"]["default"]
                                print(f"template_logo_url extrait de la liste: {template_logo_url}")
                            
                            if "publisher_logo_url" in var_item and "default" in var_item["publisher_logo_url"]:
                                publisher_logo_url = var_item["publisher_logo_url"]["default"]
                                print(f"publisher_logo_url extrait de la liste: {publisher_logo_url}")
                    
                    # Recherche des sources
                    if "source" in item:
                        source_item = item["source"]
                        if "xenserver-iso" in source_item:
                            xenserver_item = source_item["xenserver-iso"]
                            print(f"Source xenserver-iso trouvée dans la liste: {xenserver_item.keys() if isinstance(xenserver_item, dict) else 'non dict'}")
                            
                            if isinstance(xenserver_item, dict):
                                for key, value in xenserver_item.items():
                                    if isinstance(value, dict):
                                        if "vm_name" in value:
                                            vm_name = value["vm_name"]
                                            print(f"vm_name extrait de la liste: {vm_name}")
                                        
                                        if "vm_description" in value:
                                            vm_description = value["vm_description"]
                                            print(f"vm_description extrait de la liste: {vm_description}")
                                        
                                        if "vm_tags" in value:
                                            vm_tags = value["vm_tags"]
                                            print(f"vm_tags extraits de la liste: {vm_tags}")
    except Exception as e:
        print(f"Avertissement: Erreur lors de l'extraction des informations: {e}")
        import traceback
        traceback.print_exc()
    
    # Construction du JSON de métadonnées
    metadata = {
        "name": f"{vm_name}",
        "os": os_type,
        "version": f"{os_version}.0",
        "target_platform": target_platform,
        "files": [s3_url],
        "description": f"{vm_description}",
        "template_logo_url": template_logo_url,
        "publisher_logo_url": publisher_logo_url,
        "publisher": publisher,
        "tags": vm_tags,
        "release_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    # Débogage: Afficher les métadonnées générées
    print("Métadonnées générées:")
    pprint.pprint(metadata)
    
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
