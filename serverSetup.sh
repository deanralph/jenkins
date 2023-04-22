#!/bin/bash

#####################################################################
# Name: Server Setup
# Description: This script will assist in setting up a new server
# Author: Dean Ralph
# Date: 2023-01-12
# Version: 4
#####################################################################


apiToken="11522c24ccb8912c8005f66855ddea18e8"

clear
echo "###################################################"
echo -e "\033[1;33m                   DEANRALPH.NET"
echo "         SERVER SETUP SCRIPT V4.0 - Back to BASH"
echo -e "\033[0m###################################################"
echo

# Check script is being run as root user
if [ "$EUID" -ne 0 ]
  then echo -e "\033[0;31mPlease run as root"
  exit
fi

#checks if user is sudo no password
echo -e "\033[0mChecking if user is sudo no password..."
if grep -q "dean ALL=(ALL) NOPASSWD: ALL" /etc/sudoers; then
    echo "User already in sudoers"
else
    echo "Setting sudo without password..."
    echo "Taking backup of etc/sudoers"
    cp /etc/sudoers /etc/sudoers.backup
    if test -f "/etc/sudoers.backup"; then
        echo "backup successfull."
    fi
    echo "dean ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
    if grep -q "dean ALL" /etc/sudoers; then
        echo "Added to sudoers successfully"
    else
        echo -e "\033[0;31mFailed to set up are you running as root?"
        exit
    fi
fi

echo "Running updates, this may take some time"
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove && sudo apt-get autoclean -y
sudo apt install qemu-guest-agent net-tools

# Create the "jenkins" user
echo "Creating jenkins user"
useradd -m jenkins
sudo passwd jenkins

# Add "jenkins" user to the sudo group
echo "Giving jenkins user sudo without password"
usermod -aG sudo jenkins

# Give "jenkins" user passwordless sudo access
if grep -q "jenkins ALL=(ALL) NOPASSWD: ALL" /etc/sudoers; then
    echo "User already in sudoers"
else
    echo "jenkins ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
    echo "Added jenkins to sudoers successfully"
fi

# Create an SSH key pair for the "jenkins" user
echo "Creating SSH keys"
sudo -u jenkins ssh-keygen -N "" -f /home/jenkins/.ssh/id_rsa

# Create Jenkins folder and set perms
echo
echo "Creating Jenkins folder"
mkdir /jenkins
chmod -R 777 /jenkins

# Call Jenkins job to copy ssh key

echo
echo "Setting up Jenkins SSH"

ServerIP=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}')
JenkinsURL="http://10.0.0.26:8080/job/SSHKey/buildWithParameters?token=sshkeys&ServerIP=$ServerIP"

echo $JenkinsURL

curl -u dean:$apiToken $JenkinsURL