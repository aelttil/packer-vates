# XCP-ng connection variables
variable "remote_host" {
  type        = string
  description = "The ip or fqdn of your XCP-ng. It must be the master"
  sensitive   = true
}

variable "remote_username" {
  type        = string
  description = "The username used to interact with your XCP-ng"
  sensitive   = true
  default     = "root"
}

variable "remote_password" {
  type        = string
  description = "The password used to interact with your XCP-ng"
  sensitive   = true
}

# Storage variables
variable "sr_iso_name" {
  type        = string
  description = "The ISO-SR to packer will use"
  default     = "isos"
}

variable "sr_name" {
  type        = string
  description = "The name of the SR to packer will use"
}

# VM configuration variables
variable "vm_memory" {
  type        = number
  description = "VM memory in MB"
  default     = 2048
}

variable "vm_vcpus" {
  type        = number
  description = "Number of virtual CPUs"
  default     = 2
}

variable "disk_size" {
  type        = number
  description = "Disk size in MB"
  default     = 20480
}

# Network configuration
variable "network_name" {
  type        = string
  description = "XCP-ng network name"
  default     = "local-network"
}

# SSH configuration
variable "ssh_username" {
  type        = string
  description = "SSH username for provisioning"
  default     = "debian"
}

variable "ssh_password" {
  type        = string
  description = "SSH password for provisioning"
  sensitive   = true
  default     = "debian"
}

variable "ssh_timeout" {
  type        = string
  description = "SSH timeout"
  default     = "60000s"
}
