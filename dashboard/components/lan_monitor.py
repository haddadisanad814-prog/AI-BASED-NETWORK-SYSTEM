import pandas as pd
import socket
import os
import re
import platform
import subprocess
import concurrent.futures
import streamlit as st
import networkx as nx
from pyvis.network import Network
import psutil
import time
from datetime import datetime


# ================= PING =================
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


# ================= SCAN NETWORK =================
def scan_network(base: str) -> list[dict]:
    targets = [f"{base}.{i}" for i in range(1, 255)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as ex:
        list(ex.map(ping, targets))

    try:
        raw = subprocess.run(["arp", "-a"],
                             capture_output=True, text=True,
                             timeout=10).stdout
    except Exception:
        return []

    MAC_RE = re.compile(r'(?:[0-9a-fA-F]{2}[:\-]){5}[0-9a-fA-F]{2}')
    IP_RE  = re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b')

    devices: dict[str, dict] = {}

    for line in raw.splitlines():
        if "incomplete" in line.lower():
            continue
        ip_match  = IP_RE.search(line)
        mac_match = MAC_RE.search(line)
        if not ip_match or not mac_match:
            continue
        ip  = ip_match.group(1)
        mac = mac_match.group(0).upper().replace("-", ":")
        if not ip.startswith(base + "."):
            continue
        if mac in ("FF:FF:FF:FF:FF:FF", "00:00:00:00:00:00"):
            continue
        octets = ip.split(".")
        if len(octets) != 4 or not all(o.isdigit() and 0 <= int(o) <= 255
                                        for o in octets):
            continue
        devices[ip] = {"ip": ip, "mac": mac}

    return list(devices.values())


# ================= HOSTNAME =================
def get_hostname(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "Unknown"


# ================= DEVICE TYPE =================
_OUI_MAP = {
    "00:00:48": "Printer", "00:00:C9": "Printer",
    "00:40:8C": "Camera",  "2C:AA:8E": "Camera",
    "00:00:0C": "Router",  "00:1A:A1": "Router",
    "F8:72:EA": "Router",  "CC:32:E5": "Router",
    "00:50:56": "PC",      "08:00:27": "PC",
    "AC:16:2D": "PC",      "B8:27:EB": "PC",
}

def device_type(device: dict | str) -> str:
    if isinstance(device, str):
        ip  = device
        mac = ""
    else:
        ip  = device.get("ip", "")
        mac = device.get("mac", "")

    oui = mac[:8].upper() if mac else ""
    if oui in _OUI_MAP:
        return _OUI_MAP[oui]

    try:
        last = int(ip.split(".")[-1])
    except (ValueError, IndexError):
        return "PC"

    if last == 1:
        return "Router"
    if last in (253, 254):
        return "Server"
    return "PC"


# ================= AI HEALTH SCORE =================
def health_score() -> int:
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    return max(0, int(100 - (cpu + ram) / 2))


# ================= BUILD GRAPH =================
def build_graph(devices: list[dict]) -> nx.Graph:
    G = nx.Graph()

    router_label = "Router\n(Gateway)"
    G.add_node(router_label, color="red", label="🌐 Gateway\nRouter")

    switches, pcs, servers, printers, cameras, others = [], [], [], [], [], []

    for device in devices:
        t = device_type(device)
        if t == "Router":
            ip  = device["ip"]
            mac = device["mac"]
            G.nodes[router_label]["label"] = f"🌐 Gateway\n{ip}\n{mac}"
        elif t == "Switch":
            switches.append(device)
        elif t == "PC":
            pcs.append(device)
        elif t == "Server":
            servers.append(device)
        elif t == "Printer":
            printers.append(device)
        elif t == "Camera":
            cameras.append(device)
        else:
            others.append(device)

    hub = switches[0]["ip"] if switches else router_label

    for d in switches:
        ip  = d["ip"]
        mac = d["mac"]
        G.add_node(ip, label=f"🔀 Switch\n{ip}\n{mac}", color="orange")
        G.add_edge(router_label, ip)

    for d in pcs:
        ip    = d["ip"]
        mac   = d["mac"]
        score = health_score()
        color = "red" if score < 70 else "green"
        G.add_node(ip, label=f"💻 PC\n{ip}\n{mac}", color=color, health=score)
        G.add_edge(hub, ip)

    for d in servers:
        ip  = d["ip"]
        mac = d["mac"]
        G.add_node(ip, label=f"🖥 Server\n{ip}", color="blue")
        G.add_edge(router_label, ip)

    for d in printers:
        ip = d["ip"]
        G.add_node(ip, label=f"🖨 Printer\n{ip}", color="purple")
        G.add_edge(hub, ip)

    for d in cameras:
        ip = d["ip"]
        G.add_node(ip, label=f"📷 Camera\n{ip}", color="cyan")
        G.add_edge(hub, ip)

    for d in others:
        ip  = d["ip"]
        mac = d["mac"]
        G.add_node(ip, label=f"❓ {ip}\n{mac}", color="gray")
        G.add_edge(hub, ip)

    return G


# ================= DRAW GRAPH — returns HTML string directly =================
# FIX: Removed temp file approach entirely.
# draw_graph() now returns HTML string directly — no file read/write,
# no risk of temp file deletion causing silent graph failure.
def draw_graph(G: nx.Graph) -> str:
    net = Network(height="700px", width="100%",
                  bgcolor="#0f0f0f", font_color="white")

    for node, data in G.nodes(data=True):
        label = data.get("label", str(node))
        if "health" in data:
            label += f"\n({data['health']}%)"
        net.add_node(str(node), label=label, color=data.get("color", "gray"))

    for u, v in G.edges():
        net.add_edge(str(u), str(v))

    # FIX: generate_html() returns string directly — no temp file needed
    return net.generate_html()


# ================= SHOW TOPOLOGY =================
def show_topology(cpu, ram, network):
    st.markdown("## 🌐 NETWORK TOPOLOGY MAP")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.error("📡 ROUTER DOWN") if network == "DOWN" else st.success("📡 ROUTER UP")
    with col2:
        st.error("🔀 SWITCH CPU HIGH") if cpu > 90 else st.success("🔀 SWITCH NORMAL")
    with col3:
        st.error("🖥 SERVER RAM HIGH") if ram > 90 else st.success("🖥 SERVER NORMAL")
    with col4:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "Unknown"
        st.success(f"💻 THIS MACHINE\n🔵 {local_ip}")

    st.markdown("---")
    show_lan()


# ================= MAIN LAN SCANNER UI =================
def show_lan():
    st.title("🖧 CISCO NOC SYSTEM (AI LAN MONITOR)")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        base = ".".join(local_ip.split(".")[:3])
    except Exception:
        local_ip = "Unknown"
        base = "192.168.0"

    st.info(f"🌐 Detected Network: {base}.0/24  |  Your IP: {local_ip}")

    # -------------------------------------------------------
    # FIX: Auto-refresh — 1-sec tick, no blocking sleep
    # -------------------------------------------------------
    auto = st.checkbox("🔄 LIVE MODE (Auto Refresh every 30 sec)")
    if auto:
        if "last_auto_refresh" not in st.session_state:
            st.session_state["last_auto_refresh"] = time.time()
        elapsed   = time.time() - st.session_state["last_auto_refresh"]
        remaining = max(0, 30 - int(elapsed))
        st.info(f"🔄 Auto-refresh in {remaining}s")
        if elapsed >= 30:
            st.session_state["last_auto_refresh"] = time.time()
            st.rerun()
        time.sleep(1)
        st.rerun()

    if "selected_device" not in st.session_state:
        st.session_state.selected_device = None

    # -------------------------------------------------------
    # FIX: Scan button debounce — no double-trigger freeze
    # -------------------------------------------------------
    if st.button("🚀 SCAN & BUILD FINAL NETWORK MAP", type="primary"):
        last = st.session_state.get("last_manual_scan", 0)
        if time.time() - last < 15:
            st.warning("⏳ Scan just ran. Please wait a moment.")
        else:
            st.session_state["last_manual_scan"] = time.time()
            # Clear old graph so it rebuilds fresh after new scan
            st.session_state.pop("graph_html", None)
            st.session_state.pop("graph_fingerprint", None)
            with st.spinner("🔍 Scanning network... (wait 10-15 sec)"):
                devices   = scan_network(base)
                scan_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            st.session_state["devices"]   = devices
            st.session_state["scan_time"] = scan_time

    if "devices" not in st.session_state or not st.session_state["devices"]:
        st.info("👆 Scan button dabao - network ke sab devices detect honge")
        return

    devices   = st.session_state["devices"]
    scan_time = st.session_state.get("scan_time", "—")

    # ---------- disconnect detection ----------
    if "previous_devices" not in st.session_state:
        st.session_state["previous_devices"] = []

    old_ips      = {d["ip"] for d in st.session_state["previous_devices"]}
    new_ips      = {d["ip"] for d in devices}
    disconnected = old_ips - new_ips

    if disconnected:
        st.markdown("## 🚨 DEVICE DISCONNECT ALERT")
        for ip in disconnected:
            st.error(f"❌ Device Offline: {ip}")

    st.session_state["previous_devices"] = list(devices)

    st.success(f"✅ {len(devices)} device(s) found | Last Scan: {scan_time}")

    # ================= GRAPH + INSPECTOR =================
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🗺️ VISUAL NETWORK MAP")

        # FIX: Build graph only when device list changes (fingerprint check)
        # FIX: graph_html is now a string from generate_html(), no temp file
        device_fingerprint = str(sorted([d["ip"] for d in devices]))

        if st.session_state.get("graph_fingerprint") != device_fingerprint:
            try:
                G = build_graph(devices)
                st.session_state["graph_html"]        = draw_graph(G)
                st.session_state["graph_fingerprint"] = device_fingerprint
            except Exception as e:
                st.session_state["graph_html"] = None
                st.error(f"❌ Graph build error: {e}")

        if st.session_state.get("graph_html"):
            st.components.v1.html(st.session_state["graph_html"], height=700)
        else:
            st.warning("⚠️ Graph could not be rendered. Check pyvis is installed: pip install pyvis")

    with col2:
        st.markdown("### 🧠 DEVICE INSPECTOR")

        # FIX: Show device IP buttons so user doesn't have to type manually
        ip_list = [d["ip"] for d in devices]
        selected_from_list = st.selectbox(
            "📋 Select device from list", ["-- Select --"] + ip_list, key="inspector_select"
        )
        typed = st.text_input("Or type IP manually", key="inspector_ip")

        # Typed input takes priority over selectbox
        if typed:
            st.session_state.selected_device = typed
        elif selected_from_list != "-- Select --":
            st.session_state.selected_device = selected_from_list

        if st.session_state.selected_device:
            ip     = st.session_state.selected_device
            record = next((d for d in devices if d["ip"] == ip), {"ip": ip, "mac": ""})
            t      = device_type(record)

            # FIX: psutil called once — consistent values
            cpu_pct = psutil.cpu_percent(interval=0.1)
            ram_pct = psutil.virtual_memory().percent
            score   = max(0, int(100 - (cpu_pct + ram_pct) / 2))

            st.success(f"📍 Device: {ip}")
            st.write(f"**Type:** {t}")
            st.write(f"**MAC:** {record.get('mac', 'Unknown')}")
            st.write(f"**Hostname:** {record.get('hostname', get_hostname(ip))}")

            if t == "PC":
                st.metric("Health Score", f"{score}%")
                st.write(f"CPU: {cpu_pct}%")
                st.write(f"RAM: {ram_pct}%")

            st.warning("Live monitoring active")
            if score < 70:
                st.error("⚠️ AI ALERT: Device Health Critical")
            else:
                st.success("✅ Device Healthy")

    # ================= NETWORK OVERVIEW =================
    st.markdown("---")
    st.markdown("## 📊 NETWORK OVERVIEW")

    counts = {"Router": 0, "Switch": 0, "PC": 0,
              "Server": 0, "Printer": 0, "Camera": 0, "Other": 0}
    for d in devices:
        t = device_type(d)
        if t in counts:
            counts[t] += 1
        else:
            counts["Other"] += 1

    score      = health_score()
    risk_nodes = 1 if score < 70 else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("🟢 Devices",  len(devices))
    c2.metric("📡 Routers",  counts["Router"])
    c3.metric("🔀 Switches", counts["Switch"])
    c4.metric("💻 PCs",      counts["PC"])
    c5.metric("🖥 Servers",  counts["Server"])
    c6.metric("🔴 Risk",     risk_nodes)

    st.info("🤖 AI Health Score = this machine's CPU/RAM only (agents needed for remote devices).")

    # ================= AI ALERT CENTER =================
    st.markdown("---")
    st.markdown("## 🚨 AI ALERT CENTER")

    for d in devices:
        ip = d["ip"]
        if score < 60:
            st.error(f"🔴 {ip} : CRITICAL ({score}%)")
        elif score < 75:
            st.warning(f"🟡 {ip} : WARNING ({score}%)")
        else:
            st.success(f"🟢 {ip} : HEALTHY ({score}%)")

    st.markdown("## 🤖 AI RECOMMENDATIONS")
    if score < 60:
        st.error("High CPU/RAM detected. Restart services and check resource usage.")
    elif score < 75:
        st.warning("Monitor device performance. Possible future issue.")
    else:
        st.success("Network operating normally.")

    # ================= NETWORK STATISTICS =================
    st.markdown("---")
    st.markdown("## 📈 NETWORK STATISTICS")

    chart_data = pd.DataFrame({
        "Count": [counts["Router"], counts["Switch"], counts["PC"],
                  counts["Server"], counts["Printer"], counts["Camera"]]
    }, index=["Routers", "Switches", "PCs", "Servers", "Printers", "Cameras"])
    st.bar_chart(chart_data)

    # ================= DEVICE INVENTORY =================
    st.markdown("---")
    st.markdown("## 🖥 DEVICE INVENTORY")

    table_data = []
    for d in devices:
        table_data.append({
            "IP Address":  d["ip"],
            "MAC Address": d["mac"],
            "Hostname":    d.get("hostname", "Unknown"),
            "Device Type": device_type(d),
            "Status":      "✅ UP",
        })

    df = pd.DataFrame(table_data)

    # FIX: st.form — rerun only on submit, not on every keystroke
    with st.form(key="search_form"):
        search = st.text_input("🔍 Search IP / Hostname / MAC")
        st.form_submit_button("🔍 Search")

    if search:
        mask = (
            df["IP Address"].str.contains(search, case=False, na=False)  |
            df["Hostname"].str.contains(search, case=False, na=False)     |
            df["MAC Address"].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Export Device List", csv,
                       "device_inventory.csv", "text/csv")

    st.success(f"✅ Last Scan: {scan_time}")