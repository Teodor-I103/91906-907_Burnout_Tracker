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
    with open(filename, "w") as file:
        file.write(f"{username},{password}\n")

def load_check_ins(filename=FILENAME):
    check_ins = []
    try:
        with open(filename, "r") as file:
            for line in file:
                username, date, mood, energy, workload = line.split(",")
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
    value = entry.get() #Get the value from the entry box
    try:
        value = int(value) #Convert the value to an integer
    except ValueError:
        messagebox.showerror("Invalid input", f"{field_name} must be a whole number.") #Show an error message if the value is not a whole number
        return None
    if value < LOWER_BOUNDARY or value > UPPER_BOUNDARY:
        messagebox.showerror("Invalid input", f"{field_name} must be between {LOWER_BOUNDARY} and {UPPER_BOUNDARY}.") #Show an error message if the value is not between 1 and 5
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

check_ins = load_check_ins() #Load the check-ins from the file when the program starts

#Create the main window for the GUI and set its title and size
root = tk.Tk()
root.title("Flare") #Title of the window
root.geometry("300x320") #Size of the window

tk.Label(root, text="Mood (1-5):").pack(pady=(15, 0)) #Label for the mood entry box
mood_entry = tk.Entry(root, width=10) #Entry box for the mood rating
mood_entry.pack()

tk.Label(root, text="Energy (1-5):").pack(pady=(10, 0)) #Label for the energy entry box
energy_entry = tk.Entry(root, width=10) #Entry box for the energy rating
energy_entry.pack()

tk.Label(root, text="Workload (1-5):").pack(pady=(10, 0)) #Label for the workload entry box
workload_entry = tk.Entry(root, width=10) #Entry box for the workload rating
workload_entry.pack()

score_label = tk.Label(root, text="", font=("Arial", 12)) #Label to display the burnout risk score and level
score_label.pack(pady=15)

#Function to refresh the score label with the current burnout risk score and level
def refresh_score_label():
    score = calculate_risk_score(check_ins) #Calculate the current burnout risk score based on the check-ins
    level = risk_level_from_score(score) #Determine the risk level based on the score
    score_label.config(text=f"Burnout risk: {score} - {level}") #Update the score label with the current burnout risk score and level

#Function to collect the entries from the user, validate them, create a new check-in, save it, and refresh the score label
def collect_entries():
    mood = get_valid_rating(mood_entry, "Mood") #Get and validate the mood rating from the entry box
    energy = get_valid_rating(energy_entry, "Energy") #Get and validate the energy rating from the entry box
    workload = get_valid_rating(workload_entry, "Workload") #Get and validate the workload rating from the entry box
    if mood is None or energy is None or workload is None:
        return #Messagebox has already told the user what was wrong
    today = datetime.date.today().isoformat() #Get today's date
    new_check_in = Check_In(today, mood, energy, workload)
    check_ins.append(new_check_in) #Add the new check-in to the list
    save_checkin(new_check_in) #Save the new check-in to the file
    refresh_score_label() #Refresh the score label to show the updated burnout risk score and level
    messagebox.showinfo("Saved", "Your check-in has been saved.")

#Submit button that calls collect_entries when clicked
tk.Button(root, text="Submit check-in", command=collect_entries).pack(pady=5)

#Function to open a new window that displays the history of check-ins
def open_history():
    history_window = tk.Toplevel(root) #Create a new window for the history of check-ins
    history_window.title("Flare Check-in History") #Set the title of the history window
    history_window.geometry("250x250") #Set the size of the history window

    tk.Label(history_window, text="Check-in History", font=("Arial", 14)).pack(pady=10) #Label for the history window

    if not check_ins:
        tk.Label(history_window, text="No check-ins yet.").pack(pady=10) #If there are no check-ins, show a message
    else:
        for check_in in check_ins:
            text = f"{check_in.date}: {risk_level_for(check_in)}" #Format the check-in data for display
            tk.Label(history_window, text=text, anchor="w").pack(fill="x", padx=20) #Display each check-in in the history window

#Function to open a new window that displays a notice based on the current burnout risk score
def open_notice():
    notice_window = tk.Toplevel() #Create a new window for the notice
    notice_window.title("Flare - Notice") #Set the title of the notice window
    notice_window.geometry("250x150") #Set the size of the notice window
    score = calculate_risk_score(check_ins)
    level = risk_level_from_score(score)

    if level == "high": #If the burnout risk level is high, show a message to the user
        message = "Your check-ins show a high burnout risk. Consider taking a break."
    else: #If the burnout risk level is moderate or low, show a message to the user
        message = "Your burnout risk is not currently high. Keep checking in daily."
    
    tk.Label(notice_window, text=message, wraplength=200, justify="center").pack(pady=20, padx=10) #Display the notice message in the notice window

tk.Button(root, text="View History", command=open_history).pack(pady=5) #Button that opens the history window when clicked
tk.Button(root, text="View Notice", command=open_notice).pack(pady=5) #Button that opens the notice window when clicked

refresh_score_label() #Refresh the score label when the program starts to show the current burnout risk score and level

root.mainloop() #Start the Tkinter to run the GUI