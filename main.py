import tkinter as tk
from tkinter import StringVar, filedialog
import pathlib
import os
import json

DESKTOP = pathlib.Path.home() / 'Desktop'

with open ("saved_groups.json", "r", encoding="utf-8") as file:
    groups = json.load(file)

def add_file():
    filepath = filedialog.askopenfilename(initialdir=DESKTOP, title="Select File", 
                                         filetypes=[("All Files", "*.*")])
    get_filename = filepath.split("/",-2)
    filename = get_filename[-2]+"/"+get_filename[-1]
    if filepath != "":
        groups["new"][filepath] = filename
        write_json(groups)

def add_folder():
    folderpath = filedialog.askdirectory(initialdir=DESKTOP, title="Select Folder")
    get_foldername = folderpath.split("/")
    foldername = get_foldername[-1]
    if folderpath != "":
        groups["new"][folderpath] = foldername
        write_json(groups)

def write_json(write_to_json):
    with open ("saved_groups.json", "w") as file:
        json.dump(write_to_json, file, indent=2, ensure_ascii=False)

def draw_gui():
    """Construct the GUI for the application."""
    root = tk.Tk()
    root.title("Open Group Of Files")

    #Create 700x400 unresizable GUI roughly in the middle of the screen (80px north of center)
    w = 700
    h = 400
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2) - 0
    y = (hs/2) - (h/2) - 80
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.resizable(width=False, height=False)

    add_file_button = tk.Button(text="Add File", command=add_file)
    add_file_button.place(x=100, y=100)

    add_folder_button = tk.Button(text="Add Folder", command=add_folder)
    add_folder_button.place(x=100, y=130)

    root.mainloop()

draw_gui()
