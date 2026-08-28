import tkinter as tk #Import Tkinter for the GUI
from tkinter import messagebox #Import messagebox for pop-up validation and information messages
import datetime #datetime module to get the current date for check-ins
"""
Note for marker:
You must have the cryptography library installed to run my application.
Check README.md for instructions on how to install it.
"""
from cryptography.fernet import Fernet #Import Fernet for password encryption and decryption

#Named Constants used throughout the app
FILENAME, USERS_FILENAME, KEY_FILENAME = "check_ins.txt", "users.txt", "secret.key"
UPPER_BOUNDARY = 5 #Highest possible rating for mood, energy, and workload
LOWER_BOUNDARY = 1 #Lowest possible rating for mood, energy, and workload
MIN_SCORE = 0 #Lowest possible burnout risk score
MAX_SCORE = 100 #Highest possible burnout risk score
HIGH_RISK_SCORE = 65 #Score threshold for high burnout risk
MODERATE_RISK_SCORE = 35 #Score threshold for moderate burnout risk
WEEK, MONTH = 7, 30
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
        self.username = username #Username of the user who made the check-in
        self.date = date #Date of the check-in
        self.mood = mood #Mood rating (1-5)
        self.energy = energy
        self.workload = workload

    #Method to format the check-in data as a string for saving to the file
    def daily_check_in(self):
        return f"{self.username},{self.date},{self.mood},{self.energy},{self.workload}"

#Function to load the encryption key from a file, or create a new one if it doesn't exist.
def load_or_create_key(filename=KEY_FILENAME):
    try:
        with open(filename, "rb") as file:
            return file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(filename, "wb") as file:
            file.write(key)
        return key

fernet = Fernet(load_or_create_key()) #Create a Fernet object for encrypting and decrypting passwords using the loaded or newly created key.

#Functions for loading and saving user data and check-ins to files
def load_users(filename=USERS_FILENAME):
    users = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                username, encrypted_password = line.strip().split(",")
                users[username] = encrypted_password
    except FileNotFoundError:
        pass
    return users

#Function to save a new user to the users file
def save_user(username, encrypted_password, filename=USERS_FILENAME):
    with open(filename, "a") as file:
        file.write(f"{username},{encrypted_password}\n") #Append the new user's username and encrypted password to the users file

#Function to load all check-ins from the check-in save file
def load_check_ins(filename=FILENAME):
    check_ins = []
    try:
        with open(filename, "r") as file:
            for line in file:
                username, date, mood, energy, workload = line.strip().split(",")
                check_ins.append(Check_In(username, date, int(mood), int(energy), int(workload))) #Load each check-in from the file and create a Check_In object, adding it to the list of check-ins
    except FileNotFoundError:
        pass
    return check_ins

#Function to save all check-ins to the check-in save file
def save_all_checkins(all_checkins, filename=FILENAME):
    with open(filename, "w") as file:
        for check_in in all_checkins:
            file.write(check_in.daily_check_in() + "\n") #Write each check-in's data to the file, one per line, using the daily_check_in method to format it correctly.

#Function to ensure that the burnout risk score is between 0 and 100
def limit_score(score):
    if score < MIN_SCORE:
        return MIN_SCORE
    elif score > MAX_SCORE:
        return MAX_SCORE
    return score

#Calculates the average burnout risk score based on the last 7 days of check-ins. If there are no check-ins, it returns a score of 0.
def calculate_average_score(check_ins, days):
    if not check_ins:
        return 0
    recent = check_ins[-days:]
    total = 0
    for check_in in recent:
        total += (UPPER_BOUNDARY - check_in.mood) + (UPPER_BOUNDARY - check_in.energy) + check_in.workload
    average = total / len(recent)
    return limit_score(int((average / MAX_TOTAL_SCORE) * 100))
   
#Turns the numeric risk score into a string of "Low", "Moderate", or "high"
def risk_level_from_score(score):
    if score >= HIGH_RISK_SCORE: #If the score is above the high risk threshold, return "high"
        return "high"
    elif score >= MODERATE_RISK_SCORE: #If the score is above the moderate risk threshold, return "moderate"
        return "moderate"
    return "low"

