"""
Run this directly in terminal:  python debug_scan.py
Yeh scan_network() ko seedha test karega — Streamlit ke bahar.
Output terminal mein aayega.
"""

import re
import socket
import subprocess
import concurrent.futures
import platform


def ping(ip: str) -> bool:
    if platform.system().lower() == "windows":
        cmd = ["ping", "-n", "1", "-w", "300", ip]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]
    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, timeout=2)
        return result.returncode == 0
    except Exception:
        return False


def scan_network(base: str):
    print(f"\n[1] Pinging all hosts in {base}.1 - {base}.254 ...")
    targets = [f"{base}.{i}" for i in range(1, 255)]
    alive = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as ex:
        results = list(ex.map(ping, targets))
    for ip, ok in zip(targets, results):
        if ok:
            alive.append(ip)
            print(f"    ✅ PING OK: {ip}")
    print(f"\n[1] Ping done. {len(alive)} host(s) responded.\n")

    print("[2] Reading ARP table (arp -a) ...")
    try:
        raw = subprocess.run(["arp", "-a"],
                             capture_output=True, text=True, timeout=10).stdout
        print(raw)
    except Exception as e:
        print(f"    ❌ arp -a failed: {e}")
        return []

    MAC_RE = re.compile(r'(?:[0-9a-fA-F]{2}[:\-]){5}[0-9a-fA-F]{2}')
    IP_RE  = re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b')

    devices = {}
    print(f"[3] Parsing ARP for subnet {base}.x ...")
    for line in raw.splitlines():
        if "incomplete" in line.lower():
            continue
        ip_m  = IP_RE.search(line)
        mac_m = MAC_RE.search(line)
        if not ip_m or not mac_m:
            continue
        ip  = ip_m.group(1)
        mac = mac_m.group(0).upper().replace("-", ":")
        if not ip.startswith(base + "."):
            continue
        if mac in ("FF:FF:FF:FF:FF:FF", "00:00:00:00:00:00"):
            continue
        octets = ip.split(".")
        if len(octets) != 4 or not all(o.isdigit() and 0 <= int(o) <= 255 for o in octets):
            continue
        devices[ip] = {"ip": ip, "mac": mac}
        print(f"    ✅ Found: {ip}  →  {mac}")

    print(f"\n[4] TOTAL DEVICES FOUND: {len(devices)}")
    for d in devices.values():
        print(f"    {d['ip']}   {d['mac']}")
    return list(devices.values())


# ── AUTO DETECT BASE ──
try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    base = ".".join(local_ip.split(".")[:3])
except Exception:
    local_ip = "Unknown"
    base = "192.168.0"

print(f"Local IP  : {local_ip}")
print(f"Base      : {base}")

scan_network(base)
