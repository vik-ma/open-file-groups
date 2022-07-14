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
    if filepath != "":
        get_filename = filepath.split("/",-2)
        filename = get_filename[-2]+"/"+get_filename[-1]
        groups["new"][filepath] = filename
        write_json(groups)

def add_folder():
    folderpath = filedialog.askdirectory(initialdir=DESKTOP, title="Select Folder")
    if folderpath != "":
        get_foldername = folderpath.split("/")
        foldername = get_foldername[-1]
        groups["new"][folderpath] = foldername
        write_json(groups)

def remove_entry(entry):
    if entry != None:
        get_index = list(groups["new"])
        del groups["new"][get_index[entry]]
        write_json(groups)

def add_group(new_group):
    groups[new_group] = {}
    write_json(groups)

def remove_group(group):
    del groups[group]
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

    add_file_button = tk.Button(text="Add File", command=lambda:[add_file(),update_file_list()])
    add_file_button.place(x=100, y=100)

    add_folder_button = tk.Button(text="Add Folder", command=lambda:[add_folder(), update_file_list()])
    add_folder_button.place(x=100, y=130)

    remove_entry_button = tk.Button(text="Remove Entry", command=lambda:[remove_entry(get_file_selection()),update_file_list()])
    remove_entry_button.place(x=100, y=160)

    add_group_entry = tk.Entry(width=30)
    add_group_entry.place(x=250, y=70)
    add_group_button = tk.Button(text="Add File Group", command=lambda:[add_group(add_group_entry.get())])
    add_group_button.place(x=250, y=100)

    remove_group_button = tk.Button(text="Remove Group", command=lambda:[remove_group(add_group_entry.get())])
    remove_group_button.place(x=250, y=130)


    file_list = StringVar(value=[k for k, v in groups["new"].items()])
    file_listbox = tk.Listbox(listvariable=file_list, width=40, selectmode="SINGLE")
    file_listbox.place(x=450, y=100)

    def get_file_selection():
        if file_listbox.curselection() != ():
            return file_listbox.curselection()[0]

    def update_file_list():
        file_list.set([k for k, v in groups["new"].items()])

    root.mainloop()

draw_gui()
