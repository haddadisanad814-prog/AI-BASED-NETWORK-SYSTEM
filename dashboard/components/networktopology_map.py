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


# ================= GET CONNECTED IPS (live connections) =================
def get_connected_ips():
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED' and conn.raddr:
                ip = conn.raddr.ip
                port = conn.raddr.port
                if ip.startswith("127.") or ip == "::1":
                    continue
                try:
                    hostname = socket.getfqdn(ip)
                except:
                    hostname = ip
                connections.append({
                    "ip": ip,
                    "port": port,
                    "hostname": hostname if hostname != ip else "—"
                })
    except:
        pass
    seen = set()
    unique = []
    for c in connections:
        if c["ip"] not in seen:
            seen.add(c["ip"])
            unique.append(c)
    return unique


# ================= MAIN TOPOLOGY DISPLAY =================
def show_topology(cpu, ram, network):
    st.markdown("## 🌐 NETWORK TOPOLOGY MAP")

    local_ip = get_local_ip()

    # Detect base network from local IP
    if local_ip != "Unknown":
        base = ".".join(local_ip.split(".")[:3])
    else:
        base = "192.168.29"

    # ================= STATUS CARDS =================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if network == "DOWN":
            st.error("📡 ROUTER DOWN")
        else:
            st.success("📡 ROUTER UP")
    with col2:
        if cpu > 90:
            st.error("🔀 SWITCH CPU HIGH")
        else:
            st.success("🔀 SWITCH NORMAL")
    with col3:
        if ram > 90:
            st.error("🖥 SERVER RAM HIGH")
        else:
            st.success("🖥 SERVER NORMAL")
    with col4:
        st.success(f"💻 THIS PC\n🔵 {local_ip}")

    st.markdown("---")

    # ================= WAN SCANNER =================
    st.markdown("### 🔍 WAN DEVICE SCANNER")
    st.caption(f"Network Range: `{base}.1` → `{base}.254`")

    col_scan, col_info = st.columns([1, 3])
    with col_scan:
        scan_btn = st.button("🚀 Scan Network", type="primary")

    if scan_btn:
        with st.spinner(f"🔍 Scanning {base}.0/24 ... (takes 15-30 sec)"):
            devices = scan_network(base_ip=base)
            st.session_state["scanned_devices"] = devices
            st.session_state["scan_time"] = datetime.now().strftime("%H:%M:%S")

    # ================= SHOW SCAN RESULTS =================
    if "scanned_devices" in st.session_state and st.session_state["scanned_devices"]:
        devices = st.session_state["scanned_devices"]
        scan_time = st.session_state.get("scan_time", "—")

        st.success(f"✅ {len(devices)} device(s) found on network | Last scan: {scan_time}")

        # ---- SUMMARY COUNTS ----
        routers = [d for d in devices if d["type"] == "router"]
        switches = [d for d in devices if d["type"] == "switch"]
        clients = [d for d in devices if d["type"] == "client"]
        mobiles = [d for d in devices if d["type"] == "mobile"]
        printers = [d for d in devices if d["type"] == "printer"]

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("📡 Routers", len(routers))
        m2.metric("🔀 Switches", len(switches))
        m3.metric("💻 Clients", len(clients))
        m4.metric("📱 Mobiles", len(mobiles))
        m5.metric("🖨️ Printers", len(printers))

        st.markdown("---")

        # ---- VISUAL TOPOLOGY ----
        st.markdown("### 🗺️ LIVE TOPOLOGY VIEW")

        # Show Internet → Router → devices flow
        st.markdown("""
```
🌍 INTERNET
     │
     ▼
📡 ROUTER (Gateway)
     │
     ├──── 🔀 SWITCHES
     │          │
     │          └──── 💻 CLIENTS / 📱 MOBILES
     │
     └──── 💻 DIRECT CLIENTS
```
""")

        # ---- DEVICE TABLE ----
        st.markdown("### 📋 ALL DETECTED DEVICES")

        # Group by type
        type_order = ["router", "switch", "client", "mobile", "printer"]
        type_names = {
            "router": "📡 Routers",
            "switch": "🔀 Switches",
            "client": "💻 Clients / PCs",
            "mobile": "📱 Mobile Devices",
            "printer": "🖨️ Printers"
        }

        for dtype in type_order:
            group = [d for d in devices if d["type"] == dtype]
            if not group:
                continue

            st.markdown(f"#### {type_names[dtype]}")
            h1, h2, h3, h4 = st.columns([2, 3, 2, 1])
            h1.markdown("**IP Address**")
            h2.markdown("**Hostname**")
            h3.markdown("**Device Type**")
            h4.markdown("**Status**")

            for d in group:
                c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
                # Highlight local machine
                if d["ip"] == local_ip:
                    c1.code(f"{d['ip']} ← YOU")
                else:
                    c1.code(d["ip"])
                c2.write(d["hostname"])
                c3.write(d["label"])
                c4.success("🟢 UP")

            st.markdown("---")

    elif "scanned_devices" in st.session_state and len(st.session_state["scanned_devices"]) == 0:
        st.warning("⚠️ Koi device nahi mila - Network DOWN ho sakta hai ya firewall block kar raha hai")

    # ================= LIVE ACTIVE CONNECTIONS =================
    st.markdown("### 🔗 LIVE ACTIVE CONNECTIONS (Real-time)")
    connected = get_connected_ips()
    if not connected:
        st.info("🔍 Koi active connection nahi mila abhi")
    else:
        st.success(f"✅ {len(connected)} live connection(s)")
        h1, h2, h3 = st.columns([2, 2, 4])
        h1.markdown("**🌐 IP**")
        h2.markdown("**🔌 Port**")
        h3.markdown("**🖥 Hostname**")
        st.markdown("---")
        for c in connected:
            c1, c2, c3 = st.columns([2, 2, 4])
            c1.code(c["ip"])
            c2.write(str(c["port"]))
            c3.write(c["hostname"])

    st.caption(f"🏠 Local IP: {local_ip} | Network: {network} | CPU: {cpu}% | RAM: {ram}%")