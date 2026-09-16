#!/usr/bin/env python3
"""Tell every connected Logitech HID++ device to hop to another Easy-Switch slot.

Usage: switch-hosts.py <slot>        slot is 1, 2 or 3 as printed on the device
       switch-hosts.py --list        show devices and which slot they are on

Works over Bluetooth and Unifying/Bolt receivers on Linux and macOS, using the
same HID++ 2.0 "Change Host" feature (0x1814) that Logi Options+ Flow uses.
"""
import sys
import time

try:
    # Debian/Ubuntu python3-hid: 'hid' is the libusb backend, which cannot see
    # Bluetooth devices; 'hidraw' is the same API over /dev/hidraw*.
    import hidraw as hid
except ImportError:
    import hid  # pip: hid (needs libhidapi)

# hidapi on macOS opens devices exclusively by default, which is refused for
# keyboards/mice ("privilege violation") and would fight Logi Options+.
_lib = getattr(hid, "hidapi", None)
if _lib is not None and hasattr(_lib, "hid_darwin_set_open_exclusive"):
    _lib.hid_darwin_set_open_exclusive(0)

LOGITECH_VID = 0x046D
REPORT_LONG = 0x11
DEVICE_INDEX_BT = 0xFF          # direct Bluetooth connection
FEATURE_ROOT = 0x0000
FEATURE_CHANGE_HOST = 0x1814
SWID = 0x0A                     # any non-zero 4-bit software id
HIDPP_USAGE_PAGES = (0xFF00, 0xFF43)  # receiver, Bluetooth


def open_device(info):
    """Support both the 'hid' (apmorton) and 'hidapi' (trezor) python packages."""
    if hasattr(hid, "Device"):
        return hid.Device(path=info["path"])
    dev = hid.device()
    dev.open_path(info["path"])
    return dev


def request(dev, device_index, feature_index, function, params=b""):
    payload = bytes([REPORT_LONG, device_index, feature_index, (function << 4) | SWID])
    payload += params
    payload += bytes(20 - len(payload))
    dev.write(payload)
    deadline = time.time() + 0.5
    while time.time() < deadline:
        data = bytes(dev.read(20, 100) or b"")
        if not data:
            continue
        # HID++ 2.0 error report
        if data[0] == REPORT_LONG and data[2] == 0xFF and data[3] == feature_index:
            raise IOError(f"HID++ error {data[5]:#x}")
        if data[1] == device_index and data[2] == feature_index and data[3] & 0x0F == SWID:
            return data[4:]
    return None


def probe(dev, device_index):
    """Return the Change Host feature index, or None if unsupported/unreachable."""
    try:
        resp = request(dev, device_index, FEATURE_ROOT, 0x00,
                       FEATURE_CHANGE_HOST.to_bytes(2, "big"))
    except IOError:
        return None
    if not resp or resp[0] == 0:
        return None
    return resp[0]


def candidates():
    seen = set()
    for info in hid.enumerate(LOGITECH_VID, 0):
        usage_page = info.get("usage_page") or 0
        # macOS lists one entry per collection; only the vendor pages talk HID++.
        if usage_page and usage_page not in HIDPP_USAGE_PAGES:
            continue
        if info["path"] in seen:
            continue
        seen.add(info["path"])
        yield info


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("1", "2", "3", "--list"):
        print(__doc__)
        sys.exit(2)
    listing = sys.argv[1] == "--list"
    target = None if listing else int(sys.argv[1]) - 1  # HID++ hosts are 0-based

    done = set()
    for info in candidates():
        try:
            dev = open_device(info)
        except Exception as err:
            print(f"{info.get('product_string') or 'device'}: {err}", file=sys.stderr)
            continue
        name = info.get("product_string") or f"pid {info['product_id']:#06x}"
        try:
            # Bluetooth device first, then receiver slots 1-6.
            for device_index in (DEVICE_INDEX_BT, 1, 2, 3, 4, 5, 6):
                key = (info["product_id"], device_index)
                if key in done:
                    continue
                feature = probe(dev, device_index)
                if feature is None:
                    continue
                done.add(key)
                if listing:
                    resp = request(dev, device_index, feature, 0x00)
                    hosts, current = resp[0], resp[1] + 1
                    print(f"{name}: on slot {current} of {hosts}")
                else:
                    try:
                        request(dev, device_index, feature, 0x01, bytes([target]))
                    except IOError as err:
                        print(f"{name}: {err}")
                        continue
                    print(f"{name}: sent switch to slot {target + 1}")
                if device_index == DEVICE_INDEX_BT:
                    break  # Bluetooth devices answer on every index; don't repeat.
        finally:
            dev.close()

    if not done:
        print("No Logitech HID++ device found. Is it connected to this machine "
              "and do you have permission to open it?", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
