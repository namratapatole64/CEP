import tkinter as tk
from tkinter import messagebox
import time
import threading
import os

# -------------------------------
# Configuration
# -------------------------------
PIN_FILE = "pin.txt"
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 10  # seconds
entered_pin = ""
attempts = 0
locked = False


# -------------------------------
# Functions
# -------------------------------
def load_pin():
    """Load stored PIN from file or create default"""
    if not os.path.exists(PIN_FILE):
        with open(PIN_FILE, "w") as f:
            f.write("1234")
        return "1234"
    with open(PIN_FILE, "r") as f:
        return f.read().strip()


def save_pin(new_pin):
    """Save new PIN to file"""
    with open(PIN_FILE, "w") as f:
        f.write(new_pin)


CORRECT_PIN = load_pin()


def update_display(text):
    display_var.set(text)


def press_key(key):
    global entered_pin
    if locked:
        return

    if key == "C":  # clear
        entered_pin = ""
        update_display("")
    elif key == "E":  # enter
        check_pin()
    else:
        if len(entered_pin) < 4:
            entered_pin += key
            update_display("*" * len(entered_pin))


def check_pin():
    global entered_pin, attempts, locked, CORRECT_PIN

    if entered_pin == CORRECT_PIN:
        update_display("✅ UNLOCKED")
        set_status("unlocked")
        messagebox.showinfo("Access Granted", "Door Unlocked!")
        root.after(3000, lock_back)
        attempts = 0

        # Ask to change PIN
        change = messagebox.askyesno("Change PIN", "Do you want to change your PIN?")
        if change:
            new_pin = simple_input("Enter new 4-digit PIN:")
            if new_pin and len(new_pin) == 4 and new_pin.isdigit():
                save_pin(new_pin)
                CORRECT_PIN = new_pin
                messagebox.showinfo("PIN Changed", "New PIN saved successfully!")
            else:
                messagebox.showwarning("Invalid", "PIN must be 4 digits.")

    else:
        attempts += 1
        update_display("❌ WRONG PIN")
        set_status("locked")
        if attempts >= MAX_ATTEMPTS:
            lockout()
        else:
            root.after(1500, lambda: update_display(""))
    entered_pin = ""


def lock_back():
    update_display("")
    set_status("locked")


def set_status(state):
    if state == "locked":
        lock_label.config(text="🔒 LOCKED", fg="red")
    else:
        lock_label.config(text="🔓 UNLOCKED", fg="green")


def lockout():
    global locked, attempts
    locked = True
    update_display("⏳ LOCKED OUT")
    messagebox.showwarning(
        "LOCKOUT", f"Too many wrong attempts!\nLocked for {LOCKOUT_TIME} seconds."
    )

    def unlock_after_delay():
        global locked, attempts
        time.sleep(LOCKOUT_TIME)
        locked = False
        attempts = 0
        update_display("")
        set_status("locked")

    threading.Thread(target=unlock_after_delay, daemon=True).start()


def simple_input(prompt):
    """Popup window to get text input"""
    win = tk.Toplevel(root)
    win.title("Input")
    win.geometry("250x120")
    win.resizable(False, False)

    tk.Label(win, text=prompt, font=("Arial", 10)).pack(pady=5)
    val = tk.StringVar()
    entry = tk.Entry(win, textvariable=val, show="*", font=("Arial", 12))
    entry.pack(pady=5)
    entry.focus()

    result = {"value": None}

    def submit():
        result["value"] = val.get()
        win.destroy()

    tk.Button(win, text="OK", command=submit).pack(pady=5)
    win.wait_window()
    return result["value"]


# -------------------------------
# GUI Setup
# -------------------------------
root = tk.Tk()
root.title("Digital Lock System")
root.geometry("300x420")
root.resizable(True, True)
root.minsize(300, 420)
root.configure(bg="#111")

display_var = tk.StringVar()

# Display
display = tk.Entry(
    root,
    textvariable=display_var,
    font=("Arial", 20, "bold"),
    justify="center",
    bd=6,
    relief="ridge",
)
display.pack(pady=10, ipadx=20, ipady=5)

# Lock status label
lock_label = tk.Label(root, text="🔒 LOCKED", fg="red", bg="#111", font=("Arial", 16))
lock_label.pack(pady=10)

# Keypad layout
keys = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["C", "0", "E"],
]

frame = tk.Frame(root, bg="#111")
frame.pack()

for r, row in enumerate(keys):
    for c, key in enumerate(row):
        tk.Button(
            frame,
            text=key,
            font=("Arial", 18, "bold"),
            width=4,
            height=2,
            bg="#333",
            fg="white",
            activebackground="#555",
            command=lambda k=key: press_key(k),
        ).grid(row=r, column=c, padx=5, pady=5)

# Footer
tk.Label(
    root, text="Digital Lock Project", bg="#111", fg="#888", font=("Arial", 10)
).pack(side="bottom", pady=10)

root.mainloop()
