# Packer Templates for XCP-ng

This repository contains Packer templates for building Debian virtual machine images for XCP-ng.

## Prerequisites

- [Packer](https://www.packer.io/downloads) (v1.8.0 or later)
- Access to an XCP-ng host
- [Packer XenServer Plugin](https://github.com/ddelnano/xenserver) v0.7.3

## Installing the XenServer Plugin

Before using these templates, you need to install the XenServer plugin for Packer:

```bash
packer plugins install github.com/ddelnano/xenserver@v0.7.3
```

## Supported Operating Systems

- Debian 12 (Bookworm)

## Usage

### Setting up credentials

Create a file named `credentials.auto.pkrvars.hcl` with your XCP-ng credentials:

```hcl
# XCP-ng connection details
remote_host     = "your-xcpng-host-ip-or-hostname"
remote_username = "root"
remote_password = "your-xcpng-password"

# Storage details
sr_name         = "your-storage-repository-name"

# Network details
network_name    = "your-network-name"

# SSH credentials for provisioning
ssh_username    = "debian"
ssh_password    = "debian"
```

**Note**: This file is ignored by git to prevent credentials from being committed.

### Building Debian 12

```bash
packer build -var-file=credentials.auto.pkrvars.hcl debian/debian-12.pkr.hcl
```

## Project Structure

```
packer-vates/
├── README.md
├── variables.pkr.hcl                # Common variables
├── credentials.auto.pkrvars.hcl     # Your credentials (not in git)
├── deb12-generator.pkr.hcl          # Original example file
├── http/
│   └── preseed.cfg                  # Preseed configuration for Debian
└── debian/
    ├── debian-12.pkr.hcl            # Debian 12 configuration
    └── http/
        └── preseed.cfg              # Copy of preseed.cfg (for reference)
```

**Note**: The `http/preseed.cfg` file at the root level is used by both the original example file and the modular configuration.

## Customization

You can customize the VM configurations by modifying the respective `.pkr.hcl` files or by passing variables at build time:

```bash
packer build -var="vm_memory=4096" -var="disk_size=40000" -var-file=credentials.auto.pkrvars.hcl debian/debian-12.pkr.hcl
