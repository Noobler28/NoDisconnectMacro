import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pynput.keyboard import Controller, Listener

keyboard = Controller()

def hold_key(key, duration):
    keyboard.press(key)
    time.sleep(duration)
    keyboard.release(key)

class HotkeyManager:
    def __init__(self, start_key="f6", stop_key="f7"):
        self.start_key = start_key
        self.stop_key = stop_key
        self.listener = None
        self.callbacks = {"start": None, "stop": None}

    def set_callbacks(self, start_cb, stop_cb):
        self.callbacks["start"] = start_cb
        self.callbacks["stop"] = stop_cb

    def update_hotkeys(self, start_key, stop_key):
        self.start_key = start_key.lower()
        self.stop_key = stop_key.lower()
        self.restart_listener()

    def restart_listener(self):
        if self.listener:
            self.listener.stop()
        self.listener = Listener(on_press=self.on_press)
        self.listener.daemon = True
        self.listener.start()

    def on_press(self, key):
        try:
            k = key.char.lower()
        except:
            k = str(key).replace("Key.", "").lower()

        if k == self.start_key and self.callbacks["start"]:
            self.callbacks["start"]()
        if k == self.stop_key and self.callbacks["stop"]:
            self.callbacks["stop"]()

class KeyPresser:
    def __init__(self):
        self.running = False
        self.interval = 0.5
        self.randomize = False
        self.random_min = 0.3
        self.random_max = 0.8
        self.sequence = ["a", "d"]
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def run(self):
        import random
        while self.running:
            for key in self.sequence:
                if not self.running:
                    break

                duration = self.interval
                if self.randomize:
                    duration = random.uniform(self.random_min, self.random_max)

                hold_key(key, duration)

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, hotkeys, presser):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x420")
        self.resizable(False, False)

        self.hotkeys = hotkeys
        self.presser = presser

        frame = ttk.Frame(self, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Macro Settings", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0,10))

        hotkey_frame = ttk.LabelFrame(frame, text="Hotkeys", padding=10)
        hotkey_frame.pack(fill="x", pady=10)

        ttk.Label(hotkey_frame, text="Start Hotkey:").pack(anchor="w")
        self.start_entry = ttk.Entry(hotkey_frame)
        self.start_entry.insert(0, self.hotkeys.start_key)
        self.start_entry.pack(fill="x")

        ttk.Label(hotkey_frame, text="Stop Hotkey:").pack(anchor="w", pady=(10,0))
        self.stop_entry = ttk.Entry(hotkey_frame)
        self.stop_entry.insert(0, self.hotkeys.stop_key)
        self.stop_entry.pack(fill="x")

        random_frame = ttk.LabelFrame(frame, text="Random Interval", padding=10)
        random_frame.pack(fill="x", pady=10)

        self.random_var = tk.BooleanVar(value=self.presser.randomize)
        ttk.Checkbutton(random_frame, text="Enable Randomised Interval", variable=self.random_var).pack(anchor="w")

        ttk.Label(random_frame, text="Min (seconds):").pack(anchor="w")
        self.min_entry = ttk.Entry(random_frame)
        self.min_entry.insert(0, str(self.presser.random_min))
        self.min_entry.pack(fill="x")

        ttk.Label(random_frame, text="Max (seconds):").pack(anchor="w")
        self.max_entry = ttk.Entry(random_frame)
        self.max_entry.insert(0, str(self.presser.random_max))
        self.max_entry.pack(fill="x")

        ttk.Label(seq_frame, text="Keys (comma separated):").pack(anchor="w")
        self.seq_entry = ttk.Entry(seq_frame)
        self.seq_entry.insert(0, ",".join(self.presser.sequence))
        self.seq_entry.pack(fill="x")

        ttk.Button(frame, text="Save Settings", command=self.save).pack(pady=15)

    def save(self):
        try:
            start_key = self.start_entry.get().strip().lower()
            stop_key = self.stop_entry.get().strip().lower()

            self.hotkeys.update_hotkeys(start_key, stop_key)

            self.presser.randomize = self.random_var.get()
            self.presser.random_min = float(self.min_entry.get())
            self.presser.random_max = float(self.max_entry.get())

            seq = self.seq_entry.get().strip().lower().split(",")
            self.presser.sequence = [s.strip() for s in seq if s.strip()]

            messagebox.showinfo("Saved", "Settings updated successfully.")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Invalid settings:\n{e}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("No Disconnect Macro")
        self.root.geometry("450x300")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")

        self.presser = KeyPresser()
        self.hotkeys = HotkeyManager()
        self.hotkeys.set_callbacks(self.start, self.stop)
        self.hotkeys.restart_listener()

        main = ttk.Frame(root, padding=15)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="NO DISCONNECT MACRO", font=("Segoe UI", 18, "bold")).pack(pady=5)
        ttk.Label(main, text="Created by Connor", font=("Segoe UI", 10, "italic")).pack(pady=(0,10))

        control_frame = ttk.LabelFrame(main, text="Controls", padding=10)
        control_frame.pack(fill="x", pady=10)

        self.interval_var = tk.DoubleVar(value=0.5)
        ttk.Label(control_frame, text="Base Hold Duration (seconds):").pack(anchor="w")
        self.slider = ttk.Scale(control_frame, from_=0.05, to=2.0, orient="horizontal",
                                variable=self.interval_var, command=self.update_interval)
        self.slider.pack(fill="x")

        ttk.Button(control_frame, text="Start", command=self.start).pack(side="left", padx=5, pady=10)
        ttk.Button(control_frame, text="Stop", command=self.stop).pack(side="left", padx=5, pady=10)

        self.status = ttk.Label(main, text="Status: Stopped", foreground="red")
        self.status.pack(pady=5)

        menubar = tk.Menu(root)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.open_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="Menu", menu=settings_menu)
        root.config(menu=menubar)

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_interval(self, _):
        self.presser.interval = self.interval_var.get()

    def start(self):
        self.presser.start()
        self.status.config(text="Status: Running", foreground="green")

    def stop(self):
        self.presser.stop()
        self.status.config(text="Status: Stopped", foreground="red")

    def open_settings(self):
        SettingsWindow(self.root, self.hotkeys, self.presser)

    def on_close(self):
        self.presser.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
