import streamlit as st

def show_cisco_map(cpu, ram, network):

    st.markdown("## 🌐 CISCO LIVE NETWORK MAP")

    col1, col2, col3, col4 = st.columns(4)

    # Router
    with col1:
        if network == "UP":
            st.success("📡 ROUTER 🟢 UP")
        else:
            st.error("📡 ROUTER 🔴 DOWN")

    # Switch
    with col2:
        if cpu < 90:
            st.success("🔀 SWITCH 🟢 NORMAL")
        else:
            st.error("🔀 SWITCH 🔴 OVERLOAD")

    # Server
    with col3:
        if ram < 90:
            st.success("🖥 SERVER 🟢 HEALTHY")
        else:
            st.error("🖥 SERVER 🔴 CRITICAL")
            # Client PC
    with col4:
         st.success("💻 PC1\n🟢 ONLINE")

    st.markdown("""
    ### Network Flow

    ```text
           INTERNET
               │
               ▼
         📡 ROUTER
               │
               ▼
         🔀 SWITCH
               │
       ┌───────┴───────┐
       ▼               ▼
    🖥 SERVER       💻 CLIENT
    ```
    """)

    health = round((cpu + ram) / 2)

    st.markdown("### Network Health")
    st.progress(health / 100)

    if health < 60:
        st.success(f"🟢 Network Health: {health}%")
    elif health < 85:
        st.warning(f"🟡 Network Health: {health}%")
    else:
        st.error(f"🔴 Network Health: {health}%")