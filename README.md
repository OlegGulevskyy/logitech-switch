# logi-switch

Move a Logitech MX mouse + keyboard between Easy-Switch slots from software.
Slot 1 = Mac, slot 2 = Ubuntu. The machine you are *leaving* sends the command.

Trigger: rest the pointer in a screen corner for a moment.
- Ubuntu: top-right corner -> Mac
- macOS: bottom-left corner -> Ubuntu

## Ubuntu (once, X11 session)
    sudo ./install-ubuntu.sh
Then reconnect the devices to Ubuntu once (press their slot-2 buttons) and log
out/in. The corner watcher (`hot-corner.py`) starts from
`~/.config/autostart/logi-switch-corner.desktop`.

## macOS (once)
Copy this folder to the Mac, then `./install-macos.sh` and reload Hammerspoon.
It writes `~/.hammerspoon/logi_switch.lua` and requires it from `init.lua`.

## Check / debug
    /usr/bin/python3 switch-hosts.py --list     # which slot each device is on
    /usr/bin/python3 switch-hosts.py 2          # send everything to slot 2
On Ubuntu use `/usr/bin/python3`: that is the interpreter `python3-hid` is installed for.
