import csv
import os

def calculate_sla():

    file_path = "network_logs.csv"

    if not os.path.exists(file_path):
        return 100, 0, 0

    total = 0
    down = 0

    with open(file_path, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            total += 1

            if row["Network Status"] == "DOWN":
                down += 1

    if total == 0:
        return 100, 0, 0

    uptime = total - down

    sla = (uptime / total) * 100
    return round(sla, 2), uptime, down