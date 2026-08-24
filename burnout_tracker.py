import tkinter as tk #Import Tkinter for the GUI
from tkinter import messagebox #Import messagebox for pop-up validation and information messages
import datetime

#Named Constants used throughout the app
FILENAME, USERS_FILENAME = "check_ins.txt", "users.txt"
UPPER_BOUNDARY = 5 #Highest possible rating for mood, energy, and workload
LOWER_BOUNDARY = 1 #Lowest possible rating for mood, energy, and workload
MIN_SCORE = 0 #Lowest possible burnout risk score
MAX_SCORE = 100 #Highest possible burnout risk score
HIGH_RISK_SCORE = 65 #Score threshold for high burnout risk
MODERATE_RISK_SCORE = 35 #Score threshold for moderate burnout risk
WEEK = 7 #Number of day used to calculate the average burnout risk score
MAX_TOTAL_SCORE = 13 #Highest possible total score from a single check-in

#Colour palette used throughout the app, instead of Tkinter's default grey/white look
BG_COLOR = "#F2F5F9" #Main window background colour
CARD_BG = "#FFFFFF" #Background colour for cards/panels
TEXT_COLOR = "#1B2A41" #Main text colour
SUBTEXT_COLOR = "#7A8AA0" #Muted text colour for secondary labels
PRIMARY = "#1E3A5F" #Main button colour
PRIMARY_DARK = "#142A47" #Darker shade for button press/hover
DANGER = "#E74C3C" #Colour for destructive actions (e.g. logout)
DANGER_DARK = "#C0392B" #Darker shade for danger button press/hover
LOW_COLOUR = "#4C9A6B" #Colour for low burnout risk
MODERATE_COLOUR = "#C99A3D" #Colour for moderate burnout risk
HIGH_COLOUR = "#B0645A" #Colour for high burnout risk

#Represents a single check-in, holding the data and ratings.
class Check_In:
    def __init__(self, username, date, mood, energy, workload):
        self.username = username
        self.date = date #Date of the check-in
        self.mood = mood #Mood rating (1-5)
        self.energy = energy #Energy rating (1-5)
        self.workload = workload #Workload rating (1-5)

    def daily_check_in(self):
        return f"{self.username},{self.date},{self.mood},{self.energy},{self.workload}" #Formats the check-in data as a string for saving to the file.

def load_users(filename=USERS_FILENAME):
    users = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                username, password = line.strip().split(",")
                users[username] = password
    except FileNotFoundError:
        pass
    return users

def save_user(username, password, filename=USERS_FILENAME):
    with open(filename, "a") as file:
        file.write(f"{username},{password}\n")

def load_check_ins(filename=FILENAME):
    check_ins = []
    try:
        with open(filename, "r") as file:
            for line in file:
                username, date, mood, energy, workload = line.strip().split(",")
                check_ins.append(Check_In(username, date, int(mood), int(energy), int(workload)))
    except FileNotFoundError:
        pass
    return check_ins

def save_all_checkins(all_checkins, filename=FILENAME):
    with open(filename, "w") as file:
        for check_in in all_checkins:
            file.write(check_in.daily_check_in() + "\n")

def limit_score(score):
    if score < MIN_SCORE:
        return MIN_SCORE
    elif score > MAX_SCORE:
        return MAX_SCORE
    return score

#Calculates the average burnout risk score based on the last 7 days of check-ins. If there are no check-ins, it returns a score of 0.
def calculate_risk_score(check_ins):
    if not check_ins:
        return 0 #If there are no check-ins, return a score of 0
    recent = check_ins[-WEEK:] #Get the last 7 days of check-ins
    total = 0
    for check_in in recent:
        total += (UPPER_BOUNDARY - check_in.mood) + (UPPER_BOUNDARY - check_in.energy) + check_in.workload #Calculate the total score based on mood, energy, and workload ratings
    average = total / len(recent)
    return limit_score(int((average / MAX_TOTAL_SCORE) * 100))
   
#Turns the numeric risk score into a string of "Low", "Moderate", or "high"
def risk_level_from_score(score):
    if score >= HIGH_RISK_SCORE: #If the score is above the high risk threshold, return "high"
        return "high"
    elif score >= MODERATE_RISK_SCORE: #If the score is above the moderate risk threshold, return "moderate"
        return "moderate"
    return "low"

