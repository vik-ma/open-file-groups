import tkinter as tk
from tkinter import BooleanVar, StringVar, filedialog, messagebox
from tkinter.simpledialog import askstring
import pathlib
import os
import json

DESKTOP = pathlib.Path.home() / 'Desktop'

has_json = pathlib.Path("saved_groups.json").exists()


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

    lastdir = StringVar(value=groups["_SETTINGS_"]["lastdir"])

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
        filepath = filedialog.askopenfilename(initialdir=lastdir.get(), title="Select File", 
                                            filetypes=[("All Files", "*.*")])
        try:
            if filepath != "":
                get_filename = filepath.split("/")
                filename = get_filename[-2]+"/"+get_filename[-1]
                groups[group][filepath] = filename
                get_dir = filepath.rsplit("/",1)[0]
                groups["_SETTINGS_"]["lastdir"] = get_dir
                lastdir.set(get_dir)
                write_json(groups)
        except:
            messagebox.showerror("Error", "Cannot add file if no group is selected!")

    def add_folder(group):
        folderpath = filedialog.askdirectory(initialdir=lastdir.get(), title="Select Folder")
        try:
            if folderpath != "":
                get_foldername = folderpath.split("/")
                foldername = get_foldername[-1]
                groups[group][folderpath] = foldername
                get_dir = folderpath.rsplit("/",1)[0]
                groups["_SETTINGS_"]["lastdir"] = get_dir
                lastdir.set(get_dir)
                write_json(groups)
        except:
            messagebox.showerror("Error", "Cannot add folder if no group is selected!")

    def remove_entry(entry, group):
        if entry != None:
            get_index = list(groups[group])
            del groups[group][get_index[entry]]
            write_json(groups)

    current_group = StringVar(value="None")

    selected_group_label = tk.Label(text="Selected Group:", font="arial 13 bold")
    selected_group_label.place(x=350, y=50)
    current_group_label = tk.Label(textvariable=current_group, font="arial 13 bold", fg="#166edb")
    current_group_label.place(x=350, y=70)

    file_list = StringVar()
    file_listbox = tk.Listbox(listvariable=file_list, width=40, selectmode="SINGLE", exportselection=False)
    file_listbox.place(x=350, y=100)

    group_list = StringVar(value=[group for group in groups][1::])
    group_listbox = tk.Listbox(listvariable=group_list, width=40, selectmode="SINGLE", exportselection=True)
    group_listbox.place(x=5, y=100)

    


    def group_listbox_on_select(event):
        e = event.widget
        group = e.get(e.curselection())
        if toggle_filepath_state.get() is True:
            file_list.set([k for k, v in groups[group].items()])
        else:
            file_list.set([v for k, v in groups[group].items()])
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
                if toggle_filepath_state.get() is True:
                    file_list.set([k for k, v in groups[current_group.get()].items()])
                else:
                    file_list.set([v for k, v in groups[current_group.get()].items()])
            else:
                file_list.set([])

    def update_group_list():
        group_list.set([group for group in groups][1::])

    toggle_filepath_state = BooleanVar()
    toggle_filepath_state.set(groups["_SETTINGS_"]["show_full_filepath"])
    
    toggle_filepath_button_text = StringVar()

    def show_filepath_button(state):
        if state is True:
            toggle_filepath_button_text.set("Toggle Shorter Filepath")
        else:
            toggle_filepath_button_text.set("Toggle Full Filepath")

    show_filepath_button(toggle_filepath_state.get())

    toggle_filepath_button = tk.Button(textvariable=toggle_filepath_button_text, command=lambda:[toggle_filepath()])
    toggle_filepath_button.place(x=350, y=270)

    def toggle_filepath():
        new_state = toggle_filepath_state.get()
        if new_state is True:
            new_state = False
        else:
            new_state = True
        toggle_filepath_state.set(new_state)
        show_filepath_button(new_state)
        groups["_SETTINGS_"]["show_full_filepath"] = new_state
        write_json(groups)
        update_file_list()

    def open_files():
        group = current_group.get()
        if group != "None" and group != "":
            for k, v in groups[group].items():
                os.startfile(k)
        else:
            messagebox.showerror("Error", "Must select a group to open from!")

    open_button = tk.Button(text="Open Files", bg="#3599e6", fg="#1c1c1c", 
                            font="arial 18 bold", command=open_files)
    open_button.place(x=550, y=5)

    test_button = tk.Button(text="TEST", command=lambda:[testasd()])
    test_button.place(x=50, y=30)


    def testasd():
        print(current_group.get())

    root.mainloop()



if has_json:
    with open ("saved_groups.json", "r", encoding="utf-8") as file:
        groups = json.load(file)
    draw_gui()
else:
    settings = {
        "show_full_filepath": True,
        "lastdir": str(DESKTOP)
        }
    json_content = {"_SETTINGS_":settings}
    write_json(json_content)
    with open ("saved_groups.json", "r", encoding="utf-8") as file:
        groups = json.load(file)
    draw_gui()

#draw_gui()
