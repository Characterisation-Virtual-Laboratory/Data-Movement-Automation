#!/bin/bash

SCRIPT_NAME="TransferScript"
USER_NAME="user"
INSTALL_PATH="/usr/local/scripts/${SCRIPT_NAME}"
SYSTEMD_PATH="/etc/systemd/system"

# Ensure Folder Structure Exists
mkdir -p ${INSTALL_PATH}/logs

# Copy files to respective locations
cp TransferScript.py ${INSTALL_PATH}/${SCRIPT_NAME}.py
cp config.json ${INSTALL_PATH}/
cp excludes.txt ${INSTALL_PATH}/
touch ${INSTALL_PATH}/rclone.conf
cp TransferScript.service ${SYSTEMD_PATH}/${SCRIPT_NAME}.service
cp TransferScript.timer ${SYSTEMD_PATH}/${SCRIPT_NAME}.timer

# Update permissions
chown -R ${USER_NAME} ${INSTALL_PATH}

# Update service file
sed -i 's|^User=.*|User=${USER_NAME}|g' ${SYSTEMD_PATH}/${SCRIPT_NAME}.service
sed -i 's|^ExecStart=.*|ExecStart=/usr/bin/python3 -O ${INSTALL_PATH}/${SCRIPT_NAME}.py|g' ${SYSTEMD_PATH}/${SCRIPT_NAME}.service

# Ensure Permissions
chmod 755 ${INSTALL_PATH}/${SCRIPT_NAME}.py
