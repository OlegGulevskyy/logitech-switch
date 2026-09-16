#!/usr/bin/env bash
# One-time macOS setup. Copy this folder to the Mac and run: ./install-macos.sh
set -euo pipefail
cd "$(dirname "$0")"
brew list hidapi >/dev/null 2>&1 || brew install hidapi
brew list --cask hammerspoon >/dev/null 2>&1 || brew install --cask hammerspoon
python3 -m pip install --user --break-system-packages hid 2>/dev/null || python3 -m pip install --user hid
mkdir -p ~/.hammerspoon
SCRIPT="$(pwd)/switch-hosts.py"
grep -q "switch-hosts" ~/.hammerspoon/init.lua 2>/dev/null || cat >> ~/.hammerspoon/init.lua <<LUA

-- Logitech: send mouse + keyboard to the Ubuntu slot (2). Cmd+Alt+S.
hs.hotkey.bind({"cmd", "alt"}, "s", function()
  hs.task.new("/usr/bin/python3", nil, {"$SCRIPT", "2"}):start()
end)
LUA
echo "Done. Open Hammerspoon once, allow Accessibility, then reload its config."
echo "macOS may also ask to grant python3 Input Monitoring the first time."
