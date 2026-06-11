import streamlit as st

def login():

    st.title("🔐 NOC LOGIN")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if user == "admin" and pwd == "admin":
        st.success("Login Success")
        return True

    st.warning("Enter credentials")
    return False