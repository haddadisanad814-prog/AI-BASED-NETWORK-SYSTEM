import os
import platform
import psutil
from logger import log_data
from datetime import datetime

print("===== Network Monitoring =====")

# Network Check
if platform.system().lower() == "windows":
    response = os.system("ping 8.8.8.8 -n 1 > nul")
else:
    response = os.system("ping 8.8.8.8 -c 1 > /dev/null")

network_status = "UP" if response == 0 else "DOWN"

# CPU Usage
cpu_usage = psutil.cpu_percent(interval=1)

# Memory Usage
memory_usage = psutil.virtual_memory().percent

# Time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Print output
print(f"Network Status : {network_status}")
print(f"CPU Usage      : {cpu_usage}%")
print(f"Memory Usage   : {memory_usage}%")
print(f"Time           : {current_time}")

# Log data (IMPORTANT)
log_data(network_status, cpu_usage, memory_usage)