def score_for(check_in):
    total = (UPPER_BOUNDARY - check_in.mood) + (UPPER_BOUNDARY - check_in.energy) + check_in.workload
    return limit_score(int((total / MAX_TOTAL_SCORE) * 100))

def score_colour(level):
    if level == "high":
        return HIGH_COLOUR
    elif level == "moderate":
        return MODERATE_COLOUR
    return LOW_COLOUR

#Checks that a value typed into an entry box is a whole number and between 1 and 5
def get_valid_rating(entry, field_name):
    try:
        value = int(entry.get())
    except ValueError:
        messagebox.showerror("Invalid input", f"{field_name} must be a whole number.")
        return None
    if value < LOWER_BOUNDARY or value > UPPER_BOUNDARY:
        messagebox.showerror("Invalid input", f"{field_name} must be between {LOWER_BOUNDARY} and {UPPER_BOUNDARY}.")
        return None
    return value

def styled_button(parent, text, command, bg=PRIMARY, fg="white", active_bg=PRIMARY_DARK):
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg, activebackground=active_bg,
                      activeforeground=fg, relief="flat", font=("Arial", 10, "bold"), padx=10, pady=6, bd=0)

def styled_entry(parent, width=18, show=None):
    return tk.Entry(parent, width=width, show=show, bg="white", fg=TEXT_COLOR, relief="solid", bd=1,
                     highlightthickness=1, highlightbackground="#DAD6F5", highlightcolor=PRIMARY)

def labeled_entry(parent, row, label_text, width=18, show=None, prefill=None):
    tk.Label(parent, text=label_text, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row, column=0, sticky="e", padx=(20, 10), pady=6)
    entry = styled_entry(parent, width=width, show=show)
    if prefill is not None:
        entry.insert(0, str(prefill))
    entry.grid(row=row, column=1, sticky="w", padx=(0, 20), pady=6)
    return entry

all_checkins = load_check_ins()
users = load_users()
open_popups = []

root = tk.Tk()
root.title("Flare")
root.geometry("340x480")

def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

def close_all_popups():
    for popup in open_popups:
        if popup.winfo_exists():
            popup.destroy()
    open_popups.clear()

def build_login_screen():
    clear_screen()
    root.configure(bg=BG_COLOR)
    tk.Label(root, text="Flare", font=("Arial", 20, "bold"), bg=BG_COLOR, fg=PRIMARY).grid(row=0, column=0, columnspan=2, pady=(30, 20))

    username_entry = labeled_entry(root, 1, "Username:")
    password_entry = labeled_entry(root, 2, "Password:", show="*")

    def on_login():
        username, password = username_entry.get().strip(), password_entry.get().strip()
        if username not in users or users[username] != password:
            messagebox.showerror("Login failed", "Incorrect username or password.")
            return
        build_main_screen(username)

    def on_signup():
        username, password = username_entry.get().strip(), password_entry.get().strip()
        if username == "" or password == "":
            messagebox.showerror("Invalid input", "Username and password cannot be empty.")
            return
        if username in users:
            messagebox.showerror("Invalid input", "That username is already taken.")
            return
        users[username] = password
        save_user(username, password)
        messagebox.showinfo("Account created", "You can now log in.")

    styled_button(root, "Login", on_login).grid(row=3, column=0, columnspan=2, pady=(20, 6))
    styled_button(root, "Sign Up", on_signup, bg=CARD_BG, fg=PRIMARY, active_bg="#E4EAF2").grid(row=4, column=0, columnspan=2, pady=6)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

