import os
import psutil
import platform
import csv
from datetime import datetime

from healing_memory import save_memory, get_best_action, init_memory

print("===== SELF HEALING ENGINE STARTED =====")

# ❌ SAFE PROCESSES
SAFE_PROCESSES = {
    "System Idle Process",
    "System",
    "svchost.exe",
    "explorer.exe"
}

# 🛡 SAFE PROCESS CHECK
def is_safe_process(name):

    SAFE_KEYWORDS = [
        "system", "svchost", "explorer", "wininit",
        "csrss", "services", "lsass", "idle"
    ]

    if not name:
        return True

    name = name.lower()

    for keyword in SAFE_KEYWORDS:
        if keyword in name:
            return True

    return False


# 🚨 THREAT SCORE
def threat_score(name, cpu, memory):

    score = 0

    if not name:
        return 0

    name = name.lower()

    suspicious_keywords = [
        "miner", "crypto", "trojan", "worm",
        "rat", "keylog", "payload", "hack", "inject"
    ]

    for word in suspicious_keywords:
        if word in name:
            score += 60

    if cpu > 80:
        score += 20

    if memory > 80:
        score += 20

    return min(score, 100)


# 📁 LOG
def log_healing(action):

    file_path = "healing_logs.csv"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, "a", newline="") as file:
        writer = csv.writer(file)

        if os.path.exists(file_path) and os.stat(file_path).st_size == 0:
            writer.writerow(["Time", "Healing Action"])

        writer.writerow([current_time, action])


# 🌐 NETWORK HEAL
def heal_network():

    print("🔧 Fixing Network...")

    try:
        if platform.system().lower() == "windows":
            os.system("ipconfig /release")
            os.system("ipconfig /renew")
        else:
            os.system("sudo dhclient -r")
            os.system("sudo dhclient")

        log_healing("Network Healing")
        save_memory("NETWORK_DOWN", "NETWORK_RESET", 1)

        print("✅ Network Healing Done")

    except Exception as e:
        print("❌ Network Heal Error:", e)


# 💻 CPU HEAL (AI + LEARNING)
def heal_cpu():

    print("🛡 CPU SMART HEAL ACTIVE")

    killed_count = 0

    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):

            try:
                name = proc.info['name']
                cpu = proc.info['cpu_percent'] or 0

                if name and not is_safe_process(name):

                    score = threat_score(name, cpu, 0)

                    if score >= 70 or cpu > 85:

                        print(f"🚨 KILLING: {name} | Score: {score}")

                        psutil.Process(proc.info['pid']).terminate()

                        killed_count += 1

            except:
                pass

        log_healing("CPU Healing")

        # 🧠 LEARNING SAVE
        save_memory("CPU_HIGH", "KILL_PROCESS", 1)

        print(f"🧠 Killed Processes: {killed_count}")
        print("✅ CPU Healing Done")

    except Exception as e:
        print("❌ CPU Heal Error:", e)


# 🧠 MEMORY HEAL
def heal_memory():

    print("🔧 Memory cleanup running...")

    try:
        if platform.system().lower() == "windows":
            os.system("echo Memory cleanup triggered")
        else:
            os.system("sync; echo 3 | sudo tee /proc/sys/vm/drop_caches")

        log_healing("Memory Healing")

        # 🧠 LEARNING SAVE
        save_memory("MEMORY_HIGH", "CLEAR_CACHE", 1)

        print("✅ Memory Healing Done")

    except Exception as e:
        print("❌ Memory Heal Error:", e)


# 🧠 SMART AI DECISION ENGINE (LEARNING ENABLED)
def ai_decision_engine(cpu_usage, memory_usage, network_status, failure_risk):

    actions = []

    # 🧠 FIRST CHECK MEMORY (LEARNED FIX)
    if network_status == "DOWN":
        actions.append("NETWORK_HEAL")

    if cpu_usage > 90:
        actions.append("CPU_EMERGENCY")

    elif cpu_usage > 80:
        actions.append("CPU_WARNING")

    if memory_usage > 90:
        actions.append("MEMORY_EMERGENCY")

    elif memory_usage > 80:
        actions.append("MEMORY_WARNING")

    if failure_risk > 85:
        actions.append("FULL_RECOVERY_MODE")

    return actions


# 🚀 MAIN CONTROLLER (FINAL AI SYSTEM)
def run_healing(network_status, cpu_usage, memory_usage, failure_risk=0):

    try:
        init_memory()

        actions = ai_decision_engine(cpu_usage, memory_usage, network_status, failure_risk)

        for action in actions:

            if action == "NETWORK_HEAL":
                heal_network()

            elif action == "CPU_EMERGENCY":
                heal_cpu()

            elif action == "MEMORY_EMERGENCY":
                heal_memory()

            elif action == "FULL_RECOVERY_MODE":

                print("🚨 FULL AI RECOVERY MODE ACTIVE")

                heal_network()
                heal_cpu()
                heal_memory()

    except Exception as e:
        print("❌ Healing System Error:", e)