import tkinter as tk
from tkinter import messagebox
import datetime

FILENAME = "check_ins.txt"
UPPER_BOUNDARY = 5
LOWER_BOUNDARY = 1
MIN_SCORE = 0
MAX_SCORE = 100
HIGH_RISK_AVERAGE = 2
HIGH_RISK_SCORE = 65
MODERATE_RISK_SCORE = 35
MODERATE_RISK_AVERAGE = 3.5
WEEK = 7
MAX_TOTAL_SCORE = 15
FACTOR_COUNT = 3

class Check_In:
    def __init__(self, date, mood, energy, workload):
        self.date = date
        self.mood = mood
        self.energy = energy
        self.workload = workload

    def daily_check_in(self):
        return f"{self.date},{self.workload},{self.energy},{self.mood}"

def load_check_ins(filename=FILENAME):
    try:
        check_ins = []
        with open(filename, "r") as file:
            for line in file:
                date, mood, energy, workload = line.split(",")
                check_ins.append(Check_In(date, int(mood), int(energy), int(workload)))
        return check_ins
    except FileNotFoundError:
        return check_ins
    
def save_checkin(check_in, filename=FILENAME):
    with open(filename, "a") as file:
            file.write(check_in.daily_check_in() + "\n")

def calculate_risk_score(check_ins):
    if not check_ins:
        return 0
    recent = check_ins[-WEEK:] #Get the last 7 days of check-ins
    total = 0
    for check_in in recent:
        total += (UPPER_BOUNDARY - check_in.mood) + (UPPER_BOUNDARY - check_in.energy) + check_in.workload
    average = total / len(recent)
    score = int((average / MAX_TOTAL_SCORE) * 100)
    if score < MIN_SCORE:
        score = MIN_SCORE
    elif score > MAX_SCORE:
        score = MAX_SCORE
    return score

def risk_level_from_score(score):
    if score >= HIGH_RISK_SCORE:
        return "high"
    elif score >= MODERATE_RISK_SCORE:
        return "moderate"
    else:
        return "low"

def risk_level_for(check_in):
    average = (check_in.mood + check_in.energy + (UPPER_BOUNDARY - check_in.workload)) / FACTOR_COUNT
    if average <= HIGH_RISK_AVERAGE:
        return "high"
    elif average <= MODERATE_RISK_AVERAGE:
        return "moderate"
    else:
        return "low"

def get_valid_rating(entry, field_name):
    value = entry.get()
    try:
        value = int(value)
    except ValueError:
        messagebox.showerror("Invalid input", f"{field_name} must be a whole number.")
        return None
    if value < LOWER_BOUNDARY or value > UPPER_BOUNDARY:
        messagebox.showerror("Invalid input", f"{field_name} must be between {LOWER_BOUNDARY} and {UPPER_BOUNDARY}.")
        return None
    return value

checkins = load_check_ins()
 
root = tk.Tk()
root.title("Flare")
root.geometry("300x320")

tk.Label(root, text="Mood (1-5):").pack(pady=(15, 0))
mood_entry = tk.Entry(root, width=10)
mood_entry.pack()

tk.Label(root, text="Energy (1-5):").pack(pady=(10, 0))
energy_entry = tk.Entry(root, width=10)
energy_entry.pack()

tk.Label(root, text="Workload (1-5):").pack(pady=(10, 0))
workload_entry = tk.Entry(root, width=10)
workload_entry.pack()

score_label = tk.Label(root, text="", font=("Arial", 12))
score_label.pack(pady=15)

def refresh_score_label():
    score = calculate_risk_score(checkins)
    level = risk_level_from_score(score)
    score_label.config(text=f"Burnout risk: {score} - {level}")

def collect_entries():
    mood = get_valid_rating(mood_entry, "Mood")
    energy = get_valid_rating(energy_entry, "Energy")
    workload = get_valid_rating(workload_entry, "Workload")
    if mood is None or energy is None or workload is None:
        return
    today = datetime.date.today().isoformat()
    new_check_in = Check_In(today, mood, energy, workload)
    checkins.append(new_check_in)
    save_checkin(new_check_in)
    refresh_score_label()
    messagebox.showinfo("Saved", "Your check-in has been saved.")

tk.Button(root, text="Submit check-in", command=collect_entries).pack(pady=5)

def open_history():
    history_window = tk.Toplevel(root)
    history_window.title("Flare Check-in History")
    history_window.geometry("250x250")

    tk.Label(history_window, text="Check-in History", font=("Arial", 14)).pack(pady=10)

    if not checkins:
        tk.Label(history_window, text="No check-ins yet.").pack(pady=10)
    else:
        for check_in in checkins:
            text = f"{check_in.date}: {risk_level_for(check_in)}"
            tk.Label(history_window, text=text, anchor="w").pack(fill="x", padx=20)

def open_notice():
    notice_window = tk.Toplevel()
    notice_window.title("Flare - Notice")
    notice_window.geometry("250x150")
    score = calculate_risk_score(checkins)
    level = risk_level_from_score(score)

    if level == "high":
        message = "Your check-ins show a high burnout risk. Consider taking a break."
    else:
        message = "Your burnout risk is not currently high. Keep checking in daily."
    
    tk.Label(notice_window, text=message, wraplength=200, justify="center").pack(pady=20, padx=10)

tk.Button(root, text="View History", command=open_history).pack(pady=5)
tk.Button(root, text="View Notice", command=open_notice).pack(pady=5)

refresh_score_label()

root.mainloop()