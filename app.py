import psutil
import streamlit as st
import pandas as pd
import os
import platform
import time
import joblib
model = joblib.load("failure_model.pkl")
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from dashboard.components.alerts import show_alert
from dashboard.components.buzzer import start_buzzer, stop_buzzer
from dashboard.logger import log_data
from dashboard.components.cisco_map import show_cisco_map
from dashboard.components.networktopology_map import show_topology
from dashboard.components.lan_monitor import show_lan
from dashboard.components.project_ppt import show_project_ppt

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
    [
        "Dashboard",
        "LAN Monitoring",
        "Network Logs",
        "AI Analytics",
        "System Info",
        "Reports",
        "AI Assistant",
        "Project PPT"
    ]
)

# ================= HEADER =================
import streamlit.components.v1 as components

components.html("""
<style>
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.dot { animation: pulse 2s infinite; }
.dot2 { animation: pulse 2s infinite 0.6s; }
.dot3 { animation: pulse 2s infinite 1.2s; }
* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
body { background: transparent; }
</style>

<div style="border: 1px solid #e0e0e0; border-radius: 14px; padding: 1.5rem 2rem; background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%); margin-bottom: 1rem;">

  <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.8rem;">
    <div class="dot" style="width:8px;height:8px;border-radius:50%;background:#1D9E75;"></div>
    <div class="dot2" style="width:8px;height:8px;border-radius:50%;background:#378ADD;"></div>
    <div class="dot3" style="width:8px;height:8px;border-radius:50%;background:#D4537E;"></div>
    <span style="font-size:11px;color:#888;letter-spacing:0.08em;margin-left:4px;">● LIVE</span>
  </div>

  <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:1rem;">
    <div>
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
        <span style="font-size:28px;">🖧</span>
        <div>
          <div style="font-size:20px; font-weight:600; color:#1a1a2e; line-height:1.2;">AI-Based Network Monitoring & Self-Healing System</div>
          <div style="font-size:13px; color:#555; margin-top:2px;">⚡ Real-Time AI Network Intelligence Platform</div>
        </div>
      </div>
    </div>
    <div style="text-align:right;">
      <div id="clock" style="font-size:15px; font-weight:600; color:#1a1a2e; font-family:monospace;"></div>
      <div id="dateline" style="font-size:11px; color:#888; margin-top:2px;"></div>
    </div>
  </div>

  <div style="margin-top:1.2rem; padding-top:1rem; border-top:1px solid #dde3f0; display:grid; grid-template-columns:repeat(auto-fit, minmax(150px,1fr)); gap:12px;">
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="font-size:18px;">🎓</span>
      <div>
        <div style="font-size:10px; color:#888; text-transform:uppercase; letter-spacing:0.06em;">Institute</div>
        <div style="font-size:12px; font-weight:600; color:#1a1a2e;">Jetking Infotrain, Dadar</div>
      </div>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="font-size:18px;">🚀</span>
      <div>
        <div style="font-size:10px; color:#888; text-transform:uppercase; letter-spacing:0.06em;">Event</div>
        <div style="font-size:12px; font-weight:600; color:#1a1a2e;">TechFest 2026</div>
      </div>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="font-size:18px;">👨‍💻</span>
      <div>
        <div style="font-size:10px; color:#888; text-transform:uppercase; letter-spacing:0.06em;">Developer</div>
        <div style="font-size:12px; font-weight:600; color:#1a1a2e;">Sanad Haddadi</div>
      </div>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="font-size:18px;">📅</span>
      <div>
        <div style="font-size:10px; color:#888; text-transform:uppercase; letter-spacing:0.06em;">Date</div>
        <div style="font-size:12px; font-weight:600; color:#1a1a2e;">19 June 2026</div>
      </div>
    </div>
  </div>

</div>

<script>
function tick() {
  const now = new Date();
  document.getElementById('clock').textContent = now.toLocaleTimeString('en-IN', {hour:'2-digit',minute:'2-digit',second:'2-digit'});
  document.getElementById('dateline').textContent = now.toLocaleDateString('en-IN', {day:'2-digit',month:'long',year:'numeric'});
}
tick();
setInterval(tick, 1000);
</script>
""", height=230)

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

