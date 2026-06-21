import threading
import platform
import time

running = False
lock = threading.Lock()

IS_WINDOWS = platform.system().lower() == "windows"

if IS_WINDOWS:
    import winsound


def _alarm():
    global running

    while True:
        with lock:
            if not running:
                break

        if IS_WINDOWS:
            try:
                winsound.Beep(1200, 500)
            except Exception:
                pass
        else:
            time.sleep(0.5)


def start_buzzer():
    global running

    with lock:
        if running:
            return
        running = True

    threading.Thread(target=_alarm, daemon=True).start()


def stop_buzzer():
    global running
    with lock:
        running = False