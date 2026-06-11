import streamlit as st
import pandas as pd
from utils.graphs import get_live_metrics

st.title("🔥 NETWORK CONTROL DASHBOARD")

data = get_live_metrics()

df = pd.DataFrame({
    "Metric": ["CPU", "Memory"],
    "Usage": [data["cpu"], data["memory"]]
})

st.bar_chart(df.set_index("Metric"))

if data["cpu"] > 85:
    st.error("🚨 CPU HIGH")
if data["memory"] > 85:
    st.error("🚨 MEMORY HIGH")