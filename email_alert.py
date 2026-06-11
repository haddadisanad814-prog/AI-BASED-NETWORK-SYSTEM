import smtplib
from email.mime.text import MIMEText

SENDER_EMAIL = "haddadisanad814@gmail.com"
APP_PASSWORD = "iaqx cbqb ulnb zhle"
RECEIVER_EMAIL = "haddadisanad814@gmail.com"

def send_alert(network_status, cpu_usage, memory_usage, prediction, reason):

    try:
        message = f"""
AI NETWORK ALERT SYSTEM

Reason: {reason}

--------------------------------
Network Status : {network_status}
CPU Usage      : {cpu_usage}%
Memory Usage   : {memory_usage}%
AI Prediction   : {prediction}
--------------------------------

System Monitoring Alert Triggered
"""

        msg = MIMEText(message)
        msg["Subject"] = "⚠ AI Network Full System Alert"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        print("Email Alert Sent ✔")

    except Exception as e:
        print("Email Failed ❌")
        print(e)