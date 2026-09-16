#!/usr/bin/env bash
# One-time Ubuntu setup. Run with: sudo ./install-ubuntu.sh
set -euo pipefail
cd "$(dirname "$0")"
apt-get install -y python3-hid python3-gi gir1.2-gtk-3.0
install -m 644 60-logitech-hidraw.rules /etc/udev/rules.d/60-logitech-hidraw.rules
udevadm control --reload-rules
udevadm trigger --subsystem-match=hidraw

# Hot corner (top-right -> Mac), started at login for the invoking user.
USER_HOME="$(getent passwd "${SUDO_USER:-$USER}" | cut -d: -f6)"
sudo -u "${SUDO_USER:-$USER}" mkdir -p "$USER_HOME/.config/autostart"
sudo -u "${SUDO_USER:-$USER}" tee "$USER_HOME/.config/autostart/logi-switch-corner.desktop" >/dev/null <<EOF
[Desktop Entry]
Type=Application
Name=Logitech hot corner
Comment=Top-right screen corner sends mouse + keyboard to the Mac
Exec=/usr/bin/python3 $(pwd)/hot-corner.py 1
X-GNOME-Autostart-enabled=true
NoDisplay=true
EOF
echo "Done. Reconnect the mouse/keyboard once so the new permissions apply,"
echo "then log out and back in (or run: /usr/bin/python3 $(pwd)/hot-corner.py &)."
