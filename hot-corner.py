#!/usr/bin/python3
"""Ubuntu (X11): rest the pointer in the top-right corner of a screen to send
the Logitech mouse + keyboard to another Easy-Switch slot (default 1 = Mac).

Usage: hot-corner.py [slot]
Started at login from ~/.config/autostart (see install-ubuntu.sh).
"""
import os
import subprocess
import sys
import time

import gi

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib  # noqa: E402

CORNER_PX = 2       # how close to the corner counts as "in" it
DWELL = 0.4         # seconds the pointer has to rest there
POLL_MS = 100
SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "switch-hosts.py")


def main():
    slot = sys.argv[1] if len(sys.argv) > 1 else "1"
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        sys.exit("hot-corner.py needs an X11 session; Wayland hides the pointer position.")
    display = Gdk.Display.get_default()
    if display is None:
        sys.exit("hot-corner.py: no display")
    pointer = display.get_default_seat().get_pointer()
    since = None
    armed = True

    def tick():
        nonlocal since, armed
        _, x, y = pointer.get_position()
        geo = display.get_monitor_at_point(x, y).get_geometry()
        in_corner = (x >= geo.x + geo.width - 1 - CORNER_PX
                     and y <= geo.y + CORNER_PX)
        if not in_corner:
            since, armed = None, True
        elif armed:
            now = time.monotonic()
            if since is None:
                since = now
            elif now - since >= DWELL:
                # The pointer stays parked here while the devices are away, so
                # only re-arm once it has left the corner.
                armed = False
                subprocess.Popen([sys.executable, SCRIPT, slot])
        return True

    GLib.timeout_add(POLL_MS, tick)
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()
