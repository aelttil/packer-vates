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
  default     = "images/ubuntu.png"
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
  description = "Produit cible pour le template. Exemple OpenIaaS ou IaaS VMware."
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


source "xenserver-iso" "ubuntu24" {
  iso_checksum      = "d6dab0c3a657988501b4bd76f1297c053df710e06e0c3aece60dead24f270b4d"
  iso_url           = "https://reks2ee2b1.s3.fr1.cloud-temple.com/packer-vates/ISO/ubuntu-24.04.2-live-server-amd64.iso"

  sr_iso_name    = var.sr_iso_name
  sr_name        = var.sr_name
  tools_iso_name = ""

  remote_host     = var.remote_host
  remote_password = var.remote_password
  remote_username = var.remote_username

  http_directory = "packer/ubuntu/http"
  boot_wait      = "5s"

  boot_command = ["<spacebar><wait><spacebar><wait><spacebar><wait><spacebar><wait><spacebar><wait>",
    "e<wait>",
    "<down><down><down><end><wait>",
    "<bs><bs><bs>",
    " autoinstall ds=\"nocloud;seedfrom=http://10.0.0.143:{{ .HTTPPort }}/\"",
    "<enter><wait>",
    "<f10>"
    ]

  clone_template = "Generic Linux BIOS"
  vm_name        = "template-ubuntu-24.04"
  vm_description = "Ubuntu 24.04 LTS (Noble Numbat) cloud-init-ready template. \nDefault login : 'admct'. \nDefault password: 'InitCT@2025'"
  vcpus_max      = 4
  vcpus_atstartup = 2
  vm_memory      = 4096 #MB
  network_names  = var.network_names
  disk_size      = 20480 #MB
  disk_name      = "ubuntu-24.04-disk-0"
  vm_tags        = ["Generated by Packer", "Ubuntu", "cloud-init"]

  ssh_username            = "admct"
  ssh_password            = "InitCT@2025"

  ssh_wait_timeout        = "60000s"
  ssh_handshake_attempts  = 10000

  communicator = "ssh"
  output_directory = "packer-template-ubuntu-24.04"
  pause_before_connecting = "60s"

  # Conserver la VM en cas d'échec pour faciliter le débogage
  keep_vm          = "never"
  format = "xva_compressed"

  # Permet de faire un XVA de type VM ou Template
  skip_set_template = true
}

build {
  sources = ["xenserver-iso.ubuntu24"]

  provisioner "file" {
    source      = "packer/common/"
    destination = "/tmp/"
  }

  provisioner "file" {
    source      = "packer/ubuntu/extras/"
    destination = "/tmp/"
  }

  # Exécution des scripts
  provisioner "shell" {
    inline = [
      "chmod +x /tmp/*.sh",

      # Scripts communs
      "sudo /tmp/update_system.sh",
      "sudo /tmp/harden_ssh.sh",
      "sudo /tmp/harden_system.sh",
      "sudo /tmp/setup_motd.sh",
      
      # Scripts spécifiques à Ubuntu (incluant l'activation de cloud-init)
      "sudo /tmp/ubuntu_specific.sh",

      # Suppression des scripts
      "rm -f /tmp/*.sh"
    ]
  }
}
