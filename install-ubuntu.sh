#!/usr/bin/env bash
# One-time Ubuntu setup. Run with: sudo ./install-ubuntu.sh
set -euo pipefail
cd "$(dirname "$0")"
apt-get install -y python3-hid
install -m 644 60-logitech-hidraw.rules /etc/udev/rules.d/60-logitech-hidraw.rules
udevadm control --reload-rules
udevadm trigger --subsystem-match=hidraw
echo "Done. Reconnect the mouse/keyboard once so the new permissions apply."