#Calculates the burnout risk score for a single check-in, based on the mood, energy, and workload ratings.
def score_for(check_in):
    total = (UPPER_BOUNDARY - check_in.mood) + (UPPER_BOUNDARY - check_in.energy) + check_in.workload
    return limit_score(int((total / MAX_TOTAL_SCORE) * 100))

#Returns the colour associated with a given burnout risk level, for use in the GUI.
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

#Creates a styled button with a primary colour background, white text, and bold font.
def styled_button(parent, text, command, bg=PRIMARY, fg="white", active_bg=PRIMARY_DARK):
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg, activebackground=active_bg,
                      activeforeground=fg, relief="flat", font=("Arial", 10, "bold"), padx=10, pady=6, bd=0)

#Creates a styled entry box with a white background, solid border, and custom text colour.
def styled_entry(parent, width=18, show=None):
    return tk.Entry(parent, width=width, show=show, bg="white", fg=TEXT_COLOR, relief="solid", bd=1,
                     highlightthickness=1, highlightbackground="#DAD6F5", highlightcolor=PRIMARY)

#Creates a label and an entry box in a single row, with the label on the left and the entry on the right.
def labeled_entry(parent, row, label_text, width=18, show=None, prefill=None):
    tk.Label(parent, text=label_text, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row, column=0, sticky="e", padx=(20, 10), pady=6)
    entry = styled_entry(parent, width=width, show=show)
    if prefill is not None: #If a prefill value is provided, insert it into the entry box when creating it.
        entry.insert(0, str(prefill))
    entry.grid(row=row, column=1, sticky="w", padx=(0, 20), pady=6)
    return entry

def rating_description(parent, row, text):
    # Small helper text placed under a rating entry, e.g. explaining what 1 vs 5 means
    tk.Label(parent, text=text, font=("Arial", 8), bg=BG_COLOR, fg=SUBTEXT_COLOR).grid(row=row, column=0, columnspan=2, pady=(0, 6))

all_checkins = load_check_ins()
users = load_users()
open_popups = [] #List to keep track of all open pop-up windows, so they can be closed when logging out.

root = tk.Tk()
root.title("Flare")
root.geometry("340x580")

#Clear the main window of all widgets, used when switching between login and main screens.
def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

#Close all open pop-up windows, used when logging out to ensure no pop-ups remain open.
def close_all_popups():
    for popup in open_popups:
        if popup.winfo_exists():
            popup.destroy()
    open_popups.clear() #Clear the list of open pop-ups after closing them all.

#Builds the login screen with username and password entry fields, and buttons for logging in or signing up.
def build_login_screen():
    clear_screen()
    root.configure(bg=BG_COLOR)
    tk.Label(root, text="Flare", font=("Arial", 20, "bold"), bg=BG_COLOR, fg=PRIMARY).grid(row=0, column=0, columnspan=2, pady=(30, 20))

    username_entry = labeled_entry(root, 1, "Username:")
    password_entry = labeled_entry(root, 2, "Password:", show="*")

    #Functions for handling login and sign-up actions, validation and saving new users.
    def on_login():
        username, password = username_entry.get().strip(), password_entry.get().strip()
        if username not in users:
            messagebox.showerror("Login failed", "Incorrect username or password.")
            return
        decrypted_password = fernet.decrypt(users[username].encode()).decode() #Decrypt the stored password for the given username using the Fernet object and compares it to the entered password.
        if decrypted_password != password:
            messagebox.showerror("Login failed", "Incorrect username or password.")
            return
        build_main_screen(username)

    #Function for handling sign-up action, validation and saving new users.
    def open_signup():
        signup_window = tk.Toplevel(root)
        signup_window.title("Flare - Sign Up")
        signup_window.geometry("260x220")
        signup_window.configure(bg=BG_COLOR)

        su_username_entry = labeled_entry(signup_window, 0, "Username:")
        su_password_entry = labeled_entry(signup_window, 1, "Password:", show="*")

        #Function for creating a new account, validating the input, encrypting the password, saving the new user, and closing the sign-up window.
        def on_create_account():
            username, password = su_username_entry.get().strip(), su_password_entry.get().strip()
            if username == "" or password == "":
                messagebox.showerror("Invalid input", "Username and password cannot be empty.")
                return
            if username in users:
                messagebox.showerror("Invalid input", "That username is already taken.")
                return
            encrypted_password = fernet.encrypt(password.encode()).decode()
            users[username] = encrypted_password
            save_user(username, encrypted_password) #Save the new user's username and encrypted password to the users file
            messagebox.showinfo("Account created", f"Account '{username}' created. You can now log in.")
            signup_window.destroy() #Close the sign-up window after successfully creating the account.

        styled_button(signup_window, "Create Account", on_create_account).grid(row=2, column=0, columnspan=2, pady=15)

    #Create and place the login and sign-up buttons on the login screen.
    styled_button(root, "Login", on_login).grid(row=3, column=0, columnspan=2, pady=(20, 6))
    styled_button(root, "Sign Up", open_signup, bg=CARD_BG, fg=PRIMARY, active_bg="#E4EAF2").grid(row=4, column=0, columnspan=2, pady=6)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

