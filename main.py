import tkinter as tk
from tkinter import StringVar, filedialog
import pathlib
import os
import json
from tkinter import messagebox
from tkinter.simpledialog import askstring

DESKTOP = pathlib.Path.home() / 'Desktop'

with open ("saved_groups.json", "r", encoding="utf-8") as file:
    groups = json.load(file)



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

    add_file_button = tk.Button(text="Add File", command=lambda:[add_file(current_group.get()),update_file_list()])
    add_file_button.place(x=600, y=100)

    add_folder_button = tk.Button(text="Add Folder", command=lambda:[add_folder(current_group.get()), update_file_list()])
    add_folder_button.place(x=600, y=130)

    remove_entry_button = tk.Button(text="Remove Entry", command=lambda:[remove_entry(get_file_selection(),current_group.get()),update_file_list()])
    remove_entry_button.place(x=600, y=160)

    add_group_button = tk.Button(text="Add File Group", command=lambda:[add_group(), update_group_list()])
    add_group_button.place(x=255, y=100)

    remove_group_button = tk.Button(text="Remove Group", command=lambda:[remove_group(get_group_selection()), update_file_list()])
    remove_group_button.place(x=255, y=130)

    def add_group():
        new_group = askstring("New Group", "Name file group:")
        if new_group != None:
            if new_group in groups:
                messagebox.showerror("Error", "A group with that name already exists!")
            else:
                groups[new_group] = {}
                write_json(groups)

    def remove_group(group):
        if group != None:
            del groups[group]
            write_json(groups)
            update_group_list()
            current_group.set(get_group_selection())


    def add_file(group):
        filepath = filedialog.askopenfilename(initialdir=DESKTOP, title="Select File", 
                                            filetypes=[("All Files", "*.*")])
        try:
            if filepath != "":
                get_filename = filepath.split("/",-2)
                filename = get_filename[-2]+"/"+get_filename[-1]
                groups[group][filepath] = filename
                write_json(groups)
        except:
            messagebox.showerror("Error", "Cannot add file if no group is selected!")

    def add_folder(group):
        folderpath = filedialog.askdirectory(initialdir=DESKTOP, title="Select Folder")
        try:
            if folderpath != "":
                get_foldername = folderpath.split("/")
                foldername = get_foldername[-1]
                groups[group][folderpath] = foldername
                write_json(groups)
        except:
            messagebox.showerror("Error", "Cannot add folder if no group is selected!")

    def remove_entry(entry, group):
        if entry != None:
            get_index = list(groups[group])
            del groups[group][get_index[entry]]
            write_json(groups)


    file_list = StringVar()
    file_listbox = tk.Listbox(listvariable=file_list, width=40, selectmode="SINGLE", exportselection=False)
    file_listbox.place(x=350, y=100)

    group_list = StringVar(value=[group for group in groups])
    group_listbox = tk.Listbox(listvariable=group_list, width=40, selectmode="SINGLE", exportselection=True)
    group_listbox.place(x=5, y=100)

    current_group = StringVar()


    def group_listbox_on_select(event):
        e = event.widget
        group = e.get(e.curselection())
        file_list.set([k for k, v in groups[group].items()])
        current_group.set(e.get(e.curselection()))


    group_listbox.bind('<<ListboxSelect>>', group_listbox_on_select)

    def get_group_selection():
        if group_listbox.curselection() != ():
            return group_listbox.get(group_listbox.curselection())

    def get_file_selection():
        if file_listbox.curselection() != ():
            return file_listbox.curselection()[0]

    def update_file_list():
        if current_group.get() != "":
            if current_group.get() in groups:
                file_list.set([k for k, v in groups[current_group.get()].items()])
            else:
                file_list.set([])

    def update_group_list():
        group_list.set([group for group in groups])

    test_button = tk.Button(text="TEST", command=lambda:[testasd()])
    test_button.place(x=255, y=350)

    def testasd():
        asd = askstring("AAA", "AAAAAAAAAAAAAAAAAAAAAAA")
        print(asd)

    root.mainloop()

draw_gui()
