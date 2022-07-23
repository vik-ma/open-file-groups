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

    lastdir = StringVar(value=groups["_SETTINGS_"]["lastdir"])
    vlcrcpath = StringVar(value=groups["_SETTINGS_"]["vlcrc_path"])
    remove_warn_group = tk.BooleanVar(value=groups["_SETTINGS_"]["remove_warn_group"])
    remove_warn_files = tk.BooleanVar(value=groups["_SETTINGS_"]["remove_warn_files"])
    current_group = StringVar(value=groups["_SETTINGS_"]["saved_group"])
    toggle_filepath_state = BooleanVar(value=groups["_SETTINGS_"]["show_full_filepath"])

    vlc_settings_frame = tk.Frame(height=299, width=702, highlightbackground="black", highlightthickness=1)
    vlc_settings_frame.place(x=-1, y=-1)

    autoclose = tk.BooleanVar(value=groups["_SETTINGS_"]["autoclose"])
    save_group = tk.BooleanVar(value=groups["_SETTINGS_"]["save_group"])

    autoclose_checkbox = tk.Checkbutton(text="Close Program After Opening", variable=autoclose, onvalue=True, offvalue=False)
    save_group_checkbox = tk.Checkbutton(text="Automatically select current group next time program is opened", variable=save_group, onvalue=True, offvalue=False)
    
    autoclose_checkbox.place(x=1, y=21)
    save_group_checkbox.place(x=1, y=1)

    created_groups_label = tk.Label(text="Created Groups:", font="arial 13 bold")
    created_groups_label.place(x=3, y=44)

    gbw = 120
    fbw = 105

    add_group_button = tk.Button(text="Create New Group", command=lambda:[add_group()])
    add_group_button.place(x=203, y=70, width=gbw)
        
    rename_group_button = tk.Button(text="Rename Group", command=lambda:[rename_group(get_group_selection())])
    rename_group_button.place(x=203, y=100, width=gbw)

    move_group_up_button = tk.Button(text="Move Group Up", command=lambda:[move_group_up(get_group_index())])
    move_group_up_button.place(x=203, y=130, width=gbw)

    move_group_down_button = tk.Button(text="Move Group Down", command=lambda:[move_group_down(get_group_index())])
    move_group_down_button.place(x=203, y=160, width=gbw)

    remove_group_button = tk.Button(text="Delete Group", command=lambda:[remove_group(get_group_selection())])
    remove_group_button.place(x=203, y=190, width=gbw)
    
    add_file_button = tk.Button(text="Add File", command=lambda:[add_file(current_group.get())])
    add_file_button.place(x=590, y=70, width=fbw)

    add_folder_button = tk.Button(text="Add Folder", command=lambda:[add_folder(current_group.get())])
    add_folder_button.place(x=590, y=100, width=fbw)
    
    move_file_up_button = tk.Button(text="Move Entry Up", command=lambda:[move_file_up(get_file_selection(), get_group_selection())])
    move_file_up_button.place(x=590, y=130, width=fbw)

    move_file_down_button = tk.Button(text="Move Entry Down", command=lambda:[move_file_down(get_file_selection(), get_group_selection())])
    move_file_down_button.place(x=590, y=160, width=fbw)

    remove_entry_button = tk.Button(text="Remove Entry", command=lambda:[remove_entry(get_file_selection(), current_group.get())])
    remove_entry_button.place(x=590, y=190, width=fbw)

    group_list = StringVar(value=[group for group in groups][1::])
    group_listbox = tk.Listbox(listvariable=group_list, width=32, selectmode="SINGLE", exportselection=True, activestyle="none")
    group_listbox.place(x=5, y=70)

    def add_group():
        new_group = askstring("New Group", "Name file group:")
        if new_group != None:
            if new_group in groups:
                messagebox.showerror("Error", "A group with that name already exists!")
            else:
                groups[new_group] = {}
                write_json(groups)
                update_group_list()
                current_group.set(new_group)
                listbox_update_selection("Group", len(groups)-2)
                update_file_list()

    def rename_group(group):
        if group != None:
            index = get_group_index()[0]
            new_group = askstring("New Group", "Name file group:")
            if new_group != None:
                if new_group in groups:
                    messagebox.showerror("Error", "A group with that name already exists!")
                else:
                    storevalue = groups[group]
                    temp_list = [[k,v] for k,v in groups.items()]
                    for t in temp_list:
                        del groups[t[0]]
                        if t[0] == group:
                            groups[new_group] = storevalue
                        else:
                            groups[t[0]] = t[1]
                    write_json(groups)
                    update_group_list()
                    current_group.set(new_group)
                    listbox_update_selection("Group", index)

    def move_group_up(lower):
        if lower != None:
            lower_int = lower[0]
            upper_int = lower_int-1
            if lower_int > 0:
                change_group_position(upper_int, lower_int)
                listbox_update_selection("Group", upper_int)
    
    def move_group_down(upper):
        if upper != None:
            upper_int = upper[0]
            lower_int = upper_int+1
            if upper_int < len(groups) - 2:
                change_group_position(upper_int, lower_int)
                listbox_update_selection("Group", lower_int)

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

    def change_group_position(upper_int, lower_int):
        temp_list = [[k,v] for k,v in groups.items()]
        temp_list[upper_int+1], temp_list[lower_int+1] = temp_list[lower_int+1], temp_list[upper_int+1]
        for t in temp_list:
            del groups[t[0]]
            groups[t[0]] = t[1] 
        write_json(groups)
        update_group_list()

    def sort_groups():
        group = get_group_selection()
        temp_list = [[k,v] for k,v in groups.items()][1::]
        if temp_list != [] and group != "None":
            sorted_list = sorted(temp_list, key=get_key)
            for t in temp_list:
                del groups[t[0]]
            index = 0
            for i, s in enumerate(sorted_list):
                groups[s[0]] = s[1]
                if s[0] == group:
                    index = i
            write_json(groups)
            update_group_list()
            if group != None:
                listbox_update_selection("Group", index)

    def update_group_list():
        group_list.set([group for group in groups][1::])

    def group_listbox_on_select(event):
        e = event.widget
        if e.curselection() != ():
            #Doesn't cause error if you click on a askstring dialog box
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

    def get_group_index():
        if group_listbox.curselection() != ():
            return group_listbox.curselection()

    def get_file_selection():
        if file_listbox.curselection() != ():
            return file_listbox.curselection()[0]

    selected_group_label = tk.Label(text="Selected Group:", font="arial 13 bold")
    selected_group_label.place(x=323, y=24)
    current_group_label = tk.Label(textvariable=current_group, font="arial 13 bold", fg="#166edb")
    current_group_label.place(x=324, y=44)

    file_list = StringVar()
    file_listbox = tk.Listbox(listvariable=file_list, width=43, selectmode="SINGLE", exportselection=False, activestyle="none")
    file_listbox.place(x=326, y=70)

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
                foldername = f"{get_foldername[-1]} (Folder)"
                groups[group][folderpath] = foldername
                get_dir = folderpath.rsplit("/",1)[0]
                groups["_SETTINGS_"]["lastdir"] = get_dir
                lastdir.set(get_dir)
                write_json(groups)
                update_file_list()
        else:
            messagebox.showerror("Error", "Select a group to add folder to first!")

    def move_file_up(lower, group):
        if lower != None and group != None:
            lower_int = lower
            upper_int = lower_int-1
            if lower_int > 0:
                change_file_position(upper_int, lower_int, group)
                listbox_update_selection("Files", upper_int)

    def move_file_down(upper, group):
        if upper != None and group != None:
            upper_int = upper
            lower_int = upper_int+1
            if upper_int < len(groups[group]) - 1:
                change_file_position(upper_int, lower_int, group)
                listbox_update_selection("Files", lower_int)

    def change_file_position(upper_int, lower_int, group):
        temp_list = [[k,v] for k,v in groups[group].items()]
        temp_list[upper_int], temp_list[lower_int] = temp_list[lower_int], temp_list[upper_int]
        for t in temp_list:
            del groups[group][t[0]]
            groups[group][t[0]] = t[1] 
        write_json(groups)
        update_file_list()

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

    def update_file_list():
        if current_group.get() != "":
            if current_group.get() in groups:
                if toggle_filepath_state.get() is True:
                    file_list.set([k for k, v in groups[current_group.get()].items()])
                else:
                    file_list.set([v for k, v in groups[current_group.get()].items()])
            else:
                file_list.set([])

    def get_key(list):
        return list[0].lower()

    def get_value(list):
        return list[1].lower()

    def listbox_update_selection(list_type, index):
        if list_type == "Group":
            group_listbox.select_clear(0, tk.END)
            group_listbox.select_set(index)
        if list_type == "Files":
            file_listbox.select_clear(0, tk.END)
            file_listbox.select_set(index)

    def sort_files():
        group = get_group_selection()
        if group != "None" and group != None:
            temp_list = [[k,v] for k,v in groups[group].items()]
            if temp_list != []:
                sorted_list = sorted(temp_list, key=get_value)
                selected_file = ""
                for i, t in enumerate(temp_list):
                    del groups[group][t[0]]
                    if i == get_file_selection():
                        selected_file = t[0]
                index = 0
                for i, s in enumerate(sorted_list):
                    groups[group][s[0]] = s[1]
                    if selected_file == s[0]:
                        index = i
                write_json(groups)
                update_file_list()
                if get_file_selection() != None:
                    listbox_update_selection("Files", index)

    warn_group_checkbox = tk.Checkbutton(text="Warn before trying to delete group", variable=remove_warn_group, onvalue=True, offvalue=False)
    warn_files_checkbox = tk.Checkbutton(text="Warn before trying to delete file or folder", variable=remove_warn_files, onvalue=True, offvalue=False)
    
    warn_group_checkbox.place(x=1, y=265)
    warn_files_checkbox.place(x=326, y=265)

    sort_groups_button = tk.Button(text="Sort Groups Alphabetically", command=lambda:[sort_groups()])
    sort_groups_button.place(x=5, y=237)

    sort_files_button = tk.Button(text="Sort Files/Folders Alphabetically", command=lambda:[sort_files()])
    sort_files_button.place(x=326, y=237)

    toggle_filepath_button_text = StringVar()

    def show_filepath_button(state):
        if state is True:
            toggle_filepath_button_text.set("Toggle Shorter Filepaths")
        else:
            toggle_filepath_button_text.set("Toggle Full Filepaths")

    show_filepath_button(toggle_filepath_state.get())

    toggle_filepath_button = tk.Button(textvariable=toggle_filepath_button_text, command=lambda:[toggle_filepath()])
    toggle_filepath_button.place(x=509, y=237)

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

    open_button = tk.Button(text="Open Files", bg="#3599e6", fg="#1c1c1c", 
                            font="arial 16 bold", command=lambda:[open_files()])
    open_button.place(x=570, y=3)

    def select_saved_group():
        if current_group.get() != None or current_group.get() != "None":
            index = -1
            for group in groups:
                if group == current_group.get():
                    group_listbox.select_set(index)
                index += 1
            update_file_list()

    select_saved_group()

    def open_files():
        group = current_group.get()
        if group != "None" and group != "":
            if len(groups[group]) > 0:
                for k, v in groups[group].items():
                    try:
                        os.startfile(k)
                    except:
                        messagebox.showerror("Error", f"Cannot open {k}!")
                if autoclose.get() is True:
                    check_checkboxes()
        else:
            messagebox.showerror("Error", "Must select a group to open from!")    

    vlc_settings_title_label = tk.Label(text="VLC Media Player Settings", font="arial 13 bold", fg="#fc8c03")
    vlc_settings_title_label.place(x=4, y=303)
    
    show_vlcrc_path = StringVar(value=f"VLC Settings file: {vlcrcpath.get()}")

    vlcrc_path_label = tk.Label(textvariable=show_vlcrc_path, font="arial 8 bold")
    vlcrc_path_label.place(x=4, y=327)

    vlc_settings_desc_label = tk.Label(text="When opening media files in VLC Media Player, it is recommended to\nstart the media files paused and to allow more than one instance of\nVLC Media Player to be active. You can turn these features on or off here.", justify="left")
    vlc_settings_desc_label.place(x=4, y=346)

    vlc_paused = "start-paused="
    vlc_mult_inst = "one-instance-when-started-from-file="

    vlc_start_paused_label = tk.Label(text="Start Paused:", font="arial 9 bold")
    vlc_start_paused_label.place(x=469, y=346)

    vlc_one_instance_label = tk.Label(text="Allow Only One Instance:", font="arial 9 bold")
    vlc_one_instance_label.place(x=406, y=372)

    vlc_pause_on_button = tk.Button(text="Turn On", command=lambda:[vlc_button_command(vlc_paused, 1, 0)], font="segoeui 8")
    vlc_pause_off_button = tk.Button(text="Turn Off", command=lambda:[vlc_button_command(vlc_paused, 0, 1)], font="segoeui 8")

    vlc_multiple_on_button = tk.Button(text="Turn On", command=lambda:[vlc_button_command(vlc_mult_inst, 1, 0)], font="segoeui 8")
    vlc_multiple_off_button = tk.Button(text="Turn Off", command=lambda:[vlc_button_command(vlc_mult_inst, 0, 1)], font="segoeui 8")

    vlc_pause_on_button.place(x=595, y=343)
    vlc_pause_off_button.place(x=645, y=343)
    vlc_multiple_on_button.place(x=595, y=370)
    vlc_multiple_off_button.place(x=645, y=370)

    vlc_check_pause_button = tk.Button(text="Check", command=lambda:[vlc_button_command(vlc_paused)], font="segoeui 8")
    vlc_check_pause_button.place(x=554, y=343)
    vlc_check_multiple_button = tk.Button(text="Check", command=lambda:[vlc_button_command(vlc_mult_inst)], font="segoeui 8")
    vlc_check_multiple_button.place(x=554, y=370)

    vlc_check_vlcrc_button = tk.Button(text="Check if vlcrc file exists", command=lambda:[check_vlrc_exists()])
    vlc_check_vlcrc_button.place(x=330, y=302)
    vlc_add_vlcrc_button = tk.Button(text="Add Custom Path", command=lambda:[vlcrc_select_dir()])
    vlc_add_vlcrc_button.place(x=467, y=302)
    vlc_restore_vlcrc_button = tk.Button(text="Restore Default Path", command=lambda:[vlcrc_restore()])
    vlc_restore_vlcrc_button.place(x=577, y=302)

    def check_vlcrc(path):
        if pathlib.Path(path).exists() and path[-5::] == "vlcrc":
            return True
        return False

    def check_vlrc_exists():
        if check_vlcrc(vlcrcpath.get()):
            messagebox.showinfo("VLC Settings File", "VLC Settings File exists in current directory.")
        else:
            messagebox.showinfo("VLC Settings File", "VLC Settings File does not exist in current directory.\nClick Add Custom Path to manually locate 'vlcrc' file.")

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
                    setting_str = "Allow Only One Instance"
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
            show_vlcrc_path.set(f"VLC Settings file: {vlcrcpath.get()}")
            write_json(groups)
    
    def vlcrc_restore():
        msgbox_warning = messagebox.askquestion("Warning", f"Do you really want to restore default vlcrc path?")
        if msgbox_warning == "yes":
            default_path = f"{HOMEFOLDER}\\AppData\\Roaming\\vlc\\vlcrc"
            groups["_SETTINGS_"]["vlcrc_path"] = default_path
            vlcrcpath.set(default_path)
            show_vlcrc_path.set(f"VLC Settings file: {vlcrcpath.get()}")
            write_json(groups)

    def vlc_button_command(setting, newvalue=None, oldvalue=None):
        path = vlcrcpath.get()
        if check_vlcrc(path):
            if newvalue != None:
                change_vlcrc_settings(path, setting, newvalue, oldvalue)
            else:
                check_vlcrc_settings(path, setting)
        else:  
            messagebox.showerror("Error", "VLC settings file not found!\nClick Add Custom Path to manually select VLC settings file.")

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
        close()

    def close():
        if save_group.get() is True:
            groups["_SETTINGS_"]["saved_group"] = current_group.get()
        else:
            groups["_SETTINGS_"]["saved_group"] = "None"
        write_json(groups)
        root.destroy()    

    root.protocol("WM_DELETE_WINDOW", lambda:[check_checkboxes()])

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
