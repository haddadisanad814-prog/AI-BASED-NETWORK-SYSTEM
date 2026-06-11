import csv
from datetime import datetime

def log_failure(cpu, memory, risk):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("failure_history.csv", "a", newline="") as file:

        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow([
                "Time",
                "CPU",
                "Memory",
                "Risk"
            ])

        writer.writerow([
            current_time,
            cpu,
            memory,
            risk
        ])