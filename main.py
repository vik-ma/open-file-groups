from enum import auto
import tkinter as tk
from tkinter import BooleanVar, StringVar, filedialog, messagebox
from tkinter.simpledialog import askstring
import pathlib
import os
import json

DESKTOP = pathlib.Path.home() / 'Desktop'
HOMEFOLDER = pathlib.Path.home()

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

    gbw = 120
    fbw = 100

    add_group_button = tk.Button(text="Create New Group", command=lambda:[add_group()])
    add_group_button.place(x=195, y=100, width=gbw)

    remove_group_button = tk.Button(text="Delete Group", command=lambda:[remove_group(get_group_selection())])
    remove_group_button.place(x=195, y=130, width=gbw)

    move_group_up_button = tk.Button(text="Move Group Up", command=lambda:[move_group_up(get_group_index())])
    move_group_up_button.place(x=195, y=160, width=gbw)

    move_group_down_button = tk.Button(text="Move Group Down", command=lambda:[move_group_down(get_group_index())])
    move_group_down_button.place(x=195, y=190, width=gbw)

    rename_group_button = tk.Button(text="Rename Group", command=lambda:[rename_group(get_group_selection())])
    rename_group_button.place(x=195, y=220, width=gbw)
    
    add_file_button = tk.Button(text="Add File", command=lambda:[add_file(current_group.get())])
    add_file_button.place(x=580, y=100, width=fbw)

    add_folder_button = tk.Button(text="Add Folder", command=lambda:[add_folder(current_group.get())])
    add_folder_button.place(x=580, y=130, width=fbw)

    remove_entry_button = tk.Button(text="Remove Entry", command=lambda:[remove_entry(get_file_selection(),current_group.get())])
    remove_entry_button.place(x=580, y=160, width=fbw)
    
    move_file_up_button = tk.Button(text="Move File Up", command=lambda:[move_file_up(get_file_selection(), get_group_selection())])
    move_file_up_button.place(x=580, y=190, width=fbw)

    move_file_down_button = tk.Button(text="Move File Down", command=lambda:[move_file_down(get_file_selection(), get_group_selection())])
    move_file_down_button.place(x=580, y=220, width=fbw)

    autoclose = tk.BooleanVar(value=groups["_SETTINGS_"]["autoclose"])
    save_group = tk.BooleanVar(value=groups["_SETTINGS_"]["save_group"])
    remove_warn_group = tk.BooleanVar(value=groups["_SETTINGS_"]["remove_warn_group"])
    remove_warn_files = tk.BooleanVar(value=groups["_SETTINGS_"]["remove_warn_files"])

    autoclose_checkbox = tk.Checkbutton(text="Close Program After Opening", variable=autoclose, onvalue=True, offvalue=False)
    save_group_checkbox = tk.Checkbutton(text="Automatically select current group next time program is opened", variable=save_group, onvalue=True, offvalue=False)
    warn_group_checkbox = tk.Checkbutton(text="Warn before trying to delete group", variable=remove_warn_group, onvalue=True, offvalue=False)
    warn_files_checkbox = tk.Checkbutton(text="Warn before trying to delete file or folder", variable=remove_warn_files, onvalue=True, offvalue=False)

    autoclose_checkbox.place(x=5, y=5)
    save_group_checkbox.place(x=5, y=25)
    warn_group_checkbox.place(x=5, y=45)
    warn_files_checkbox.place(x=5, y=65)

    lastdir = StringVar(value=groups["_SETTINGS_"]["lastdir"])
    vlcrcpath = StringVar(value=groups["_SETTINGS_"]["vlcrc_path"])

    def add_group():
        new_group = askstring("New Group", "Name file group:")
        if new_group != None:
            if new_group in groups:
                messagebox.showerror("Error", "A group with that name already exists!")
            else:
                groups[new_group] = {}
                write_json(groups)
                update_group_list()

    def remove_group(group):
        if group != None:
            msgbox_warning = ""
            if remove_warn_group.get() is True:
                msgbox_warning = messagebox.askquestion("Warning", f"Do you really want to delete {group}?")
            if msgbox_warning == "yes" or remove_warn_group.get() is False:
                del groups[group]
                write_json(groups)
                update_group_list()
                current_group.set(get_group_selection())
                update_file_list()


    def add_file(group):
        if get_group_selection() != None:
            filepath = filedialog.askopenfilename(initialdir=lastdir.get(), title="Select File", 
                                                filetypes=[("All Files", "*.*")])
            if filepath != "":
                get_filename = filepath.split("/")
                filename = get_filename[-2]+"/"+get_filename[-1]
                groups[group][filepath] = filename
                get_dir = filepath.rsplit("/",1)[0]
                groups["_SETTINGS_"]["lastdir"] = get_dir
                lastdir.set(get_dir)
                write_json(groups)
                update_file_list()
        else:
            messagebox.showerror("Error", "Select a group to add file to first!")

    def add_folder(group):
        if get_group_selection() != None:
            folderpath = filedialog.askdirectory(initialdir=lastdir.get(), title="Select Folder")
            if folderpath != "":
                get_foldername = folderpath.split("/")
                foldername = get_foldername[-1]
                groups[group][folderpath] = foldername
                get_dir = folderpath.rsplit("/",1)[0]
                groups["_SETTINGS_"]["lastdir"] = get_dir
                lastdir.set(get_dir)
                write_json(groups)
                update_file_list()
        else:
            messagebox.showerror("Error", "Select a group to add folder to first!")

    def remove_entry(entry, group):
        if entry != None:
            get_index = list(groups[group])
            get_entry = groups[group][get_index[entry]]
            msgbox_warning = ""
            if remove_warn_files.get() is True:
                msgbox_warning = messagebox.askquestion("Warning", f"Do you really want to remove {get_entry}?")
            if msgbox_warning == "yes" or remove_warn_files.get() is False:
                del groups[group][get_index[entry]]
                write_json(groups)
                update_file_list()

    current_group = StringVar(value=groups["_SETTINGS_"]["saved_group"])



    selected_group_label = tk.Label(text="Selected Group:", font="arial 13 bold")
    selected_group_label.place(x=330, y=50)
    current_group_label = tk.Label(textvariable=current_group, font="arial 13 bold", fg="#166edb")
    current_group_label.place(x=330, y=70)

    file_list = StringVar()
    file_listbox = tk.Listbox(listvariable=file_list, width=40, selectmode="SINGLE", exportselection=False, activestyle="none")
    file_listbox.place(x=330, y=100)

    group_list = StringVar(value=[group for group in groups][1::])
    group_listbox = tk.Listbox(listvariable=group_list, width=30, selectmode="SINGLE", exportselection=True, activestyle="none")
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

    def get_group_index():
        if group_listbox.curselection() != ():
            return group_listbox.curselection()

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



    def move_group_up(lower):
        if (lower != None):
            lower_int = lower[0]
            upper_int = lower_int-1
            if (lower_int > 0):
                change_group_position(upper_int, lower_int)
                listbox_update_selection("Group", upper_int)
    
    def move_group_down(upper):
        if (upper != None):
            upper_int = upper[0]
            lower_int = upper_int+1
            if (upper_int < len(groups)-2):
                change_group_position(upper_int, lower_int)
                listbox_update_selection("Group", lower_int)

    def change_group_position(upper_int, lower_int):
        temp_list = []
        for k, v in groups.items():
            temp_list.append([k,v])
        temp_list[upper_int+1], temp_list[lower_int+1] = temp_list[lower_int+1], temp_list[upper_int+1]
        for t in temp_list:
            del groups[t[0]]
            groups[t[0]] = t[1] 
        write_json(groups)
        update_group_list()

    def rename_group(group):
        if group != None:
            new_group = askstring("New Group", "Name file group:")
            if new_group in groups:
                messagebox.showerror("Error", "A group with that name already exists!")
            else:
                storevalue = groups[group]
                del groups[group]
                groups[new_group] = storevalue
                write_json(groups)
                update_group_list()
                listbox_update_selection("Group", len(groups)-2)

    def move_file_up(lower, group):
        if (lower != None and group != None):
            lower_int = lower
            upper_int = lower_int-1
            if (lower_int > 0):
                change_file_position(upper_int, lower_int, group)
                listbox_update_selection("Files", upper_int)

    def move_file_down(upper, group):
        if (upper != None and group != None):
            upper_int = upper
            lower_int = upper_int+1
            if (upper_int < len(groups[group])-1):
                change_file_position(upper_int, lower_int, group)
                listbox_update_selection("Files", lower_int)

    def change_file_position(upper_int, lower_int, group):
        temp_list = []
        for k, v in groups[group].items():
            temp_list.append([k,v])
        temp_list[upper_int], temp_list[lower_int] = temp_list[lower_int], temp_list[upper_int]
        for t in temp_list:
            del groups[group][t[0]]
            groups[group][t[0]] = t[1] 
        write_json(groups)
        update_file_list()

    def listbox_update_selection(list_type, index):
        if list_type == "Group":
            group_listbox.select_clear(0, tk.END)
            group_listbox.select_set(index)
        if list_type == "Files":
            file_listbox.select_clear(0, tk.END)
            file_listbox.select_set(index)

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
    toggle_filepath_button.place(x=330, y=270)

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
                try:
                    os.startfile(k)
                    if autoclose.get() is True:
                        check_checkboxes()
                        close()
                except:
                    messagebox.showerror("Error", f"Cannot open {k}!")
        else:
            messagebox.showerror("Error", "Must select a group to open from!")

    open_button = tk.Button(text="Open Files", bg="#3599e6", fg="#1c1c1c", 
                            font="arial 18 bold", command=open_files)
    open_button.place(x=550, y=5)

    def check_vlcrc(path):
        if pathlib.Path(path).exists() and path[-5::] == "vlcrc":
            return True
        return False

    def check_vlrc_exists():
        if check_vlcrc(vlcrcpath.get()):
            messagebox.showinfo("VLC Settings File", "VLC Settings File exists in current directory.")
        else:
            messagebox.showinfo("VLC Settings File", "VLC Settings File does not exist in current directory. Click Add Custom Path to manually locate 'vlcrc' file.")

    def change_vlcrc_settings(path, setting, newvalue, oldvalue):
        try:
            newsetting = setting+str(newvalue)
            oldsetting = setting+str(oldvalue)
            with open (path, "r") as f:
                lines = []
                for f in f.readlines():
                    lines.append(f.replace(oldsetting,newsetting))
            with open (path, "w") as f:
                for line in lines:
                    f.writelines(line)
        except:
            messagebox.showerror("Error", "VLC settings file can not be read or modified!")

    def check_vlcrc_settings(path, setting):
        try:
            with open (path, "r") as f:
                for f in f.readlines():
                    if setting in f:
                        value = f
            value = value.strip()[-1]
            match setting:
                case "start-paused=":
                    setting_str = "Start Paused"
                case "one-instance-when-started-from-file=":
                    setting_str = "Only Allow One Instance"
            match value:
                case "1":
                    value_str = "ON"
                case "0":
                    value_str = "OFF"
            messagebox.showinfo("Check Setting", f"{setting_str} is turned {value_str}.")

        except:
            messagebox.showerror("Error", "VLC settings file can not be read!")

    def vlcrc_select_dir():
        filepath = filedialog.askopenfilename(initialdir="/", title="Select vlcrc File", 
                                                filetypes=[("All Files", "*.*")])
        if filepath != "":
            groups["_SETTINGS_"]["vlcrc_path"] = filepath
            vlcrcpath.set(filepath)
            write_json(groups)
    
    def vlcrc_restore():
        msgbox_warning = messagebox.askquestion("Warning", f"Do you really want to restore default vlcrc path?")
        if msgbox_warning == "yes":
            default_path = f"{HOMEFOLDER}\\AppData\\Roaming\\vlc\\vlcrc"
            groups["_SETTINGS_"]["vlcrc_path"] = default_path
            vlcrcpath.set(default_path)
            write_json(groups)

    def vlc_button_command(setting, newvalue=None, oldvalue=None):
        path = vlcrcpath.get()
        if check_vlcrc(path):
            if newvalue != None:
                change_vlcrc_settings(path, setting, newvalue, oldvalue)
            else:
                check_vlcrc_settings(path, setting)
        else:  
            messagebox.showerror("Error", "VLC settings file not found! Click Add Custom Path to manually select VLC settings file.")

    vlc_paused = "start-paused="
    vlc_mult_inst = "one-instance-when-started-from-file="

    vlc_pause_on_button = tk.Button(text="Pause On", command=lambda:[vlc_button_command(vlc_paused, 1, 0)])
    vlc_pause_off_button = tk.Button(text="Pause Off", command=lambda:[vlc_button_command(vlc_paused, 0, 1)])

    vlc_multiple_on_button = tk.Button(text="Mult On", command=lambda:[vlc_button_command(vlc_mult_inst, 1, 0)])
    vlc_multiple_off_button = tk.Button(text="Mult Off", command=lambda:[vlc_button_command(vlc_mult_inst, 0, 1)])

    vlc_pause_on_button.place(x=5, y=300)
    vlc_pause_off_button.place(x=75, y=300)
    vlc_multiple_on_button.place(x=5, y=330)
    vlc_multiple_off_button.place(x=75, y=330)

    vlc_check_pause_button = tk.Button(text="Check Pause", command=lambda:[vlc_button_command(vlc_paused)])
    vlc_check_pause_button.place(x=5, y=360)
    vlc_check_multiple_button = tk.Button(text="Check Mult", command=lambda:[vlc_button_command(vlc_mult_inst)])
    vlc_check_multiple_button.place(x=120, y=360)

    vlc_check_vlcrc_button = tk.Button(text="Check if vlcrc file exists", command=check_vlrc_exists)
    vlc_check_vlcrc_button.place(x=250, y=300)
    vlc_add_vlcrc_button = tk.Button(text="Add Custom Path", command=vlcrc_select_dir)
    vlc_add_vlcrc_button.place(x=250, y=330)
    vlc_restore_vlcrc_button = tk.Button(text="Restore Default Path", command=vlcrc_restore)
    vlc_restore_vlcrc_button.place(x=250, y=360)


    

    def check_checkboxes(): 
        """Update value of checkboxes if any change has been made."""
        if groups["_SETTINGS_"]["autoclose"] != autoclose.get():
            groups["_SETTINGS_"]["autoclose"] = autoclose.get()
        if groups["_SETTINGS_"]["save_group"] != save_group.get():
            groups["_SETTINGS_"]["save_group"] = save_group.get()
        if groups["_SETTINGS_"]["remove_warn_group"] != remove_warn_group.get():
            groups["_SETTINGS_"]["remove_warn_group"] = remove_warn_group.get()
        if groups["_SETTINGS_"]["remove_warn_files"] != remove_warn_files.get():
            groups["_SETTINGS_"]["remove_warn_files"] = remove_warn_files.get()
        write_json(groups)

    def select_saved_group():
        if current_group.get() != None or current_group.get() != "None":
            index = -1
            for group in groups:
                if group == current_group.get():
                    group_listbox.select_set(index)
                index += 1
            update_file_list()

    select_saved_group()

    test_button = tk.Button(text="TEST", command=lambda:[testasd()])
    test_button.place(x=550, y=330)


    def testasd():
        print(get_group_selection())

    def close():
        if save_group.get() is True:
            groups["_SETTINGS_"]["saved_group"] = current_group.get()
        else:
            groups["_SETTINGS_"]["saved_group"] = "None"
        write_json(groups)
        root.destroy()    

    root.protocol("WM_DELETE_WINDOW", lambda:[close(), check_checkboxes()])

    root.mainloop()



if has_json:
    with open ("saved_groups.json", "r", encoding="utf-8") as file:
        groups = json.load(file)
    draw_gui()
else:
    vlcrc = f"{HOMEFOLDER}\\AppData\\Roaming\\vlc\\vlcrc"
    settings = {
        "show_full_filepath": True,
        "lastdir": str(DESKTOP),
        "vlcrc_path": vlcrc,
        "saved_group": "None",
        "save_group": False,
        "autoclose": False,
        "remove_warn_group": False,
        "remove_warn_files": True
        }
    json_content = {"_SETTINGS_":settings}
    write_json(json_content)
    with open ("saved_groups.json", "r", encoding="utf-8") as file:
        groups = json.load(file)
    draw_gui()

#draw_gui()
