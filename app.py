import psutil
import streamlit as st
import pandas as pd
import os
import platform
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from dashboard.components.alerts import show_alert
from dashboard.components.buzzer import start_buzzer, stop_buzzer
from dashboard.logger import log_data
from dashboard.components.cisco_map import show_cisco_map
from dashboard.components.networktopology_map import show_topology

from auth import login
from email_alert import send_alert
from self_healing import run_healing
from sla_monitor import calculate_sla
from report_pdf import generate_pdf_report
from chat_assistant import handle_query
from summary_generator import generate_summary

time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI NOC Dashboard", layout="wide")

# ================= LOGIN SYSTEM =================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 AI NOC Dashboard - Login")
    st.caption("Please login to continue")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        role = login(username, password)
        if role:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = role
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.stop()

# ================= SIDEBAR =================
st.sidebar.title("🖧 CONTROL PANEL")
st.sidebar.markdown(
    f"👤 **{st.session_state['username']}**  \nRole: `{st.session_state['role']}`"
)
if st.sidebar.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Network Logs", "AI Analytics", "System Info", "Reports", "AI Assistant"]
)

# ================= HEADER =================
st.markdown("""
# 🖧 AI-Based Network Monitoring & Self-Healing System
### ⚡ Real-Time AI Network Intelligence Platform
### 🎓 Training Institute: Jetking Infotrain Ltd, Dadar (Mumbai)
### 🚀 TechFest 2026 Project Showcase
### 👨‍💻 Developer: Sanad Haddadi
### 📅 12 June 2026
---
""")

