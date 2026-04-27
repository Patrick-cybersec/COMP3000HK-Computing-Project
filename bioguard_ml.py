# bioguard_ml.py - ACADEMICALLY RIGOROUS ENSEMBLE AI
import time
import os
import io
import base64
import threading
import numpy as np
import tkinter as tk
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import hmac
import hashlib
import os
import time
from tkinter import messagebox, simpledialog

# AI / ML Imports
from pynput import keyboard
from collections import deque
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
import joblib

# Cryptography Imports
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from bioguard_auth import build_alert


class BioGuardML:
    def __init__(self):
        # [CAPSTONE UPGRADE] - Adjusted for realistic behavioral trends
        self.WINDOW_SIZE = 80
        self.ANOMALY_THRESHOLD = 0.35
        self.MIN_TRAIN_KEYS = 300
        self.RETRAIN_INTERVAL = 300
        self.MODEL_DIR = "secure_profiles"

        # State Variables
        self.current_user = None
        self.current_password = None
        self.mode = "IDLE"
        self.is_locked = False
        self.keystroke_count = 0

        # Data Buffers
        self.live_buffer = deque(maxlen=self.WINDOW_SIZE)
        self.base_train_data = []
        self.safe_keystrokes = []
        self.press_times = {}
        self.current_flight_times = {}
        self.last_release_time = None

        # Spatial & Modifier Tracking
        self.active_modifiers = set()
        self.last_key_zone = -1

        # Models
        self.models = {}
        self.model_lock = threading.Lock()

        # Logging: rotating file for events and alerts
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        self.logger = logging.getLogger("BioGuard")
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(os.path.join(log_dir, "bioguard.log"), maxBytes=5_000_000, backupCount=5)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Alert config (set these environment variables or replace with constants)
        self.ADMIN_URL = os.environ.get("BIOGUARD_ADMIN_URL", "https://admin-vm.local/alerts")
        self.ALERT_API_KEY = os.environ.get("BIOGUARD_ALERT_API_KEY", "replace_with_api_key")
        self.ALERT_HMAC_KEY = os.environ.get("BIOGUARD_ALERT_HMAC_KEY", "replace_with_hmac_key").encode()


        if not os.path.exists(self.MODEL_DIR):
            os.makedirs(self.MODEL_DIR)

        self.root = tk.Tk()
        self.root.withdraw()
        self.start_listeners()
        self.show_auth_screen()
        self.root.mainloop()

    # ==================== CRYPTO & STORAGE ====================
    def _get_encryption_key(self, password, salt=b'bioguard_project_2026'):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def save_models(self, username, password, models_dict, base_data):
        """
        SECURITY NOTE FOR PROJECT REPORT:
        While encrypted with AES (Fernet), unpickling via joblib poses a deserialization
        security risk if an insider tampers with the ciphertext prior to decryption.
        A production-grade system would migrate to `skops` or JSON-based weight extraction.
        """
        cipher = self._get_encryption_key(password)
        payload = {
            'models': models_dict,
            'base_data': base_data[-1500:]
        }
        buffer = io.BytesIO()
        joblib.dump(payload, buffer)
        encrypted_data = cipher.encrypt(buffer.getvalue())
        filepath = os.path.join(self.MODEL_DIR, f"{username}.enc")
        with open(filepath, 'wb') as f:
            f.write(encrypted_data)

    def load_models(self, username, password):
        filepath = os.path.join(self.MODEL_DIR, f"{username}.enc")
        if not os.path.exists(filepath):
            return None, None

        cipher = self._get_encryption_key(password)
        try:
            with open(filepath, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = cipher.decrypt(encrypted_data)
            buffer = io.BytesIO(decrypted_data)
            payload = joblib.load(buffer)
            return payload['models'], payload['base_data']
        except Exception:
            return False, False

    # ==================== GUI SCREENS ====================
    def show_auth_screen(self):
        self.mode = "IDLE"
        auth_win = tk.Toplevel(self.root)
        auth_win.title("BioGuard AI - Capstone Edition")
        auth_win.geometry("400x350")
        auth_win.configure(bg="#1e272e")
        auth_win.protocol("WM_DELETE_WINDOW", self.root.quit)

        tk.Label(auth_win, text="BIOGUARD AI", fg="#0fb9b1", bg="#1e272e",
                 font=("Arial", 20, "bold")).pack(pady=20)

        tk.Label(auth_win, text="Username:", fg="white", bg="#1e272e", font=("Arial", 12)).pack()
        user_entry = tk.Entry(auth_win, font=("Arial", 12), width=25)
        user_entry.pack(pady=5)

        tk.Label(auth_win, text="Password:", fg="white", bg="#1e272e", font=("Arial", 12)).pack()
        pass_entry = tk.Entry(auth_win, font=("Arial", 12), width=25, show="*")
        pass_entry.pack(pady=5)

        def attempt_login():
            user = user_entry.get().strip()
            pwd = pass_entry.get().strip()

            loaded_models, loaded_data = self.load_models(user, pwd)
            if loaded_models is None:
                messagebox.showerror("Error", "Profile not found. Please Register.")
            elif loaded_models is False:
                messagebox.showerror("Error", "Access Denied. Incorrect Password.")
            else:
                self.current_user = user
                self.current_password = pwd
                self.models = loaded_models
                self.base_train_data = loaded_data
                auth_win.destroy()
                self.start_monitoring()

        def attempt_register():
            user = user_entry.get().strip()
            pwd = pass_entry.get().strip()
            if len(user) < 3 or len(pwd) < 4:
                messagebox.showerror("Error", "Username > 3 chars, Password > 4 chars required.")
                return

            self.current_user = user
            self.current_password = pwd
            auth_win.destroy()
            self.show_registration_screen()

        tk.Button(auth_win, text="Login & Monitor", command=attempt_login,
                  bg="#05c46b", fg="white", width=25, height=2,
                  font=("Arial", 10, "bold")).pack(pady=15)
        tk.Button(auth_win, text="Register New Profile", command=attempt_register,
                  bg="#ffdd59", fg="black", width=25, font=("Arial", 10)).pack()

    def show_registration_screen(self, default_name=""):
        reg_win = tk.Toplevel(self.root)
        reg_win.title("BioGuard - Fixed-Text Enrollment")
        reg_win.geometry("600x500")
        reg_win.configure(bg="#2c3e50")

        pangrams = [
            "The quick brown fox jumps over the lazy dog. The big banana changed from yellow to black. The kid Peter Chan became a adult.",
            "Pack my box, with five dozen liquor jugs! Put the carton box which has a \"fragile\" label under the table.",
            "I'm at a payphone, trying to call home. The five boxing wizards jump quickly. The lazy dog was not happy about the quick brown fox."
        ]

        tk.Label(reg_win, text="Fixed-Text Enrollment", fg="#00ff9f", bg="#2c3e50",
                 font=("Arial", 18, "bold")).pack(pady=15)
        tk.Label(reg_win, text="Please type exactly the sentence shown below (3 sessions):",
                 fg="white", bg="#2c3e50").pack()

        pangram_lbl = tk.Label(reg_win, text="", fg="#ffff00", bg="#2c3e50",
                               font=("Consolas", 14, "bold"))
        pangram_lbl.pack(pady=10)

        progress_lbl = tk.Label(reg_win, text="Session 0 / 3", fg="orange", bg="#2c3e50")
        progress_lbl.pack(pady=10)

        status_lbl = tk.Label(reg_win, text="Type the pangram naturally and click 'Finish Session'",
                              fg="white", bg="#2c3e50")
        status_lbl.pack(pady=20)

        self.current_session = 0
        self.training_sessions = []

        def start_next_session():
            self.current_session += 1
            if self.current_session > 3:
                self.mode = "IDLE"
                self.finalize_fixed_text_enrollment(default_name)
                reg_win.destroy()
                return

            self.mode = "TRAIN"
            current_pangram = pangrams[self.current_session - 1]
            pangram_lbl.config(text=current_pangram)
            progress_lbl.config(text=f"Session {self.current_session} / 3")
            status_lbl.config(text="Type the pangram naturally for at least 50 seconds\nClick 'Finish Session' when done")
            self.current_session_data = []
            self.session_start_time = time.time()
            messagebox.showinfo("Start", f"Session {self.current_session}/3\nType the sentence shown.",
                                parent=reg_win)

        def finish_session():
            duration = time.time() - self.session_start_time
            if duration < 50:
                messagebox.showwarning("Too short", "Please type for at least 50 seconds.", parent=reg_win)
                return
            if len(self.current_session_data) > 0:
                self.training_sessions.append(np.array(self.current_session_data))
            else:
                messagebox.showwarning("No data", "No keystroke vectors were recorded for this session.",
                                       parent=reg_win)
            start_next_session()

        tk.Button(reg_win, text="Finish Current Session", command=finish_session,
                  bg="#00ff9f", fg="black", width=30, height=2).pack(pady=30)
        start_next_session()

    def finalize_fixed_text_enrollment(self, username):
        if not hasattr(self, "training_sessions") or len(self.training_sessions) == 0:
            messagebox.showerror("Error", "No training data collected. Please retry enrollment.")
            self.mode = "IDLE"
            return

        try:
            combined_data = np.vstack(self.training_sessions)
        except Exception:
            try:
                reshaped = []
                for s in self.training_sessions:
                    arr = np.asarray(s)
                    if arr.ndim == 1 and arr.size % 3 == 0:
                        arr = arr.reshape(-1, 3)
                    elif arr.ndim == 2 and arr.shape[1] == 3:
                        pass
                    else:
                        raise ValueError("Session data shape invalid")
                    reshaped.append(arr)
                combined_data = np.vstack(reshaped)
            except Exception:
                messagebox.showerror("Error", "Collected data shape is invalid. Enrollment failed.")
                self.mode = "IDLE"
                return

        if combined_data.size == 0 or combined_data.ndim != 2 or combined_data.shape[1] == 0:
            messagebox.showerror("Error", "Collected data has no features. Enrollment failed.")
            self.mode = "IDLE"
            return

        if combined_data.ndim == 1:
            if combined_data.size % 3 == 0:
                combined_data = combined_data.reshape(-1, 3)
            else:
                messagebox.showerror("Error", "Collected data shape is invalid. Enrollment failed.")
                self.mode = "IDLE"
                return

        self.base_train_data = combined_data.tolist()
        self.train_and_save_models(self.base_train_data)

        messagebox.showinfo("Success", "Fixed-text AI profile created!\nStarting active monitoring.")
        self.mode = "MONITOR"
        self.safe_keystrokes = []
        self.live_buffer.clear()
        self.start_monitoring()

    # ==================== ENSEMBLE TRAINING & ADAPTIVE AI ====================
    def train_and_save_models(self, data_list):
        print("Training Spatially-Aware ML Models...")
        data = np.array(data_list)

        if data.size == 0:
            messagebox.showerror("Training Error", "No training samples available.")
            return
        if data.ndim == 1:
            if data.size % 3 == 0:
                data = data.reshape(-1, 3)
            else:
                messagebox.showerror("Training Error", "Training data has incorrect dimensionality.")
                return
        if data.shape[1] == 0:
            messagebox.showerror("Training Error", "Training data has zero features.")
            return

        model_iso = IsolationForest(n_estimators=100, contamination=0.10, random_state=42)
        model_iso.fit(data)

        model_svm = OneClassSVM(nu=0.10, kernel="rbf", gamma="scale")
        model_svm.fit(data)

        with self.model_lock:
            self.models = {'iforest': model_iso, 'ocsvm': model_svm}

        self.save_models(self.current_user, self.current_password, self.models, data_list)

    def trigger_adaptive_retraining(self):
        print("\n[AI] Triggering Adaptive Background Retraining...")
        combined_data = self.base_train_data + self.safe_keystrokes
        self.safe_keystrokes = []  # clear immediately to avoid double-triggering

        def retrain_task():
            self.train_and_save_models(combined_data)
            self.base_train_data = combined_data[-1500:]
            print("[AI] Adaptive Retraining Complete. Models Updated.")

        threading.Thread(target=retrain_task, daemon=True).start()

    # ==================== MONITORING & INFERENCE ====================
    def start_monitoring(self):
        self.live_buffer.clear()
        self.safe_keystrokes = []
        self.keystroke_count = 0
        self.mode = "MONITOR"
        print(f"BioGuard Active: Spatially-Aware Monitoring for '{self.current_user}'...")

    def trigger_lockout(self, anomaly_rate=None):
        self.is_locked = True
        self.mode = "IDLE"
        self.safe_keystrokes = []
        self.logger.warning(f"Lockout triggered for user {self.current_user} anomaly_rate={anomaly_rate}")

        # Send alert asynchronously so UI isn't blocked
        try:
            threading.Thread(
                target=lambda: build_alert(self.current_user, anomaly_rate or 0.0, self.WINDOW_SIZE),
                daemon=True
            ).start()
        except Exception as e:
            self.logger.error(f"Failed to start alert thread: {e}")

        lock_win = tk.Toplevel(self.root)
        lock_win.attributes("-fullscreen", True)
        lock_win.configure(bg="#c23616")
        lock_win.attributes("-topmost", True)
        lock_win.protocol("WM_DELETE_WINDOW", lambda: None)

        tk.Label(lock_win, text="SYSTEM LOCKED", fg="white", bg="#c23616", font=("Courier", 50, "bold")).pack(pady=100)
        tk.Label(lock_win, text="Anomalous typing rhythm detected.", fg="white", bg="#c23616", font=("Arial", 20)).pack(pady=20)

        # Unlock attempt tracking
        if not hasattr(self, "failed_unlocks"):
            self.failed_unlocks = 0
            self.last_failed_time = 0

        def unlock():
            # Enforce cooldown after 3 failed attempts
            now = time.time()
            if self.failed_unlocks >= 3 and (now - self.last_failed_time) < 30:
                wait = int(30 - (now - self.last_failed_time))
                messagebox.showwarning("Cooldown", f"Too many attempts. Please wait {wait} seconds.", parent=lock_win)
                return

            pwd = simpledialog.askstring("Unlock", f"Enter Password for {self.current_user}:", show='*', parent=lock_win)
            if pwd is None:
                return

            if pwd == self.current_password:
                self.is_locked = False
                self.keystroke_count = 0
                self.mode = "MONITOR"
                self.live_buffer.clear()
                lock_win.destroy()
                self.failed_unlocks = 0
                self.last_failed_time = 0
                self.logger.info(f"User {self.current_user} unlocked system successfully.")
                print("Identity verified. Resuming monitoring.")
            else:
                self.failed_unlocks = getattr(self, "failed_unlocks", 0) + 1
                self.last_failed_time = time.time()
                self.logger.warning(f"Failed unlock attempt {self.failed_unlocks} for user {self.current_user}")
                messagebox.showerror("Denied", "Incorrect Password!", parent=lock_win)

        tk.Button(lock_win, text="UNLOCK SYSTEM", command=unlock, font=("Arial", 18, "bold"), bg="black", fg="white", width=20, height=3).pack(pady=50)

    # ==================== FEATURE EXTRACTION ====================
    def _get_key_zone(self, key):
        """Maps keys to keyboard zones to extract spatial features without compromising privacy."""
        try:
            char = key.char.lower()
            if char in 'qwertasdfgzxcvb':
                return 1  # Left Hand Zone
            if char in 'yuiophjklnm':
                return 2  # Right Hand Zone
        except AttributeError:
            pass
        return 0  # Symbols, Space, Numbers, etc.

    def _is_ignored_key(self, key):
        """Centralised set of keys to exclude from biometric feature extraction."""
        ignored = {
            keyboard.Key.space,
            keyboard.Key.enter,
            keyboard.Key.backspace,
            keyboard.Key.tab,
            keyboard.Key.left, keyboard.Key.right, keyboard.Key.up, keyboard.Key.down,
            keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
            keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
            keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
            keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
            keyboard.Key.caps_lock, keyboard.Key.num_lock, keyboard.Key.scroll_lock,
            keyboard.Key.esc,
            keyboard.Key.f1, keyboard.Key.f2, keyboard.Key.f3, keyboard.Key.f4,
            keyboard.Key.f5, keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8,
            keyboard.Key.f9, keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12,
        }
        return key in ignored

    def process_keystroke_vector(self, vector):
        if self.mode == "TRAIN":
            self.base_train_data.append(vector)
            if hasattr(self, "current_session_data"):
                self.current_session_data.append(vector)
            return

        if self.mode != "MONITOR":
            return

        now = time.time()

        # Reset warm-up counter if idle for >= 5 seconds
        if self.last_release_time and (now - self.last_release_time) >= 5:
            self.keystroke_count = 0

        self.keystroke_count += 1

        # Skip first 20 keystrokes after each idle reset (warm-up period)
        if self.keystroke_count <= 20:
            return

        self.live_buffer.append(vector)
        self.safe_keystrokes.append(vector)

        if len(self.safe_keystrokes) >= self.RETRAIN_INTERVAL:
            self.trigger_adaptive_retraining()

        if len(self.live_buffer) == self.WINDOW_SIZE:
            current_window = np.array(self.live_buffer)

            with self.model_lock:
                if not self.models or 'iforest' not in self.models or 'ocsvm' not in self.models:
                    print("[Warning] Models not ready for inference.")
                    for _ in range(int(self.WINDOW_SIZE * 0.4)):
                        self.live_buffer.popleft()
                    return
                try:
                    pred_iso = self.models['iforest'].predict(current_window)
                    pred_svm = self.models['ocsvm'].predict(current_window)
                except Exception as e:
                    print(f"[Error] Model prediction failed: {e}")
                    for _ in range(int(self.WINDOW_SIZE * 0.4)):
                        self.live_buffer.popleft()
                    return

            rate_iso = np.sum(pred_iso == -1) / self.WINDOW_SIZE
            rate_svm = np.sum(pred_svm == -1) / self.WINDOW_SIZE
            anomaly_rate = (rate_iso + rate_svm) / 2

            if anomaly_rate > 0.05:
                print(f"[Alert] Ensemble Rate: {anomaly_rate:.2%} (Threshold: {self.ANOMALY_THRESHOLD:.2%})")

            if anomaly_rate > self.ANOMALY_THRESHOLD:
                self.root.after(0, lambda: self.trigger_lockout(anomaly_rate))

            # Slide window forward by 40%
            for _ in range(int(self.WINDOW_SIZE * 0.4)):
                self.live_buffer.popleft()

    # ==================== EVENT LISTENERS ====================
    def start_listeners(self):
        self.k_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.k_listener.start()

    def on_press(self, key):
        if self.is_locked:
            return

        # Track modifiers separately
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                   keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
                   keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
                   keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.active_modifiers.add(key)
            return

        if len(self.active_modifiers) > 0:
            return

        if self._is_ignored_key(key):
            return

        t = time.time()
        key_id = str(key)
        current_zone = self._get_key_zone(key)

        if key_id not in self.press_times:
            self.press_times[key_id] = t
            flight_time = 0
            if self.last_release_time is not None:
                flight_time = min(t - self.last_release_time, 2.0)

            self.current_flight_times[key_id] = flight_time

            is_same_hand = 0.5
            if self.last_key_zone in [1, 2] and current_zone in [1, 2]:
                is_same_hand = 1.0 if self.last_key_zone == current_zone else 0.0

            self.last_key_zone = current_zone
            self.current_flight_times[key_id + "_hand"] = is_same_hand

    def on_release(self, key):
        if self.is_locked:
            return

        # Clean up modifier tracking
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                   keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
                   keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
                   keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.active_modifiers.discard(key)
            return

        if len(self.active_modifiers) > 0:
            return

        if self._is_ignored_key(key):
            # Still update last_release_time for idle detection
            self.last_release_time = time.time()
            return

        t = time.time()
        key_id = str(key)

        if key_id in self.press_times:
            press_time = self.press_times.pop(key_id)
            hold_time = t - press_time
            flight_time = self.current_flight_times.pop(key_id, 0)
            is_same_hand = self.current_flight_times.pop(key_id + "_hand", 0.5)
            self.last_release_time = t

            if hold_time < 1.0:
                # 3D VECTOR: [Hold Time, Flight Time, Spatial Hand Transition]
                self.process_keystroke_vector([hold_time, flight_time, is_same_hand])
    
    def _send_alert(self, username, anomaly_rate, window_size):
        payload = {
            "event": "anomaly_lockout",
            "user": username,
            "anomaly_rate": round(float(anomaly_rate), 4),
            "window_size": int(window_size),
            "timestamp": int(time.time()),
            "event_id": f"{username}-{int(time.time())}"
        }
        body = json.dumps(payload, separators=(",", ":")).encode()
        signature = hmac.new(self.ALERT_HMAC_KEY, body, hashlib.sha256).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.ALERT_API_KEY,
            "X-Signature": signature
        }

        # Simple retry with exponential backoff
        backoff = 1
        for attempt in range(4):
            try:
                r = requests.post(self.ADMIN_URL, data=body, headers=headers, timeout=5, verify=True)
                r.raise_for_status()
                self.logger.info(f"Alert sent: {payload['event_id']} to {self.ADMIN_URL}")
                return True
            except Exception as e:
                self.logger.warning(f"Alert send failed (attempt {attempt+1}): {e}")
                time.sleep(backoff)
                backoff *= 2
        self.logger.error(f"Alert send permanently failed: {payload['event_id']}")
        return False


if __name__ == "__main__":
    app = BioGuardML()