def build_main_screen(username):
    clear_screen()
    root.configure(bg=BG_COLOR)
    tk.Label(root, text=f"Logged in as: {username}", font=("Arial", 8), bg=BG_COLOR, fg=SUBTEXT_COLOR).grid(row=0, column=0, columnspan=2, pady=(15, 10))

    mood_entry = labeled_entry(root, 1, "Mood (1-5):", width=10)
    energy_entry = labeled_entry(root, 2, "Energy (1-5):", width=10)
    workload_entry = labeled_entry(root, 3, "Workload (1-5):", width=10)
    tk.Label(root, text="1 = light, 5 = heavy (several deadlines)", font=("Arial", 8), bg=BG_COLOR, fg=SUBTEXT_COLOR).grid(row=4, column=0, columnspan=2, pady=(0, 10))

    score_label = tk.Label(root, text="", font=("Arial", 14, "bold"), bg=BG_COLOR)
    score_label.grid(row=5, column=0, columnspan=2, pady=10)

    def user_checkins():
        result = []
        for c in all_checkins:
            if c.username == username:
                result.append(c)
        return result

    def refresh_score_label():
        score = calculate_risk_score(user_checkins())
        level = risk_level_from_score(score)
        score_label.config(text=f"Burnout risk: {score} - {level}", fg=score_colour(level))

    def collect_entries():
        mood = get_valid_rating(mood_entry, "Mood")
        energy = get_valid_rating(energy_entry, "Energy")
        workload = get_valid_rating(workload_entry, "Workload")
        if mood is None or energy is None or workload is None:
            return
        new_check_in = Check_In(username, datetime.date.today().isoformat(), mood, energy, workload)
        all_checkins.append(new_check_in)
        save_all_checkins(all_checkins)
        refresh_score_label()
        messagebox.showinfo("Saved", "Your check-in has been saved.")

    styled_button(root, "Submit check-in", collect_entries).grid(row=6, column=0, columnspan=2, pady=(5, 12))

    def open_history():
        history_window = tk.Toplevel(root)
        open_popups.append(history_window)
        history_window.title("Flare Check-in History")
        history_window.geometry("320x340")
        history_window.configure(bg=BG_COLOR)
        tk.Label(history_window, text="Check-in History", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, columnspan=3, pady=10)

        rows_frame = tk.Frame(history_window, bg=BG_COLOR)
        rows_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10)

        def build_rows():
            for widget in rows_frame.winfo_children():
                widget.destroy()
            entries = user_checkins()
            if not entries:
                tk.Label(rows_frame, text="No check-ins yet.", bg=BG_COLOR, fg=SUBTEXT_COLOR).grid(row=0, column=0, columnspan=3, pady=10)
                return
            for row_index, check_in in enumerate(entries):
                score = score_for(check_in)
                level = risk_level_from_score(score)
                tk.Label(rows_frame, text=f"{check_in.date}: {score} - {level}", anchor="w", bg=BG_COLOR,
                         fg=score_colour(level), font=("Arial", 9, "bold")).grid(row=row_index, column=0, sticky="w", pady=3)
                tk.Button(rows_frame, text="Edit", command=lambda check_in=check_in: open_edit(check_in), bg=PRIMARY,
                          fg="white", relief="flat", font=("Arial", 8), padx=6).grid(row=row_index, column=1, padx=4)
                tk.Button(rows_frame, text="Delete", command=lambda check_in=check_in: delete_checkin(check_in),
                          bg=DANGER, fg="white", relief="flat", font=("Arial", 8), padx=6).grid(row=row_index, column=2, padx=4)
        def delete_checkin(check_in):
            all_checkins.remove(check_in)
            save_all_checkins(all_checkins)
            refresh_score_label()
            build_rows()

        def open_edit(check_in):
            edit_window = tk.Toplevel(history_window)
            edit_window.title("Edit check-in")
            edit_window.geometry("240x260")
            edit_window.configure(bg=BG_COLOR)
            edit_mood = labeled_entry(edit_window, 0, "Mood (1-5):", width=10, prefill=check_in.mood)
            edit_energy = labeled_entry(edit_window, 1, "Energy (1-5):", width=10, prefill=check_in.energy)
            edit_workload = labeled_entry(edit_window, 2, "Workload (1-5):", width=10, prefill=check_in.workload)
        
            def save_edit():
                mood = get_valid_rating(edit_mood, "Mood")
                energy = get_valid_rating(edit_energy, "Energy")
                workload = get_valid_rating(edit_workload, "Workload")
                if mood is None or energy is None or workload is None:
                    return
                check_in.mood, check_in.energy, check_in.workload = mood, energy, workload
                save_all_checkins(all_checkins)
                refresh_score_label()
                build_rows()
                edit_window.destroy()
        
            styled_button(edit_window, "Save", save_edit).grid(row=3, column=0, columnspan=2, pady=15)

        build_rows()

    styled_button(root, "View History", open_history, bg=CARD_BG, fg=PRIMARY, active_bg="#E4EAF2").grid(row=7, column=0, columnspan=2, pady=5)

build_login_screen()
root.mainloop()