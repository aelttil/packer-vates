#!/bin/bash
set -e

echo "Installation des outils Xen Guest Agent..."
apt-get update
wget https://gitlab.com/xen-project/xen-guest-agent/-/jobs/6041608357/artifacts/raw/target/release/xen-guest-agent_0.4.0_amd64.deb
RUNLEVEL=1 dpkg -i xen-guest-agent_0.4.0_amd64.deb
rm xen-guest-agent_0.4.0_amd64.deb
echo "Installation des outils Xen Guest Agent terminée."
