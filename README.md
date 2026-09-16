# logi-switch

Move a Logitech MX mouse + keyboard between Easy-Switch slots from software.
Slot 1 = Mac, slot 2 = Ubuntu. The machine you are *leaving* sends the command.

## Ubuntu (once)
    sudo ./install-ubuntu.sh
Then reconnect the devices to Ubuntu once (press their slot-2 buttons).
Shortcut Super+Alt+S is already registered in GNOME -> runs `switch-hosts.py 1`.

## macOS (once)
Copy this folder to the Mac, then `./install-macos.sh`.
Hammerspoon binds Cmd+Alt+S -> runs `switch-hosts.py 2`.

## Check / debug
    python3 switch-hosts.py --list     # which slot each device is on
    python3 switch-hosts.py 2          # send everything to slot 2
