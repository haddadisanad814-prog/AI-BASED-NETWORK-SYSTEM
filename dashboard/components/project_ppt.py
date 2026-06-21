import streamlit as st


def show_project_ppt():

    slides = [
        {
            "title": "AI Network Monitoring & Self-Healing System",
            "content": """
### TechFest 2026 Project

**Developer:** Sanad Haddadi

**Institute:** Jetking Infotrain Ltd, Dadar

**Real-Time AI Network Intelligence Platform**
"""
        },
        {
            "title": "Problem Statement",
            "content": """
### Current Network Problems

- Manual monitoring
- Delayed failure detection
- No predictive analysis
- Long downtime
- Human dependency
- Poor visibility of LAN devices

### Goal

Create an AI-based system that detects, predicts and heals failures automatically.
"""
        },
        {
            "title": "System Architecture",
            "content": """
### Flow

    Internet -> Router -> Switch
    -> Servers / PCs / Printers
    -> AI Monitoring Engine
    -> Failure Prediction
    -> Self-Healing Module
    -> Email Alerts + Dashboard
"""
        },
        {
            "title": "LAN Monitoring",
            "content": """
### Features

- Automatic Device Discovery
- IP Address Detection
- MAC Address Detection
- Hostname Detection
- Device Inventory
- Live Topology Map
- Real-Time Monitoring
"""
        },
        {
            "title": "AI Failure Prediction",
            "content": """
### AI Monitors

- CPU Usage
- RAM Usage
- Ping / Latency
- Network Status

### Prediction Levels

- GREEN  - Normal
- YELLOW - Warning
- RED    - Failure Likely

Model predicts issues before downtime occurs.
"""
        },
        {
            "title": "Self-Healing Engine",
            "content": """
### Automatic Recovery Actions

- Restart Network Services
- Flush DNS Cache
- Renew IP Address (DHCP)
- Reset Network Adapters
- Clear ARP Cache
- Verify Connectivity After Heal

No manual intervention required.
"""
        },
        {
            "title": "Dashboard Features",
            "content": """
### Live Dashboard Includes

- CPU / RAM / Risk Graphs
- Ping Graph
- Email Alerts
- Buzzer Alerts
- PDF Reports
- AI Assistant Chat
- SLA Monitor
- Device Inventory Table
"""
        },
        {
            "title": "Future Scope",
            "content": """
### Planned Improvements

- Cisco SNMP Integration
- WAN & Multi-Site Monitoring
- Cloud Dashboard (AWS / Azure)
- Mobile App
- WhatsApp Alerts via Twilio
- Auto Ticket Generation (Jira)
- AI Root Cause Analysis
"""
        },
        {
            "title": "Thank You",
            "content": """
### Developed By

**Sanad Haddadi**

Jetking Infotrain Ltd, Dadar, Mumbai

TechFest 2026

---

Questions & Discussion Welcome
"""
        },
    ]

    if "slide_no" not in st.session_state:
        st.session_state.slide_no = 0

    slide = slides[st.session_state.slide_no]

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #0f172a, #1e293b);
            padding: 40px;
            border-radius: 20px;
            min-height: 420px;
            color: white;
            text-align: center;
            border: 1px solid rgba(59,130,246,0.3);
        ">
            <div style="font-size:11px;letter-spacing:3px;color:#3b82f6;
                        margin-bottom:16px;font-family:monospace;">
                SLIDE {st.session_state.slide_no + 1} / {len(slides)}
            </div>
            <h1 style="color:#ffffff;font-size:32px;
                       text-shadow:0 0 20px rgba(59,130,246,0.5);">
                {slide['title']}
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")
    st.markdown(slide["content"])
    st.markdown("---")

    c1, c2, c3 = st.columns([1, 2, 1])

    with c1:
        if st.button("Previous", key="prev_btn"):
            if st.session_state.slide_no > 0:
                st.session_state.slide_no -= 1
                st.rerun()

    with c2:
        st.markdown(
            f"<h4 style='text-align:center;color:#3b82f6;'>"
            f"Slide {st.session_state.slide_no + 1} / {len(slides)}"
            f"</h4>",
            unsafe_allow_html=True
        )

    with c3:
        if st.button("Next", key="next_btn"):
            if st.session_state.slide_no < len(slides) - 1:
                st.session_state.slide_no += 1
                st.rerun()
