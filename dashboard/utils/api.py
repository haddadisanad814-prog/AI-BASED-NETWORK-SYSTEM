import streamlit as st
import psutil
import time

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1000, key="refresh")

st.title("🏠 NOC LIVE DASHBOARD")

# session state for history
if "cpu_history" not in st.session_state:
    st.session_state.cpu_history = []

if "mem_history" not in st.session_state:
    st.session_state.mem_history = []

# live data
cpu = psutil.cpu_percent()
mem = psutil.virtual_memory().percent

st.session_state.cpu_history.append(cpu)
st.session_state.mem_history.append(mem)

# limit data
st.session_state.cpu_history = st.session_state.cpu_history[-20:]
st.session_state.mem_history = st.session_state.mem_history[-20:]

col1, col2 = st.columns(2)

with col1:
    st.subheader("CPU Usage")
    st.line_chart(st.session_state.cpu_history)

with col2:
    st.subheader("Memory Usage")
    st.line_chart(st.session_state.mem_history)

st.success(f"CPU: {cpu}% | MEMORY: {mem}%")

time.sleep(1)
st.rerun()