packer {
  required_plugins {
    xenserver= {
     version = "= v0.7.3"
      source = "github.com/ddelnano/xenserver"
   }
  }
}

variable "template_logo_url" {
  type        = string
  description = "URL du logo du template pour les métadonnées"
  default     = "images/default-os.png"  # À remplacer par un logo OPNsense
}

variable "publisher_logo_url" {
  type        = string
  description = "URL du logo du publisher pour les métadonnées"
  default     = "images/cloudtemple.svg"
}

variable "publisher" {
  type        = string
  description = "Nom du owner du template"
  default     = "Cloud Temple"
}

variable "target_platform" {
  type        = string
  description = "Produit cible pour le template. Exemple OpenIaaS ou IaaS VMware"
  default     = "openiaas"
}

variable "remote_host" {
  type        = string
  description = "The ip or fqdn of your XCP-ng. It must be the master"
  sensitive   = true
}

variable "remote_username" {
  type        = string
  description = "The username used to interact with your XCP-ng"
  sensitive   = true
}

variable "remote_password" {
  type        = string
  description = "The password used to interact with your XCP-ng"
  sensitive   = true
}

variable "sr_iso_name" {
  type        = string
  description = "The ISO-SR to packer will use"
  default     = "ISO"
}

variable "sr_name" {
  type        = string
  description = "The name of the SR to packer will use"
  default     = "Local storage"
}

variable "network_names" {
  type        = list(string)
  description = "List of network names to attach to the VM"
}

source "xenserver-iso" "opnsense" {
  iso_checksum      = "e4c178840ab1017bf80097424da76d896ef4183fe10696e92f288d0641475871"
  iso_url           = "https://reks2ee2b1.s3.fr1.cloud-temple.com/packer-vates/ISO/OPNsense-25.1-dvd-amd64.iso"

  sr_iso_name    = var.sr_iso_name
  sr_name        = var.sr_name
  tools_iso_name = ""

  remote_host     = var.remote_host
  remote_password = var.remote_password
  remote_username = var.remote_username

  http_directory = "packer/opnsense/http"
  boot_wait      = "90s"

  # Ces commandes de démarrage sont spécifiques à OPNsense et devront être ajustées
  
  boot_command = [
    "installer<enter><wait>opnsense<enter><wait><wait><wait>",
    "<wait><wait><wait><wait><wait><wait><wait><wait><wait><wait>",
    "<enter><enter><enter>",
    "<down><wait><enter><wait><wait><wait><wait>",
    "<enter><wait><wait><wait><wait>",
    "<left><wait><enter><wait>",
    "<wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait>",
    "<wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait>",
    "<wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait>",
    "<wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait>",
    "<wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait>",
    "<wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait>",
    "<wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait><wait>",
    "<down><wait><enter>"
  ]

  clone_template = "Generic Linux BIOS"
  vm_name        = "template-opnsense-24.1"
  vm_description = "OPNsense 24.1 template. \nDefault login : 'admct'. \nDefault password: 'InitCT@2025'"
  vcpus_max      = 4
  vcpus_atstartup = 2
  vm_memory      = 4096 #MB
  network_names  = var.network_names
  disk_size      = 20480 #MB
  disk_name      = "opnsense-24.1-disk-0"
  vm_tags        = ["Generated by Packer", "OPNsense", "Firewall"]

  ssh_username            = "admct"
  ssh_password            = "InitCT@2025"
  ssh_wait_timeout        = "60000s"
  ssh_handshake_attempts  = 10000

  communicator = "ssh"
  output_directory = "packer-template-opnsense-24.1"
  pause_before_connecting = "60s"

  # Conserver la VM en cas d'échec pour faciliter le débogage
  keep_vm          = "never" #TODO never
  format = "xva_compressed"
}

build {
  sources = ["xenserver-iso.opnsense"]

  provisioner "file" {
    source      = "packer/opnsense/extras/"
    destination = "/tmp/"
  }

  # Exécution des scripts
  provisioner "shell" {
    inline = [
      "chmod +x /tmp/*.sh",

      "sudo /tmp/update_system.sh",
      
      # Suppression des scripts
      "rm -f /tmp/*.sh"
    ]
  }
}
