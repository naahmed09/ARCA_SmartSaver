
# This file was generated by the Tkinter Designer by Parth Jadhav
# https://github.com/ParthJadhav/Tkinter-Designer


from pathlib import Path
import FE_FriendlyMain as backend
import tkinter as tk
# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import sys
import time


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets/frame4")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

import subprocess

def run_script(script_path):
    """Runs the gui1.py script in a separate process."""
    try:
        python_executable = sys.executable
        subprocess.Popen([python_executable, script_path])
        print("gui1.py started in a separate process.")
    except FileNotFoundError:
        print("Error: gui1.py not found.")
    except Exception as e:
        print(f"An error occurred while trying to run gui1.py: {e}")


window = Tk()

window.geometry("1920x1080+0+0")
window.configure(bg = "#FFFFFF")


canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 1080,
    width = 1920,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: run_script('gui1.py'),
    relief="flat"
)
button_1.place(
    x=0.0,
    y=953.0,
    width=308.0,
    height=115.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: run_script('gui5.py'),
    relief="flat"
)
button_2.place(
    x=565.0,
    y=757.0,
    width=711.0,
    height=126.0
)

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    959.0,
    127.0,
    image=image_image_1
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    958.0,
    253.0,
    image=image_image_2
)

income_data = backend.read_csv_data_list("DBs/income_data.csv")

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: backend.open_income(root, income_data),
    relief="flat"
)
button_3.place(
    x=465.0,
    y=487.0,
    width=436.0,
    height=198.0
)

root = tk.Tk()
expense_data = backend.read_csv_data_list("DBs/expense_data.csv")

button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: backend.open_expenses(root, expense_data),
    relief="flat"
)
button_4.place(
    x=980.0,
    y=487.0,
    width=436.0,
    height=198.0
)
window.resizable(False, False)
window.mainloop()
