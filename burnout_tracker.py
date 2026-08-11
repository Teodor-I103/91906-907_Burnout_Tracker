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
    check_ins = []
    with open(filename, "r") as file:
        for line in file:
            date, mood, energy, workload = line.split(",")
            check_ins.append(Check_In(date, int(mood), int(energy), int(workload)))
    return check_ins

def save_checkin(check_in, filename=FILENAME):
    with open(filename, "w") as file:
            file.write(check_in.daily_check_in() + "\n")