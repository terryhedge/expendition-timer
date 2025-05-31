import os
import sys
import time
import tkinter as tk
import multiprocessing
import pystray
from PIL import Image
import keyboard

PHASES = [
    (270, "Night’s Tide Begins!", "red"),        # 4:30
    (390, "Final Collapse Approaching", "orange"),# 6:30
    (180, "Boss Encounter Begins!", "yellow")     # 3:00
]

current_overlay_process = None

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def overlay_process():
    def update_timer(root, label, phase_index, remaining):
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            label.config(text=f"{mins:02}:{secs:02}", fg="white")
            root.after(1000, update_timer, root, label, phase_index, remaining - 1)
        else:
            if phase_index < len(PHASES):
                message, color = PHASES[phase_index][1], PHASES[phase_index][2]
                label.config(text=message, fg=color)
                next_phase = phase_index + 1
                if next_phase < len(PHASES):
                    next_remaining = PHASES[next_phase][0]
                    root.after(1000, update_timer, root, label, next_phase, next_remaining)
                else:
                    root.after(5000, root.destroy)
            else:
                root.after(5000, root.destroy)

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.7)
    root.configure(bg="black")

    label = tk.Label(root, font=("Helvetica", 32), fg="white", bg="black")
    label.pack()

    # Allow dragging
    def start_move(event):
        root.x = event.x
        root.y = event.y

    def do_move(event):
        deltax = event.x - root.x
        deltay = event.y - root.y
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        root.geometry(f"+{x}+{y}")

    label.bind("<Button-1>", start_move)
    label.bind("<B1-Motion>", do_move)

    root.geometry(f"+{int(root.winfo_screenwidth()/2 - 180)}+30")

    update_timer(root, label, 0, PHASES[0][0])
    root.mainloop()

def run_overlay():
    global current_overlay_process
    if current_overlay_process and current_overlay_process.is_alive():
        current_overlay_process.terminate()
        current_overlay_process.join()
        time.sleep(0.2)
    current_overlay_process = multiprocessing.Process(target=overlay_process)
    current_overlay_process.start()

def on_quit(icon, item):
    global current_overlay_process
    if current_overlay_process and current_overlay_process.is_alive():
        current_overlay_process.terminate()
        current_overlay_process.join()
    icon.stop()
    sys.exit()

def setup_tray():
    icon_path = resource_path("nightreign.ico")
    image = Image.open(icon_path)
    menu = pystray.Menu(pystray.MenuItem("Quit", on_quit))
    icon = pystray.Icon("NightreignOverlay", image, "Nightreign Overlay", menu)

    keyboard.add_hotkey("F9", run_overlay)
    icon.run()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    setup_tray()
