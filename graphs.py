import psutil
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="NOC LIVE MONITOR", layout="wide")

st.title("🖧 AI NOC LIVE SYSTEM MONITOR")

# auto refresh
st_autorefresh(interval=1000, key="refresh")

# history init
if "cpu_history" not in st.session_state:
    st.session_state.cpu_history = []

if "ram_history" not in st.session_state:
    st.session_state.ram_history = []

# metrics
cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage("/").percent

# store history
st.session_state.cpu_history.append(cpu)
st.session_state.ram_history.append(ram)

st.session_state.cpu_history = st.session_state.cpu_history[-30:]
st.session_state.ram_history = st.session_state.ram_history[-30:]

# layout
col1, col2, col3 = st.columns(3)

col1.metric("CPU Usage", f"{cpu}%")
col2.metric("RAM Usage", f"{ram}%")
col3.metric("DISK Usage", f"{disk}%")

# graphs
df = pd.DataFrame({
    "time": list(range(len(st.session_state.cpu_history))),
    "cpu": st.session_state.cpu_history,
    "ram": st.session_state.ram_history
})

st.line_chart(df.set_index("time"))

# status logic
if cpu > 80 or ram > 80:
    st.error("🚨 SYSTEM WARNING - HIGH LOAD DETECTED")
elif cpu > 90:
    st.error("🔥 CRITICAL SYSTEM LOAD")
else:
    st.success("🟢 SYSTEM HEALTHY")