import streamlit as st

def show_alert(message):

    st.markdown(
        f"""
        <div style="
            background:red;
            color:white;
            padding:15px;
            font-size:24px;
            font-weight:bold;
            text-align:center;
            border-radius:10px;
        ">
        🚨 {message} ALERT 🚨
        </div>
        """,
        unsafe_allow_html=True
    )