import time
import os
import platform
import psutil
import pandas as pd
import joblib
import subprocess
import re

from logger import log_data
from email_alert import send_alert
from self_healing import run_healing
from failure_logger import log_failure
from system_status import status
from chat_assistant import handle_query
from chat_ai import ai_brain
from report_pdf import generate_pdf_report
from database import insert_log
from failure_simulator import simulate_failure
from sla_monitor import calculate_sla
from network_detector import get_device_status
from alert_sound import play_alarm


# ---------------- ROOT CAUSE ----------------
def get_root_cause(cpu_usage, memory_usage, latency, disk_usage):
    reasons = []

    if cpu_usage > 80:
        reasons.append("High CPU Usage")

    if memory_usage > 80:
        reasons.append("High Memory Usage")

    if latency > 100:
        reasons.append("High Network Latency")

    if disk_usage > 90:
        reasons.append("Disk Almost Full")

    if len(reasons) == 0:
        reasons.append("System Stable")

    return reasons


def predict_future_risk(current_risk):
    return min(current_risk + 10, 95), min(current_risk + 20, 95)


# ---------------- TOPLOGY ----------------
def update_topology(cpu_usage, memory_usage, failure_risk, network_status, prediction_text):

    status["PC1"] = "warning" if cpu_usage > 80 else "healthy"

    if failure_risk > 85 or prediction_text == "Failure":
        status["Server"] = "failure"
    elif memory_usage > 85:
        status["Server"] = "warning"
    else:
        status["Server"] = "healthy"

    status["Router"] = "healthy"
    status["Switch"] = "healthy" if network_status == "UP" else "failure"


# ---------------- LATENCY ----------------
def get_latency():
    try:
        output = subprocess.check_output(
            "ping 8.8.8.8 -n 1",
            shell=True,
            text=True
        )

        match = re.search(r"time[=<](\d+)ms", output)
        return int(match.group(1)) if match else 0

    except:
        return 0


print("===== LIVE MONITOR STARTED =====")

model = joblib.load("failure_model.pkl")

last_alert_time = 0
ALERT_COOLDOWN = 60


# ================= MAIN LOOP =================
while True:

    print("\n-----")

    # NETWORK CHECK
    if platform.system().lower() == "windows":
        response = os.system("ping 8.8.8.8 -n 1 > nul")
    else:
        response = os.system("ping 8.8.8.8 -c 1 > /dev/null")

    network_status = "UP" if response == 0 else "DOWN"

    net_info = get_device_status()

    router_status = net_info["Router"]
    switch_status = net_info["Switch"]
    network_type = net_info["Network_Type"]
    internet_status = net_info["Internet"]

    # SYSTEM STATS
    latency = get_latency()
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory_usage = psutil.virtual_memory().percent

    disk_path = "C:\\" if os.name == "nt" else "/"
    disk_usage = psutil.disk_usage(disk_path).percent

    # ROOT CAUSE
    reasons = get_root_cause(cpu_usage, memory_usage, latency, disk_usage)

    # AI INPUT
    test_data = pd.DataFrame([{
        "CPU Usage": cpu_usage,
        "Memory Usage": memory_usage
    }])

    prediction = model.predict(test_data)[0]
    prediction_text = "Normal" if prediction == 0 else "Failure"

    try:
        probability = model.predict_proba(test_data)[0]
        failure_risk = max(5, min(float(probability[1]) * 100, 95))
    except:
        failure_risk = 0

    # SLA
    sla, uptime, downtime = calculate_sla()

    # FUTURE RISK
    future30, future60 = predict_future_risk(failure_risk)

    # TOPLOGY UPDATE
    update_topology(cpu_usage, memory_usage, failure_risk, network_status, prediction_text)
    status["Router"] = router_status
    status["Switch"] = switch_status

    # LOGGING
    insert_log(network_status, cpu_usage, memory_usage, prediction_text, round(failure_risk, 2))

    # OUTPUT
    print(f"Network : {network_status}")
    print(f"Latency : {latency} ms")
    print(f"CPU     : {cpu_usage}%")
    print(f"Memory  : {memory_usage}%")
    print(f"Disk    : {disk_usage}%")
    print(f"AI Pred : {prediction_text}")
    print(f"Risk    : {round(failure_risk, 2)}%")

    print(f"Forecast 30 Min : {future30}%")
    print(f"Forecast 1 Hour : {future60}%")

    print(f"SLA     : {sla}%")
    print(f"Uptime  : {uptime}")
    print(f"Downtime: {downtime}")

    print(f"Internet : {internet_status}")
    print(f"Network  : {network_type}")
    print(f"Router   : {router_status}")
    print(f"Switch   : {switch_status}")

    print("Root Cause:")
    for r in reasons:
        print("-", r)

       # HEALING
    run_healing(network_status, cpu_usage, memory_usage)

    # FAILURE LOG
    if prediction_text == "Failure" or failure_risk > 85 or network_status == "DOWN":
        log_failure(cpu_usage, memory_usage, round(failure_risk, 2))

    # 🚨 CRITICAL ALERT CHECK
    critical_alert = (
        network_status == "DOWN"
        or cpu_usage > 90
        or memory_usage > 90
        or failure_risk > 85
        or prediction_text == "Failure"
    )

    # 🚨 ALARM SOUND
    if critical_alert:
        print("🚨 CRITICAL ALERT DETECTED 🚨")
        play_alarm()

    # EMAIL ALERT
    current_time = time.time()

    if failure_risk > 85 and (current_time - last_alert_time > ALERT_COOLDOWN):
        send_alert(
            network_status,
            cpu_usage,
            memory_usage,
            prediction_text,
            f"⚠ HIGH RISK DETECTED ({round(failure_risk, 2)}%)"
        )

        last_alert_time = current_time

    
    # CHAT
    try:
        user_input = input("\nAsk AI Assistant (Enter skip): ")
        if user_input.strip():
            result = handle_query(user_input)
            print("\n🤖 AI:", result["response"])
    except:
        pass

    # REPORTS
    current_minute = time.localtime().tm_min

    if current_minute == 0:
        print("📄 Daily Report:", generate_pdf_report("daily"))

    if current_minute == 10:
        print("📄 Weekly Report:", generate_pdf_report("weekly"))

    if current_minute == 20:
        print("📄 Monthly Report:", generate_pdf_report("monthly"))

    time.sleep(5)