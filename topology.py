import streamlit as st
import psutil
import socket

def get_connected_ips():
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED' and conn.raddr:
                ip = conn.raddr.ip
                port = conn.raddr.port
                # skip localhost
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
    except Exception as e:
        pass
    # deduplicate by IP
    seen = set()
    unique = []
    for c in connections:
        if c["ip"] not in seen:
            seen.add(c["ip"])
            unique.append(c)
    return unique

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"

def show_topology(cpu, ram, network):
    st.markdown("## 🌐 NETWORK TOPOLOGY MAP")

    # ── Top row: devices ──
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if network == "DOWN":
            st.error("📡 ROUTER\n\nSTATUS: DOWN")
        else:
            st.success("📡 ROUTER\n\nSTATUS: UP")

    with col2:
        if cpu > 90:
            st.error("🔀 SWITCH\n\nCPU HIGH")
        else:
            st.success("🔀 SWITCH\n\nNORMAL")

    with col3:
        if ram > 90:
            st.error("🖥 SERVER\n\nRAM HIGH")
        else:
            st.success("🖥 SERVER\n\nNORMAL")

    with col4:
        local_ip = get_local_ip()
        st.success(f"💻 THIS MACHINE\n\n🔵 {local_ip}")

    st.markdown("---")

    # ── Connected IPs ──
    st.markdown("### 🔗 LIVE CONNECTED IP ADDRESSES")

    connected = get_connected_ips()

    if not connected:
        st.info("🔍 Koi active connection nahi mila (ya permission nahi hai)")
    else:
        st.success(f"✅ {len(connected)} active connection(s) found")

        # table header
        h1, h2, h3 = st.columns([2, 2, 4])
        h1.markdown("**🌐 IP Address**")
        h2.markdown("**🔌 Port**")
        h3.markdown("**🖥 Hostname**")

        st.markdown("---")

        for c in connected:
            c1, c2, c3 = st.columns([2, 2, 4])
            c1.code(c["ip"])
            c2.write(f"`{c['port']}`")
            c3.write(c["hostname"])

    st.markdown("---")
    st.caption(f"🏠 Local IP: **{get_local_ip()}**  |  Network: **{network}**  |  CPU: **{cpu}%**  |  RAM: **{ram}%**")