import tkinter as tk
from tkinter import messagebox
import datetime

FILENAME = "check_ins.txt"

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
    with open(filename, "w") as file:
            file.write(check_in.daily_check_in() + "\n")

def calculate_risk_score(check_ins):
    recent = check_ins[-7:] #Get the last 7 days of check-ins
    total = 0
    for check_in in recent:
        total += check_in.mood + check_in.energy + check_in.workload
    average = total / len(recent)
    score = int((average / 15) * 100)
    if score < 0:
        score = 0
    elif score > 100:
        score = 100
    return score

def get_valid_rating(entry, field_name):
    value = entry.get()
    try:
        value = int(value)
    except ValueError:
        messagebox.showerror("Invalid input", f"{field_name} must be a whole number.")
        return None
    if value < 0 or value > 5:
        messagebox.showerror("Invalid input", f"{field_name} must be between 0 and 5.")
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

def collect_entries():
    mood = get_valid_rating(mood_entry, "Mood")
    energy = get_valid_rating(energy_entry, "Energy")
    workload = get_valid_rating(workload_entry, "Workload")
    if mood is None or energy is None or workload is None:
        return
    today = datetime.date.today().isoformat()
    print(today)
    new_check_in = Check_In(today, mood, energy, workload)
    checkins.append(new_check_in)
    messagebox.showinfo("Saved", "Your check-in has been saved.")


root.mainloop()