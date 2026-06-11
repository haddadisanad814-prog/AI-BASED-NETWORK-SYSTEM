import winsound
import threading
import time

alarm_running = False

def alarm_loop():
    while alarm_running:
        winsound.Beep(2500, 1000)

def start_alarm():
    global alarm_running

    if not alarm_running:
        alarm_running = True
        threading.Thread(target=alarm_loop, daemon=True).start()

def stop_alarm():
    global alarm_running
    alarm_running = False

if __name__ == "__main__":
    print("Alarm Test Started...")
    start_alarm()

    time.sleep(10)

    stop_alarm()
    print("Alarm Stopped")