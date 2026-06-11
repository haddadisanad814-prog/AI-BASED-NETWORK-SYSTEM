import winsound
import threading

running = False

def _alarm():
    while running:
        winsound.Beep(4000, 1500)

def start_buzzer():
    global running
    if not running:
        running = True
        threading.Thread(target=_alarm, daemon=True).start()

def stop_buzzer():
    global running
    running = False