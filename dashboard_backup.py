import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Network Monitoring Dashboard")

st.title("AI-Based Network Failure Prediction System")

try:
    data = pd.read_csv("network_logs.csv")

    st.subheader("Network Logs")
    st.dataframe(data)

    st.subheader("CPU Usage")
    st.line_chart(data["CPU Usage"])

    st.subheader("Memory Usage")
    st.line_chart(data["Memory Usage"])

    st.success("Dashboard Running Successfully")

except Exception as e:
    st.error(f"Error: {e}")