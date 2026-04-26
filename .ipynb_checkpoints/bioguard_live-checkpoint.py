# bioguard_live.py – ULTRA-SENSITIVE & BEAUTIFUL VERSION
import numpy as np
import time
import tkinter as tk
from pynput import keyboard, mouse
import threading

# ================== LIVE ACTIVITY TRACKING ==================
last_activity_time = time.time()
lock = threading.Lock()

def update_activity():
    global last_activity_time
    with lock:
        last_activity_time = time.time()

def on_press(key):
    update_activity()

def on_release(key):
    update_activity()

def on_move(x, y):
    update_activity()

def on_click(x, y, button, pressed):
    update_activity()

# Start listeners
keyboard.Listener(on_press=on_press, on_release=on_release).start()
mouse.Listener(on_move=on_move, on_click=on_click).start()

# ================== GUI ==================
root = tk.Tk()
root.title("BioGuard")
root.geometry("400x200+40+40")
root.configure(bg="#0d0d0d")
root.attributes("-topmost", True)
root.overrideredirect(False)
root.resizable(False, False)

title = tk.Label(root, text="BIOGUARD", fg="#00ff00", bg="#0d0d0d",
                 font=("Consolas", 28, "bold"))
title.pack(pady=(20,5))

status = tk.Label(root, text="VERIFYING...", fg="yellow", bg="#0d0d0d",
                  font=("Consolas", 44, "bold"))
status.pack(expand=True)

def update_status():
    idle_seconds = time.time() - last_activity_time
    
    if idle_seconds < 1.2:
        color = "#00ff00"      # bright green
        text  = "VERIFIED"
    elif idle_seconds < 3.0:
        color = "#ffff00"      # yellow
        text  = "MONITORING"
    else:
        color = "#ff0000"      # red
        text  = "SUSPICIOUS"
    
    status.config(text=text, fg=color)
    root.after(200, update_status)   # check every 0.2 sec

update_status()
root.mainloop()