#Builds the main screen after a successful login, allowing the user to submit check-ins, view history, and see their burnout risk score.
def build_main_screen(username):
    clear_screen()
    root.configure(bg=BG_COLOR)
    tk.Label(root, text=f"Logged in as: {username}", font=("Arial", 8), bg=BG_COLOR, fg=SUBTEXT_COLOR).grid(row=0, column=0, columnspan=2, pady=(15, 10))

    mood_entry = labeled_entry(root, 1, "😊 Mood (1-5):", width=10)
    rating_description(root, 2, "1 = very low, 5 = feeling great")

    energy_entry = labeled_entry(root, 3, "⚡ Energy (1-5):", width=10)
    rating_description(root, 4, "1 = exhausted, 5 = fully energised")

    workload_entry = labeled_entry(root, 5, "📚 Workload (1-5):", width=10)
    rating_description(root, 6, "1 = light, 5 = heavy (several deadlines)")
    
    score_label = tk.Label(root, text="", font=("Arial", 14, "bold"), bg=BG_COLOR)
    score_label.grid(row=8, column=0, columnspan=2, pady=10)

    tk.Label(root, text="For more information, click 'Notice'", font=("Arial", 8, "italic"),
                 bg=BG_COLOR, fg=SUBTEXT_COLOR).grid(row=9, column=0, columnspan=2, pady=(0, 6))

    stats_label = tk.Label(root, text="", font=("Arial", 9), bg=BG_COLOR, fg=TEXT_COLOR, justify="center")
    stats_label.grid(row=10, column=0, columnspan=2, pady=(0, 10))
    
    #Returns a list of all check-ins for the currently logged-in user, used to calculate their burnout risk score and display their history.
    def user_checkins():
        result = []
        for c in all_checkins:
            if c.username == username:
                result.append(c) #Append the check-in to the result list if it belongs to the currently logged in user
        return result

    #Refreshes the burnout risk score label on the main screen, calculating the score based on the user's check-ins and updating the label text and colour accordingly.
    def refresh_score_label():
        entries = user_checkins()

        week_score = calculate_average_score(entries, WEEK)
        week_level = risk_level_from_score(week_score)
        score_label.config(text=f"Burnout risk (7-day): {week_score} - {week_level}", fg=score_colour(week_level))

        today_score = score_for(entries[-1]) if entries else 0 #If there are check-ins, get the score for the most recent one.
        today_level = risk_level_from_score(today_score)
        month_score = calculate_average_score(entries, MONTH)
        month_level = risk_level_from_score(month_score)
        stats_label.config(
            text=f"Today: {today_score} - {today_level}\n"
                 f"Past week: {week_score} - {week_level}\n"
                 f"Monthly avg: {month_score} - {month_level}"
        )

    #Collects the user's check-in entries from the entry fields, validates them, creates a new Check_In object, saves it to the file, and refreshes the burnout risk score label.
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

    #Create and place the submit button for the check-in entries on the main screen.
    styled_button(root, "Submit check-in", collect_entries).grid(row=11, column=0, columnspan=2, pady=(5, 12))

    #Functions for opening the history and notice pop-up windows, allowing the user to view their check-in history and receive a notice about their burnout risk level.
    def open_history():
        history_window = tk.Toplevel(root)
        open_popups.append(history_window)
        history_window.title("Flare Check-in History")
        history_window.geometry("340x360")
        history_window.configure(bg=BG_COLOR)
        tk.Label(history_window, text="Check-in History", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, columnspan=3, pady=10)

        rows_frame = tk.Frame(history_window, bg=BG_COLOR)
        rows_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10)

        #Function for building the rows of check-in history in the history pop-up window, displaying each check-in's date, score, risk level, and ratings.
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
                text = f"{check_in.date}: {score}-{level}  (M{check_in.mood} E{check_in.energy} W{check_in.workload})"

                tk.Label(rows_frame, text=text, anchor="w", bg=BG_COLOR, fg=score_colour(level),
                         font=("Arial", 8, "bold")).grid(row=row_index, column=0, sticky="w", pady=3)
                
                tk.Button(rows_frame, text="Edit", command=lambda check_in=check_in: open_edit(check_in), bg=PRIMARY,
                          fg="white", relief="flat", font=("Arial", 8), padx=6).grid(row=row_index, column=1, padx=2)
                
                tk.Button(rows_frame, text="Delete", command=lambda check_in=check_in: delete_checkin(check_in),
                          bg=DANGER, fg="white", relief="flat", font=("Arial", 8), padx=6).grid(row=row_index, column=2, padx=2)
                
        #Functions for deleting and editing check-ins, allowing the user to manage their check-in history from the history pop-up window.
        def delete_checkin(check_in):
            all_checkins.remove(check_in)
            save_all_checkins(all_checkins)
            refresh_score_label()
            build_rows()

        #Function for opening the edit pop-up window, allowing the user to modify the mood, energy, and workload ratings of a specific check-in.
        def open_edit(check_in):
            edit_window = tk.Toplevel(history_window)
            edit_window.title("Edit check-in")
            edit_window.geometry("240x260")
            edit_window.configure(bg=BG_COLOR)
            edit_mood = labeled_entry(edit_window, 0, "Mood (1-5):", width=10, prefill=check_in.mood)
            edit_energy = labeled_entry(edit_window, 1, "Energy (1-5):", width=10, prefill=check_in.energy)
            edit_workload = labeled_entry(edit_window, 2, "Workload (1-5):", width=10, prefill=check_in.workload)

            #Function for saving the edited check-in, validating the new ratings, updating the Check_In object, saving all check-ins to the file, and refreshing the burnout risk score label.
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

            #Create and place the save button for the edited check-in on the edit pop-up window.
            styled_button(edit_window, "Save", save_edit).grid(row=3, column=0, columnspan=2, pady=15)

        build_rows() #Build the initial rows of check-in history when the history pop-up window is opened.

    #Function for opening the notice pop-up window, displaying a message about the user's burnout risk level based on their check-ins.
    def open_notice():
        notice_window = tk.Toplevel(root)
        open_popups.append(notice_window)
        notice_window.title("Flare - Notice")
        notice_window.geometry("260x160")
        notice_window.configure(bg=BG_COLOR)
        level = risk_level_from_score(calculate_average_score(user_checkins(), WEEK))
        if level == "high":
            message = "Your check-ins show a high burnout risk. Consider taking a break."
        else:
            message = "Your burnout risk is not currently high. Keep checking in daily."
        tk.Label(notice_window, text=message, wraplength=210, justify="center", bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, padx=15, pady=25)

    #Create and place the buttons for viewing history and viewing notice on the main screen.
    styled_button(root, "View History", open_history, bg=CARD_BG, fg=PRIMARY, active_bg="#E4EAF2").grid(row=12, column=0, columnspan=2, pady=5)
    styled_button(root, "View Notice", open_notice, bg=CARD_BG, fg=PRIMARY, active_bg="#E4EAF2").grid(row=13, column=0, columnspan=2, pady=5)

    #Function for logging out, closing all pop-up windows, and returning to the login screen.
    def logout():
        close_all_popups()
        build_login_screen()

    #Create and place the logout button on the main screen, allowing the user to log out and return to the login screen.
    styled_button(root, "Logout", logout, bg=DANGER, active_bg=DANGER_DARK).grid(row=14, column=0, columnspan=2, pady=(15, 20))
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    refresh_score_label() #Refresh the burnout risk score when the main screen launches.
    
build_login_screen() #Start the app by building the login screen when the program is run.
root.mainloop() #Start the Tkinter loop.