#!/bin/bash
# Install python-WoL as a systemd service

set -e
INSTALL_DIR="/opt/python-WoL"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing python-WoL to $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"
sudo cp "$REPO_DIR/python_wol.py" "$INSTALL_DIR/"
sudo pip3 install -r "$REPO_DIR/requirements.txt"

sudo cp "$REPO_DIR/python-wol.service" /etc/systemd/system/
sudo systemctl daemon-reload
echo "Done. Enable and start with:"
echo "  sudo systemctl enable python-wol"
echo "  sudo systemctl start python-wol"
echo ""
echo "Ensure /etc/python-WoL.conf exists with your hosts (IP MAC per line)."
