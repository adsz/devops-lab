#!/bin/bash
apt-get update && \
apt-get install -y curl wget git gcc vim zsh python-dev libkrb5-dev iproute2 atop htop lsof ftp lftp mc curl iputils-ping net-tools traceroute openssh-server ruby && \
sudo timedatectl set-timezone Europe/Warsaw && \
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" && \
apt-get install python3-pip -y && \
pip3 install --upgrade pip && \
pip3 install --upgrade virtualenv && \
pip3 install pywinrm[kerberos] && \
apt install krb5-user -y && \ 
pip3 install pywinrm && \
pip3 install ansible && \
echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
ssh-keygen -A && \
service ssh start