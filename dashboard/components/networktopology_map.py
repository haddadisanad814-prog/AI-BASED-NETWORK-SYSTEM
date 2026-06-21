import streamlit as st
import socket
import subprocess
import platform
import concurrent.futures
import psutil
from datetime import datetime

# ================= DEVICE TYPE DETECTION =================
def detect_device_type(ip, hostname):
    last_octet = int(ip.split(".")[-1])
    hostname_lower = hostname.lower()

    if last_octet == 1 or last_octet == 254:
        return "router", "📡 Router"
    if "router" in hostname_lower or "gateway" in hostname_lower:
        return "router", "📡 Router"
    if "switch" in hostname_lower or "sw" in hostname_lower:
        return "switch", "🔀 Switch"
    if "printer" in hostname_lower or "print" in hostname_lower:
        return "printer", "🖨️ Printer"
    if "android" in hostname_lower or "iphone" in hostname_lower or "phone" in hostname_lower:
        return "mobile", "📱 Mobile"
    if last_octet in range(2, 10):
        return "switch", "🔀 Switch"
    return "client", "💻 Client"


# ================= PING =================
def ping_host(ip):
    try:
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "1", "-w", "500", ip]
        else:
            cmd = ["ping", "-c", "1", "-W", "1", ip]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except:
        return False


# ================= HOSTNAME RESOLVE =================
def resolve_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return ip


# ================= SCAN ONE IP =================
def scan_ip(ip):
    if ping_host(ip):
        hostname = resolve_hostname(ip)
        device_type, device_label = detect_device_type(ip, hostname)
        return {
            "ip": ip,
            "hostname": hostname if hostname != ip else "—",
            "type": device_type,
            "label": device_label,
            "status": "UP"
        }
    return None


# ================= FULL SUBNET SCAN =================
def scan_network(base_ip="192.168.29", max_hosts=254, threads=50):
    ips = [f"{base_ip}.{i}" for i in range(1, max_hosts + 1)]
    devices = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        results = executor.map(scan_ip, ips)
    for r in results:
        if r:
            devices.append(r)
    return devices


# ================= GET LOCAL IP =================
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"


# ================= GET LIVE CONNECTIONS =================
def get_connected_ips():
    connections = []

    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED' and conn.raddr:
                ip = conn.raddr.ip
                port = conn.raddr.port

                if ip.startswith("127.") or ip == "::1":
                    continue

                hostname = ip
                try:
                    hostname = socket.getfqdn(ip)
                except:
                    pass

                connections.append({
                    "ip": ip,
                    "port": port,
                    "hostname": hostname
                })

    except:
        pass

    # remove duplicates
    seen = set()
    unique = []

    for c in connections:
        if c["ip"] not in seen:
            seen.add(c["ip"])
            unique.append(c)

    return unique


# ================= MAIN DASHBOARD =================
def show_topology(cpu, ram, network):

    st.markdown("## 🌐 NETWORK TOPOLOGY MAP")

    local_ip = get_local_ip()

    # ================= STATUS CARDS =================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if network == "DOWN":
            st.error("📡 NETWORK DOWN")
        else:
            st.success("📡 NETWORK UP")

    with col2:
        if cpu > 90:
            st.error("⚠️ CPU HIGH")
        else:
            st.success(f"🔀 CPU: {cpu}%")

    with col3:
        if ram > 90:
            st.error("⚠️ RAM HIGH")
        else:
            st.success(f"🖥 RAM: {ram}%")

    with col4:
        st.success(f"💻 THIS SYSTEM\n🔵 {local_ip}")

    st.markdown("---")

    # ================= TOPOLOGY VIEW =================
    st.markdown("### 🗺️ TOPOLOGY VIEW")
st.markdown("""
🌍 INTERNET
     │
     ▼
📡 ROUTER
     │
     ▼
💻 THIS SYSTEM
""")