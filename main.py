import tkinter as tk
from tkinter import BooleanVar, StringVar, filedialog, messagebox, Frame, Checkbutton, Label, Button, Listbox
from tkinter.simpledialog import askstring
import pathlib
import os
import json

DESKTOP = pathlib.Path.home() / 'Desktop'
HOMEFOLDER = pathlib.Path.home()

has_json = pathlib.Path("saved_groups.json").exists()

def write_json(write_to_json):
    """Write changed values to saved_groups.json."""
    with open ("saved_groups.json", "w") as file:
        json.dump(write_to_json, file, indent=2, ensure_ascii=False)

def main():
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

    #Directory where last file or folder opened was contained in
    lastdir = StringVar(value=groups["_SETTINGS_"]["lastdir"])
    #Path to vlc_rc (VLC settings file)
    vlcrcpath = StringVar(value=groups["_SETTINGS_"]["vlcrc_path"])
    #Boolean to allow deletion of groups without messagebox warning if set to True
    remove_warn_group = BooleanVar(value=groups["_SETTINGS_"]["remove_warn_group"])
    #Boolean to allow deletion of file or folder without messagebox warning if set to True
    remove_warn_files = BooleanVar(value=groups["_SETTINGS_"]["remove_warn_files"])
    #Name of currently selected group
    current_group = StringVar(value=groups["_SETTINGS_"]["saved_group"])
    #Boolean to show full filepath name to file/folder if set to True. Shows shortened path if set to False
    toggle_filepath_state = BooleanVar(value=groups["_SETTINGS_"]["show_full_filepath"])

    #Line to separate VLC Settings section from main section
    vlc_settings_frame = Frame(height=299, width=702, highlightbackground="black", highlightthickness=1)
    vlc_settings_frame.place(x=-1, y=-1)
    
    #Boolean to automatically close application after opening files if set to True
    autoclose = BooleanVar(value=groups["_SETTINGS_"]["autoclose"])
    #Boolean to automatically select group saved in "saved_group" setting in json when application is launched if set to True
    save_group = BooleanVar(value=groups["_SETTINGS_"]["save_group"])

    autoclose_checkbox = Checkbutton(text="Close Program After Opening", variable=autoclose, onvalue=True, offvalue=False)
    save_group_checkbox = Checkbutton(text="Automatically select current group next time program is opened", variable=save_group, onvalue=True, offvalue=False)
    
    autoclose_checkbox.place(x=1, y=21)
    save_group_checkbox.place(x=1, y=1)

    #Title label for group_listbox
    created_groups_label = Label(text="Created Groups:", font="arial 13 bold")
    created_groups_label.place(x=3, y=44)

    #Group Button Width
    gbw = 120
    #File/Folder Button Width
    fbw = 105

    #Buttons relating to Groups
    add_group_button = Button(text="Create New Group", command=lambda:[add_group()])
    add_group_button.place(x=203, y=70, width=gbw)
        
    rename_group_button = Button(text="Rename Group", command=lambda:[rename_group(get_group_selection())])
    rename_group_button.place(x=203, y=100, width=gbw)

    move_group_up_button = Button(text="Move Group Up", command=lambda:[move_group_up(get_group_index())])
    move_group_up_button.place(x=203, y=130, width=gbw)

    move_group_down_button = Button(text="Move Group Down", command=lambda:[move_group_down(get_group_index())])
    move_group_down_button.place(x=203, y=160, width=gbw)

    copy_group_button = Button(text="Copy Group", command=lambda:[copy_group(get_group_selection())])
    copy_group_button.place(x=203, y=190, width=gbw)

    remove_group_button = Button(text="Delete Group", command=lambda:[remove_group(get_group_selection())])
    remove_group_button.place(x=203, y=220, width=gbw)
    
    #Buttons relating to Files/Folders
    add_file_button = Button(text="Add File", command=lambda:[add_file(current_group.get())])
    add_file_button.place(x=590, y=70, width=fbw)

    add_folder_button = Button(text="Add Folder", command=lambda:[add_folder(current_group.get())])
    add_folder_button.place(x=590, y=100, width=fbw)
    
    move_file_up_button = Button(text="Move Entry Up", command=lambda:[move_file_up(get_file_selection(), get_group_selection())])
    move_file_up_button.place(x=590, y=130, width=fbw)

    move_file_down_button = Button(text="Move Entry Down", command=lambda:[move_file_down(get_file_selection(), get_group_selection())])
    move_file_down_button.place(x=590, y=160, width=fbw)

    remove_entry_button = Button(text="Remove Entry", command=lambda:[remove_entry(get_file_selection(), current_group.get())])
    remove_entry_button.place(x=590, y=190, width=fbw)

    #List to store names of all groups in saved_groups.json
    #Every dictionary in json represents one group except for the first dictionary, which stores the user settings for the application
    group_list = StringVar(value=[group for group in groups][1::])
    #Listbox to list all groups saved in saved_groups.json
    group_listbox = Listbox(listvariable=group_list, width=32, selectmode="SINGLE", exportselection=True, activestyle="none")
    group_listbox.place(x=5, y=70)

    def add_group():
        """Create new group."""
        new_group = askstring("New Group", "Name file group:")
        if new_group != None:
            #If user did not cancel askstring
            if new_group in groups:
                messagebox.showerror("Error", "A group with that name already exists!")
            else:
                groups[new_group] = {}
                write_json(groups)
                update_group_list()
                #Set the new group as current selection
                current_group.set(new_group)
                #Set the listbox selection to newly created group. Index of last item is len(groups)-2
                listbox_update_selection("Group", len(groups)-2)
                update_file_list()

    def rename_group(group):
        """Rename existing group."""
        if group != None:
            #Do nothing if no group is selected
            index = get_group_index()[0]
            new_group = askstring("New Group", "Name file group:")
            if new_group != None:
                #If user did not cancel askstring
                if new_group in groups:
                    messagebox.showerror("Error", "A group with that name already exists!")
                else:
                    #Store all values in selected group to be renamed
                    storevalue = groups[group]
                    #Store all keys/values in groups in a list
                    temp_list = [[k,v] for k,v in groups.items()]
                    for t in temp_list:
                        #Delete key in groups to be renamed
                        del groups[t[0]]
                        if t[0] == group:
                            #Create new key at same index as old key
                            #Populate new key with values from old key
                            groups[new_group] = storevalue
                        else:
                            #Fill other keys with same values as before
                            groups[t[0]] = t[1]
                    write_json(groups)
                    update_group_list()
                    #Set selection to renamed group
                    current_group.set(new_group)
                    listbox_update_selection("Group", index)

    def move_group_up(lower):
        """Move group up one step in listbox and json file."""
        if lower != None:
            #lower_int is the index of selected group, upper_int is the index above it
            lower_int = lower[0]
            upper_int = lower_int-1
            if lower_int > 0:
                #If selected group is not already first
                change_group_position(upper_int, lower_int)
                #Set selection to index above original position
                listbox_update_selection("Group", upper_int)
    
    def move_group_down(upper):
        """Move group down one step in listbox and json file."""
        if upper != None:
            #upper_int is the index of selected group, lower_int is the index below it
            upper_int = upper[0]
            lower_int = upper_int+1
            if upper_int < len(groups) - 2:
                #If selected group is not already last
                change_group_position(upper_int, lower_int)
                #Set selection to index below original position
                listbox_update_selection("Group", lower_int)

    def copy_group(group):
        """Copy values of selected group to new group."""
        if group != None:
            new_group = askstring("Copy Group", "Name file group:")
            if new_group != None:
                #If user did not cancel askstring
                if new_group in groups:
                    messagebox.showerror("Error", "A group with that name already exists!")
                else:
                    #Copy values from selected group to new group
                    groups[new_group] = groups[group]
                    write_json(groups)
                    update_group_list()
                    current_group.set(new_group)
                    #Set the listbox selection to newly created group. Index of last item is len(groups)-2
                    listbox_update_selection("Group", len(groups)-2)
                    update_file_list()


    def remove_group(group):
        """Delete group along with its values."""
        if group != None:
            msgbox_warning = ""
            if remove_warn_group.get() is True:
                #Send warning messagebox before deleting if remove_warn_group is set to True
                msgbox_warning = messagebox.askquestion("Warning", f"Do you really want to delete {group}?")
            if msgbox_warning == "yes" or remove_warn_group.get() is False:
                del groups[group]
                write_json(groups)
                update_group_list()
                current_group.set(get_group_selection())
                update_file_list()

    def change_group_position(upper_int, lower_int):
        """Swap positions of adjacent groups in listbox and json file."""
        #Store all keys and corresponding values in temporary list
        temp_list = [[k,v] for k,v in groups.items()]
        #Swap positions of upper index(upper_int+1) with lower index(lower_int+1)
        temp_list[upper_int+1], temp_list[lower_int+1] = temp_list[lower_int+1], temp_list[upper_int+1]
        for t in temp_list:
            #Delete all keys and values in json and write new based on augmented list
            del groups[t[0]]
            groups[t[0]] = t[1] 
        write_json(groups)
        update_group_list()

    def sort_groups():
        """Sort groups alphabetically in listbox and json file."""
        #Stores the selected group
        group = get_group_selection()
        #Store all keys and corresponding values in temporary list, except for first key, which stores user settings
        temp_list = [[k,v] for k,v in groups.items()][1::]
        if temp_list != [] and group != "None":
            #Do nothing if no items to sort
            #Sort all keys in list alphabetically
            sorted_list = sorted(temp_list, key=get_key)
            for t in temp_list:
                #Delete all keys and values in json
                del groups[t[0]]
            index = 0
            for i, s in enumerate(sorted_list):
                #Rewrite json with keys and values of sorted_list
                groups[s[0]] = s[1]
                if s[0] == group:
                    #Gets new index of selected group
                    index = i
            write_json(groups)
            update_group_list()
            if group != None:
                #Set current group selection to same selection as before
                listbox_update_selection("Group", index)

    def update_group_list():
        """Populate group_list with every item in groups except first key in json."""
        group_list.set([group for group in groups][1::])

    def group_listbox_on_select(event):
        """List all values of group in file_listbox when clicked on."""
        e = event.widget
        if e.curselection() != ():
            #Doesn't cause error if you click on a askstring dialog box
            #Set selected group to group that was clicked on 
            group = e.get(e.curselection())
            if toggle_filepath_state.get() is True:
                #Show full filepath if toggle_filepath_state is True
                file_list.set([k for k, v in groups[group].items()])
            else:
                #Show shortened filepath names if False
                file_list.set([v for k, v in groups[group].items()])
            #Set selected group to group that was clicked on
            current_group.set(e.get(e.curselection()))

    #Bind mouseclicks onto group_listbox to group_listbox_on_select function
    group_listbox.bind('<<ListboxSelect>>', group_listbox_on_select)

    def get_group_selection() -> str:
        """Return name selected group."""
        if group_listbox.curselection() != ():
            return group_listbox.get(group_listbox.curselection())    

    def get_group_index() -> tuple:
        """Return index of selected group in tuple form."""
        if group_listbox.curselection() != ():
            return group_listbox.curselection()

    def get_file_selection() -> int:
        """Return index of selected file or folder."""
        if file_listbox.curselection() != ():
            return file_listbox.curselection()[0]

    #Title label for file_listbox
    selected_group_label = Label(text="Selected Group:", font="arial 13 bold")
    selected_group_label.place(x=323, y=24)
    #Label to show currently selected group
    current_group_label = Label(textvariable=current_group, font="arial 13 bold", fg="#166edb")
    current_group_label.place(x=324, y=44)

    file_list = StringVar()
    #Listbox to list all saved files and folders in currently selected group
    file_listbox = Listbox(listvariable=file_list, width=43, selectmode="SINGLE", exportselection=False, activestyle="none")
    file_listbox.place(x=326, y=70)

    def add_file(group):
        """Add existing file or folder to current group."""
        if get_group_selection() != None:
            filepath = filedialog.askopenfilename(initialdir=lastdir.get(), title="Select File", 
                                                filetypes=[("All Files", "*.*")])
            if filepath != "":
                #Do nothing if no item was selected
                get_filename = filepath.split("/")
                #Sets shortened filepath to "{FILE-ROOT-FOLDER}/{FILENAME}"
                filename = get_filename[-2]+"/"+get_filename[-1]
                #Stores file in group with its key being the full filepath and its value as the shortened filepath
                groups[group][filepath] = filename
                #Stores the root directory of the file in lastdir
                get_dir = filepath.rsplit("/",1)[0]
                groups["_SETTINGS_"]["lastdir"] = get_dir
                lastdir.set(get_dir)
                write_json(groups)
                update_file_list()
        else:
            #Show error message if no group is selected
            messagebox.showerror("Error", "Select a group to add file to first!")

    def add_folder(group):
        if get_group_selection() != None:
            folderpath = filedialog.askdirectory(initialdir=lastdir.get(), title="Select Folder")
            if folderpath != "":
                #Do nothing if no item was selected
                get_foldername = folderpath.split("/")
                #Sets shortened folderpath to "{FOLDERNAME} (Folder)"
                foldername = f"{get_foldername[-1]} (Folder)"
                #Stores folder in group with its key being the full folderpath and its value as the shortened folderpath
                groups[group][folderpath] = foldername
                get_dir = folderpath.rsplit("/",1)[0]
                #Stores the root directory of the folder in lastdir
                groups["_SETTINGS_"]["lastdir"] = get_dir
                lastdir.set(get_dir)
                write_json(groups)
                update_file_list()
        else:
            #Show error message if no group is selected
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

    warn_group_checkbox = Checkbutton(text="Warn before trying to delete group", variable=remove_warn_group, onvalue=True, offvalue=False)
    warn_files_checkbox = Checkbutton(text="Warn before trying to delete file or folder", variable=remove_warn_files, onvalue=True, offvalue=False)
    
    warn_group_checkbox.place(x=1, y=265)
    warn_files_checkbox.place(x=326, y=265)

    sort_groups_button = Button(text="Sort Groups Alphabetically", command=lambda:[sort_groups()])
    sort_groups_button.place(x=5, y=237)

    sort_files_button = Button(text="Sort Files/Folders Alphabetically", command=lambda:[sort_files()])
    sort_files_button.place(x=326, y=237)

    toggle_filepath_button_text = StringVar()

    def show_filepath_button(state):
        if state is True:
            toggle_filepath_button_text.set("Toggle Shorter Filepaths")
        else:
            toggle_filepath_button_text.set("Toggle Full Filepaths")

    show_filepath_button(toggle_filepath_state.get())

    toggle_filepath_button = Button(textvariable=toggle_filepath_button_text, command=lambda:[toggle_filepath()])
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

    open_button = Button(text="Open Files", bg="#3599e6", fg="#1c1c1c", 
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

    vlc_settings_title_label = Label(text="VLC Media Player Settings", font="arial 13 bold", fg="#fc8c03")
    vlc_settings_title_label.place(x=4, y=303)
    

    show_vlcrc_path = StringVar(value=f"VLC Settings file: {vlcrcpath.get()}")
    #Label that shows the current set path to VLC Settings file (vlcrc)
    vlcrc_path_label = Label(textvariable=show_vlcrc_path, font="arial 8 bold")
    vlcrc_path_label.place(x=4, y=327)

    #Label that describes the purpose of VLC Media Player Settings section
    vlc_settings_desc_label = Label(text="When opening media files in VLC Media Player, it is recommended to\nstart the media files paused and to allow more than one instance of\nVLC Media Player to be active. You can turn these features on or off here.", justify="left")
    vlc_settings_desc_label.place(x=4, y=346)

    #Lines/values in vlcrc-file which corresponds to their settings
    vlc_paused = "start-paused="
    vlc_mult_inst = "one-instance-when-started-from-file="

    vlc_start_paused_label = Label(text="Start Paused:", font="arial 9 bold")
    vlc_start_paused_label.place(x=469, y=346)

    vlc_one_instance_label = Label(text="Allow Only One Instance:", font="arial 9 bold")
    vlc_one_instance_label.place(x=406, y=372)

    #Buttons to change settings in vlcrc file
    vlc_pause_on_button = Button(text="Turn On", command=lambda:[vlc_button_command(vlc_paused, 1, 0)], font="segoeui 8")
    vlc_pause_off_button = Button(text="Turn Off", command=lambda:[vlc_button_command(vlc_paused, 0, 1)], font="segoeui 8")

    vlc_multiple_on_button = Button(text="Turn On", command=lambda:[vlc_button_command(vlc_mult_inst, 1, 0)], font="segoeui 8")
    vlc_multiple_off_button = Button(text="Turn Off", command=lambda:[vlc_button_command(vlc_mult_inst, 0, 1)], font="segoeui 8")

    vlc_pause_on_button.place(x=595, y=343)
    vlc_pause_off_button.place(x=645, y=343)
    vlc_multiple_on_button.place(x=595, y=370)
    vlc_multiple_off_button.place(x=645, y=370)

    #Buttons to check specific values of settings in vlcrc file
    vlc_check_pause_button = Button(text="Check", command=lambda:[vlc_button_command(vlc_paused)], font="segoeui 8")
    vlc_check_pause_button.place(x=554, y=343)
    vlc_check_multiple_button = Button(text="Check", command=lambda:[vlc_button_command(vlc_mult_inst)], font="segoeui 8")
    vlc_check_multiple_button.place(x=554, y=370)

    #Button to check if current path to vlcrc file valid
    vlc_check_vlcrc_button = Button(text="Check if vlcrc file exists", command=lambda:[check_vlrc_exists()])
    vlc_check_vlcrc_button.place(x=330, y=302)
    #Button for user to specify custom path to vlcrc file
    vlc_add_vlcrc_button = Button(text="Add Custom Path", command=lambda:[vlcrc_select_dir()])
    vlc_add_vlcrc_button.place(x=467, y=302)
    #Button to set the path to vlcrc to its default value
    vlc_restore_vlcrc_button = Button(text="Restore Default Path", command=lambda:[vlcrc_restore()])
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

if __name__ == "__main__":
    if has_json:
        with open ("saved_groups.json", "r", encoding="utf-8") as file:
            groups = json.load(file)
        main()
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
        main()
