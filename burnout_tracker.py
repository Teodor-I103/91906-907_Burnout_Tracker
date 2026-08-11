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