# ================= GLOBAL CPU/RAM =================
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

# ================= GLOBAL ALERT =================
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


# ================= BANDWIDTH FUNCTION =================
def get_bandwidth():
    net1 = psutil.net_io_counters()
    time.sleep(1)
    net2 = psutil.net_io_counters()
    upload = (net2.bytes_sent - net1.bytes_sent) / 1024
    download = (net2.bytes_recv - net1.bytes_recv) / 1024
    return round(upload, 2), round(download, 2)


# ================= DASHBOARD =================
if page == "Dashboard":
    st.success("🤖 AI ENGINE ACTIVE")
    st.success("🔧 SELF HEALING ENABLED")
    st.success("📡 LIVE NETWORK MONITORING")
    st.success("📧 EMAIL ALERT SYSTEM ACTIVE")
    st.success("🧠 AI FAILURE PREDICTION ENABLED")

    cpu = cpu_global
    ram = ram_global
    disk = psutil.disk_usage("C:\\").percent
    risk = risk_global
    prediction = prediction_global

    # ================= AI MODEL PREDICTION =================
    result = model.predict([[cpu_global, ram_global, 1 if network_status == "UP" else 0]])[0]

    if result == 0:
        st.success("🟢 AI Prediction: NORMAL")
    elif result == 1:
        st.warning("🟡 AI Prediction: WARNING")
    else:
        st.error("🔴 AI Prediction: FAILURE LIKELY")

    # ================= BANDWIDTH =================
    upload, download = get_bandwidth()

    st.markdown("## 🌐 LIVE BANDWIDTH")
    c1, c2 = st.columns(2)
    c1.metric("⬆ Upload KB/s", upload)
    c2.metric("⬇ Download KB/s", download)

    # ================= AI RISK SCORE =================
    risk_score = min(100, int((cpu_global + ram_global) / 2))

    st.markdown("## 🧠 AI RISK SCORE")
    st.metric("Risk", f"{risk_score}%")
    st.progress(risk_score / 100)

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


# ================= LAN MONITORING =================
elif page == "LAN Monitoring":
    show_lan()

# ================== projet ppt ==============
elif page == "Project PPT":
    show_project_ppt()
    
# ================= FOOTER =================
st.markdown("---")
import streamlit.components.v1 as components
components.html("""
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.dot { animation: pulse 2s infinite; }
</style>

<div style="border: 1px solid #e0e0e0; border-radius: 14px; padding: 1.2rem 2rem; background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%); text-align:center;">

  <div style="display:flex; align-items:center; justify-content:center; gap:6px; margin-bottom:8px;">
    <div class="dot" style="width:7px;height:7px;border-radius:50%;background:#1D9E75;"></div>
    <span style="font-size:13px; font-weight:600; color:#1a1a2e;">🖧 AI Network Monitor — TechFest 2026</span>
  </div>

  <div style="font-size:11px; color:#888; margin-bottom:10px;">
    Developed by <strong style="color:#378ADD;">Sanad Haddadi</strong> &nbsp;|&nbsp;
    Jetking Infotrain Ltd, Dadar, Mumbai &nbsp;|&nbsp;
    19 June 2026
  </div>

  <div style="display:flex; justify-content:center; gap:20px; flex-wrap:wrap;">
    <span style="font-size:11px; color:#1D9E75;">✅ AI Engine Active</span>
    <span style="font-size:11px; color:#378ADD;">📡 Live Monitoring</span>
    <span style="font-size:11px; color:#D4537E;">🔧 Self-Healing Enabled</span>
    <span style="font-size:11px; color:#BA7517;">🧠 Failure Prediction ON</span>
  </div>

  <div style="margin-top:10px; font-size:10px; color:#aaa;">
    © 2026 Sanad Haddadi. Built with Python, Streamlit & AI.
  </div>

</div>
""", height=130)