st.info(f"🕒 {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# ================= AUTO REFRESH =================
st_autorefresh(interval=5000, key="refresh")

# ================= SESSION STATE =================
for key in ["cpu", "ram", "risk", "ping", "alerts"]:
    if key not in st.session_state:
        st.session_state[key] = []

if "last_alert_time" not in st.session_state:
    st.session_state["last_alert_time"] = 0

if "last_heal_time" not in st.session_state:
    st.session_state["last_heal_time"] = 0

ALERT_COOLDOWN = 60   # seconds - email alert max once per minute
HEAL_COOLDOWN = 60    # seconds - self healing max once per minute


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
connection_type = get_connection_type()

st.session_state.ping.append(ping)
st.session_state.ping = st.session_state.ping[-20:]

# ================= GLOBAL CPU/RAM (har page ke liye) =================
cpu_global = psutil.cpu_percent(interval=0.1)
ram_global = psutil.virtual_memory().percent
risk_global = (cpu_global + ram_global) / 2

# ================= GLOBAL PREDICTION =================
prediction_global = "NORMAL"
if network_status == "DOWN":
    prediction_global = "NETWORK FAILURE"
elif cpu_global > 90:
    prediction_global = "CPU OVERLOAD"
elif ram_global > 90:
    prediction_global = "MEMORY OVERLOAD"

# ================= GLOBAL ALERT (har page pe dikhega) =================
if network_status == "DOWN":
    show_alert("NETWORK FAILURE DETECTED - AI RECOVERY MODE ACTIVE")
elif cpu_global > 90:
    show_alert("CPU OVERLOAD - SYSTEM STABILIZING")
elif ram_global > 90:
    show_alert("MEMORY PRESSURE HIGH - OPTIMIZING")

# ================= GLOBAL BUZZER + EMAIL + SELF HEALING =================
critical = (network_status == "DOWN" or cpu_global > 90 or ram_global > 90)
now_ts = time.time()

if critical:
    start_buzzer()

    # ---------- EMAIL ALERT (with cooldown) ----------
    if now_ts - st.session_state["last_alert_time"] > ALERT_COOLDOWN:
        reasons = []
        if network_status == "DOWN":
            reasons.append("Network Down")
        if cpu_global > 90:
            reasons.append("CPU Overload")
        if ram_global > 90:
            reasons.append("Memory Overload")

        send_alert(
            network_status,
            cpu_global,
            ram_global,
            prediction_global,
            ", ".join(reasons)
        )
        st.session_state["last_alert_time"] = now_ts

    # ---------- SELF HEALING (with cooldown) ----------
    if now_ts - st.session_state["last_heal_time"] > HEAL_COOLDOWN:
        run_healing(network_status, cpu_global, ram_global, failure_risk=risk_global)
        st.session_state["last_heal_time"] = now_ts

else:
    stop_buzzer()


# ================= DASHBOARD =================
if page == "Dashboard":

    cpu = cpu_global
    ram = ram_global
    disk = psutil.disk_usage("C:\\").percent
    risk = risk_global
    prediction = prediction_global

    # ================= AUTO HEAL STATUS DISPLAY =================
    if cpu > 90:
        st.info("🔧 CPU HEAL ACTIVE")
    if ram > 90:
        st.info("🔧 RAM HEAL ACTIVE")
    if network_status == "DOWN":
        st.info("🔧 NETWORK HEAL ACTIVE")

    # ================= LOGGING =================
    log_data(time_now, network_status, cpu, ram, prediction, round(risk, 2))

    st.session_state.cpu.append(cpu)
    st.session_state.ram.append(ram)
    st.session_state.risk.append(risk)

    st.session_state.cpu = st.session_state.cpu[-20:]
    st.session_state.ram = st.session_state.ram[-20:]
    st.session_state.risk = st.session_state.risk[-20:]

    # ================= METRICS =================
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("CPU", f"{cpu}%")
    col2.metric("RAM", f"{ram}%")
    col3.metric("DISK", f"{disk}%")
    col4.metric("NETWORK", network_status)
    col5.metric("CONNECTION", connection_type)

    # ================= WARNING PANEL =================
    st.markdown("## ⚠️ AI WARNING PANEL")
    warnings = []
    if network_status == "DOWN":
        warnings.append("Network Down")
    if cpu > 90:
        warnings.append("CPU High")
    if ram > 90:
        warnings.append("Memory High")

    if len(warnings) == 0:
        st.success("🟢 All Systems Normal")
    else:
        for w in warnings:
            st.error(f"🔴 {w}")

    # ================= SYSTEM GRAPH =================
    st.markdown("## 📊 SYSTEM GRAPH")
    st.line_chart(pd.DataFrame({
        "cpu": st.session_state.cpu,
        "ram": st.session_state.ram,
        "risk": st.session_state.risk
    }))

    # ================= PING GRAPH =================
    st.markdown("## 📡 PING (ms)")
    st.line_chart(pd.DataFrame({"ping": st.session_state.ping}))

    # ================= NETWORK SCORE =================
    smart_score = max(0, 100 - int(ping))
    st.markdown("## 🌐 NETWORK SCORE")
    score1, score2 = st.columns(2)
    score1.metric("Ping", f"{ping} ms")
    score2.metric("Score", f"{smart_score}%")
    st.progress(smart_score / 100)

    # ================= AI SYSTEM HEALTH =================
    health = max(0, 100 - int(risk))
    st.markdown("## 🧠 AI SYSTEM HEALTH STATUS")
    if health > 80:
        st.success(f"🟢 SYSTEM HEALTHY ({health}%)")
    elif health > 50:
        st.warning(f"🟡 SYSTEM STABLE ({health}%)")
    else:
        st.error(f"🔴 SYSTEM CRITICAL ({health}%)")
    st.progress(health / 100)

    # ================= STATUS =================
    if network_status == "DOWN":
        st.error("🔴 NETWORK DOWN")
    elif cpu > 90:
        st.error("🔥 CPU HIGH")
    elif ram > 90:
        st.error("🔥 RAM HIGH")
    else:
        st.success("🟢 SERVER HEALTHY")

    # ================= NETWORK TOPOLOGY =================
    show_topology(cpu, ram, network_status)

    # ================= CISCO MAP =================
    st.markdown("## 🌐 LIVE NETWORK FLOW STATUS")
    st.write("📡 Internet ➝ Router ➝ Switch ➝ Server ➝ Client")
    st.progress(100 if network_status == "UP" else 40)


# ================= NETWORK LOGS =================
elif page == "Network Logs":
    st.header("📄 Network Logs")
    try:
        logs = pd.read_csv("network_logs.csv")
        st.dataframe(logs, use_container_width=True)
    except:
        st.warning("No logs found")


# ================= AI ANALYTICS =================
elif page == "AI Analytics":
    st.header("🤖 AI Analytics")
    if len(st.session_state.risk) > 0:
        st.line_chart(pd.DataFrame({"Risk": st.session_state.risk}))
    else:
        st.info("Not enough data yet. Visit Dashboard page first.")


# ================= SYSTEM INFO =================
elif page == "System Info":
    st.header("💻 System Information")
    st.write("CPU Usage:", psutil.cpu_percent())
    st.write("RAM Usage:", psutil.virtual_memory().percent)
    st.write("Disk Usage:", psutil.disk_usage("C:\\").percent)
    st.write("Network Status:", network_status)

    st.markdown("---")
    st.markdown("## 📋 Daily Summary")
    st.code(generate_summary())


# ================= REPORTS =================
elif page == "Reports":
    st.header("📊 SLA & Reports")

    sla, uptime, down = calculate_sla()

    c1, c2, c3 = st.columns(3)
    c1.metric("SLA %", f"{sla}%")
    c2.metric("Uptime Records", uptime)
    c3.metric("Downtime Records", down)

    st.markdown("---")
    st.markdown("### 📄 Generate PDF Report")

    report_type = st.selectbox("Report Type", ["daily", "weekly", "monthly"])

    if st.button("Generate PDF"):
        filename = generate_pdf_report(report_type)
        with open(filename, "rb") as f:
            st.download_button(
                label="⬇️ Download Report",
                data=f,
                file_name=filename,
                mime="application/pdf"
            )
        st.success(f"✅ Report generated: {filename}")


# ================= AI ASSISTANT =================
elif page == "AI Assistant":
    st.header("🤖 AI Network Assistant")
    st.caption("Ask about network status, server status, system health, etc.")

    user_input = st.text_input("Type your question here...")

    if st.button("Ask"):
        if user_input.strip():
            result = handle_query(user_input)
            st.markdown(result["response"])
        else:
            st.warning("Please type a question first.")