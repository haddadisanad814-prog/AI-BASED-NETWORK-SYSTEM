import csv
from datetime import datetime

def log_data(network_status, cpu_usage, memory_usage, prediction, risk):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("network_logs.csv", "a", newline="") as file:

        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow([
                "Time",
                "Network Status",
                "CPU Usage",
                "Memory Usage",
                "AI Prediction",
                "Risk"
            ])

        writer.writerow([
            current_time,
            network_status,
            cpu_usage,
            memory_usage,
            prediction,
            risk
        ])