#!/bin/bash
set -e

echo "Application des mesures de hardening système..."
echo '* hard core 0' >> /etc/security/limits.conf
echo '* soft nproc 1000' >> /etc/security/limits.conf
echo '* hard nproc 1500' >> /etc/security/limits.conf
echo 'kernel.randomize_va_space = 2' >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.rp_filter = 1' >> /etc/sysctl.conf
echo 'net.ipv4.conf.default.rp_filter = 1' >> /etc/sysctl.conf
echo 'net.ipv4.icmp_echo_ignore_broadcasts = 1' >> /etc/sysctl.conf
sysctl -p
echo "Application des mesures de hardening système terminée."
