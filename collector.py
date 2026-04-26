# collector.py (mouse removed)
from pynput import keyboard
import time
import csv
import os
from datetime import datetime

class BioGuardCollector:
    def __init__(self, user_id):
        self.user_id = user_id
        self.session_start = time.time()
        self.keystrokes = []
        os.makedirs("data", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"data/{user_id}_{timestamp}.csv"

    def on_press(self, key):
        try:
            self.keystrokes.append({'event': 'press', 'key': str(key).replace("'", ""), 'time': time.time()})
        except:
            pass

    def on_release(self, key):
        try:
            self.keystrokes.append({'event': 'release', 'key': str(key).replace("'", ""), 'time': time.time()})
            if key == keyboard.Key.esc:
                self.stop()
                return False
        except:
            pass

    def start(self):
        print(f"Recording started for user {self.user_id}")
        print("Type anything… Press ESC when finished.")
        k_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        k_listener.start()
        k_listener.join()

    def stop(self):
        self.save_data()
        print(f"Data saved → {self.filename}")

    def save_data(self):
        with open(self.filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id','type','event','key','time'])
            base = self.session_start
            for e in self.keystrokes:
                writer.writerow([self.user_id, 'key', e['event'], e['key'], round(e['time']-base, 4)])

if __name__ == "__main__":
    uid = input("Enter User ID (e.g. patrick01): ")
    BioGuardCollector(uid).start()
