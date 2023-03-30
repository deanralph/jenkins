#!/bin/bash

# Script to update, upgrade, and autoclean up on Ubuntu
# It also checks if the script is being run as root, logs any errors to a file
# and check if a reboot is required at the end

echo -e "\033[1;33m########################################"
echo -e "#                                      #"
echo -e "#   Updating, Upgrading and Cleaning   #"
echo -e "#                                      #"
echo -e "########################################\033[0m"

# check if script is run as root
if [ "$(id -u)" != "0" ]; then
   echo -e "\033[1;31mThis script must be run as root\033[0m" 1>&2
   exit 1
fi

# update package lists and upgrade packages
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove && sudo apt-get autoclean

# check for errors and log them to a file
if [ $? -ne 0 ]; then
    echo -e "\033[1;31mErrors occurred during the update and upgrade process\033[0m" 1>&2
    echo "Errors occurred during the update and upgrade process" >> /var/log/update_errors.log
else
    # check if reboot is required
    if [ -f /var/run/reboot-required ]; then
        echo -e "\033[1;37mA reboot is required to complete the updates\033[0m"
    fi
fi