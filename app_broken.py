import psutil
import streamlit as st
import pandas as pd
import os
import platform
from datetime import datetime

time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
from streamlit_autorefresh import st_autorefresh
from dashboard.components.alerts import show_alert
from dashboard.components.buzzer import start_buzzer, stop_buzzer
from dashboard.logger import log_data

# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI NOC Dashboard", layout="wide")

st.sidebar.title("🖧 CONTROL PANEL")
page = st.sidebar.radio("Navigation",
                        ["Dashboard", "Network Logs", "AI Analytics", "System Info"])

# ================= HEADER =================
st.markdown("""
# 🖧 AI NOC DASHBOARD
### 👨‍💻 SANAD HADDADI
### 📅 12 JUNE 2026
---
""")

st.info(f"🕒 {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# ================= AUTO REFRESH =================
st_autorefresh(interval=5000, key="refresh")

# ================= SESSION STATE =================
for key in ["cpu", "ram", "risk", "ping", "alerts"]:
    if key not in st.session_state:
        st.session_state[key] = []

# ================= CONNECTION =================
def get_connection_type():
    stats = psutil.net_if_stats()
    for i, s in stats.items():
        if s.isup:
            if "wi-fi" in i.lower() or "wlan" in i.lower():
                return "WIRELESS 📶"
            if "eth" in i.lower():
                return "WIRED 🔌"
    return "UNKNOWN"

connection_type = get_connection_type()

# ================= PING =================
def get_ping():
    try:
        if platform.system().lower() == "windows":
            cmd = "ping 8.8.8.8 -n 1"
        else:
            cmd = "ping 8.8.8.8 -c 1"

        out = os.popen(cmd).read()

        if "time=" in out:
            return float(out.split("time=")[1].split("ms")[0])
        return 0
    except:
        return 0

# ================= NETWORK =================
net = os.system("ping 8.8.8.8 -n 1 > nul")
network_status = "UP" if net == 0 else "DOWN"

ping = get_ping()

st.session_state.ping.append(ping)
st.session_state.ping = st.session_state.ping[-20:]
# ================= DASHBOARD =================
if page == "Dashboard":

    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("C:\\").percent

    risk = (cpu + ram) / 2

    prediction = "NORMAL"

    if network_status == "DOWN":
        prediction = "NETWORK FAILURE"

    elif cpu > 90:
        prediction = "CPU OVERLOAD"

    elif ram > 90:
        prediction = "MEMORY OVERLOAD"

# ================= LOGGING =================
       log_data(
    time_now,
    network_status,
    cpu,
    ram,
    prediction,
    round(risk, 2)
)
    st.session_state.cpu.append(cpu)
    st.session_state.ram.append(ram)
    st.session_state.risk.append(risk)

    st.session_state.cpu = st.session_state.cpu[-20:]
    st.session_state.ram = st.session_state.ram[-20:]
    st.session_state.risk = st.session_state.risk[-20:]

    # ================= ALERT =================
    if network_status == "DOWN":
        show_alert("🚨 NETWORK DOWN 🚨")

    elif cpu > 90:
        show_alert("🚨 CPU HIGH 🚨")

    elif ram > 90:
        show_alert("🚨 RAM HIGH 🚨")

    # ================= METRICS =================
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("CPU", f"{cpu}%")
    col2.metric("RAM", f"{ram}%")
    col3.metric("DISK", f"{disk}%")
    col4.metric("NETWORK", network_status)
    col5.metric("CONNECTION", connection_type)

    # ================= SYSTEM GRAPH =================
    st.markdown("## 📊 SYSTEM GRAPH")

    st.line_chart(pd.DataFrame({
        "cpu": st.session_state.cpu,
        "ram": st.session_state.ram,
        "risk": st.session_state.risk
    }))

    # ================= PING GRAPH =================
    st.markdown("## 📡 PING (ms)")

    st.line_chart(pd.DataFrame({
        "ping": st.session_state.ping
    }))

    # ================= NETWORK SCORE =================
    smart_score = max(0, 100 - int(ping))

    st.markdown("## 🌐 NETWORK SCORE")

    score1, score2 = st.columns(2)

    score1.metric("Ping", f"{ping} ms")
    score2.metric("Score", f"{smart_score}%")

    st.progress(smart_score / 100)

    # ================= BUZZER =================
    critical = (
        network_status == "DOWN"
        or cpu > 90
        or ram > 90
    )

    if critical:
        start_buzzer()
    else:
        stop_buzzer()

    # ================= STATUS =================
    if network_status == "DOWN":
        st.error("🔴 NETWORK DOWN")

    elif cpu > 90:
        st.error("🔥 CPU HIGH")

    elif ram > 90:
        st.error("🔥 RAM HIGH")

    else:
        st.success("🟢 SYSTEM HEALTHY")