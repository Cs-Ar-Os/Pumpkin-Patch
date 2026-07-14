# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 19:15:13 2025

@author: CsArOs
"""

import os, sys, winshell, subprocess 
import shutil, zipfile
import tkinter as tk
from tkinter import filedialog, messagebox

EXE_NAME = "h3hota HD.exe"
PP_Folder = "PumpkinPatch"
MOD_FOLDER_INSIDE_EXE_name_string = "ModFiles"
Polish_Folder_Inside_EXE_name_string = "PolishFiles"
backup_zip = "_HOTA BACKUP.zip"
DAT = "HotA.dat"
polish_sample = b"\x74\x6F\x77\x61\x72\x7A\x79\x73\x74\x77"
tmpl_folder = "HotA_RMGTemplates"
data_folder = "Data"

if getattr(sys, 'frozen', False):
    polish_folder_inside_exe = os.path.join(sys._MEIPASS, PP_Folder, Polish_Folder_Inside_EXE_name_string)
else:
    polish_folder_inside_exe = os.path.join(os.path.dirname(__file__), PP_Folder, Polish_Folder_Inside_EXE_name_string)            

if getattr(sys, 'frozen', False):
    mod_folder_inside_exe = os.path.join(sys._MEIPASS, PP_Folder, MOD_FOLDER_INSIDE_EXE_name_string)
else:
    mod_folder_inside_exe = os.path.join(os.path.dirname(__file__), PP_Folder, MOD_FOLDER_INSIDE_EXE_name_string)    

def create_shortcut(target_path, shortcut_name="Play Pumpkin Patch", icon_path=None):
    try:
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")

        winshell.CreateShortcut(
            Path=shortcut_path,
            Target=target_path,
            Icon=(icon_path, 0) if icon_path else None
        )
    except Exception as e:
        warning_message = "Could not create a desktop shortcut. Reason: " + e
        messagebox.showinfo('Warning', warning_message)

def find_any_game_folder(start_dirs):
    for base_dir in start_dirs:
        for root, dirs, files in os.walk(base_dir):
            if EXE_NAME in files:
                path = os.path.join(root, EXE_NAME)
                return path
    return None

def find_latest_game_folder(start_dirs):
    candidates = []

    for base_dir in start_dirs:
        for root, dirs, files in os.walk(base_dir):
            if EXE_NAME in files:
                full_path = os.path.join(root, EXE_NAME)
                mod_time = os.path.getmtime(full_path)
                candidates.append((mod_time, root))

    if not candidates:
        return None

    candidates.sort()
    return candidates[-1][1]  # Return folder with the most recently updated .exe



def ask_user_to_confirm_folder(folder):
    msg = f"Game folder detected:\n\n{folder}\n\nIs this correct?"
    result = messagebox.askyesno("Confirm Game Folder", msg)
    if result:
        return folder
    else:
        new_folder = filedialog.askdirectory(title="Select Your Game Folder")
        return new_folder if new_folder else None



def install_mod_files(mod_folder, game_folder):
    for root, dirs, files in os.walk(mod_folder):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), mod_folder)
            target_path = os.path.join(game_folder, rel_path)

            dir_to_create = os.path.dirname(target_path)
            if os.path.isfile(dir_to_create):
                print(f"Path {dir_to_create} is a FILE, not a directory!")
            elif os.path.isdir(dir_to_create):
                print(f"Could not create {dir_to_create}, as it already exists as directory")
            else:
                print(f"Creating {dir_to_create}")
                os.makedirs(dir_to_create, exist_ok=True)

            shutil.copy2(os.path.join(root, file), target_path)
            print(f"Installed: {rel_path}")


def find_hex(file, hex_to_find, filepath = None):
    offsets = []
    if filepath == None:
        path = os.path.join(folder, file)
    else:
        path = filepath
    if not os.path.isfile(path):
        print("File not found: %s", path)
        raise FileNotFoundError(path)
    with open(path, 'rb') as f:
        data = f.read()
        index = data.find(hex_to_find)
        while index != -1:
            offsets.append(index)
            index = data.find(hex_to_find, index + 1)

    return offsets

#def check_language():
    #polish_offset = find_hex(DAT, polish_sample)
    #if len(polish_offset) >= 1:
    #    language = "polish"
    #    return language
    #else: 
#        language = "english"
#        return language

def main():

    global folder
    global mod_folder
    messagebox.showinfo("Welcome to the Pumpkin Patch installer!", "The installer will now load a directory for you to find your game. Please locate the heroes 3 folder when prompted.")

    mod_folder = mod_folder_inside_exe

    root = tk.Tk()
    root.withdraw()  # Hide the root window
            
    icon_path = os.path.join(mod_folder, "pp_icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    
    folder = filedialog.askdirectory(title="Select Your Game Folder")

    folder = ask_user_to_confirm_folder(folder)
    if not folder:
        messagebox.showerror("Cancelled", "Installation cancelled.")
        return

    global backup_zip
    backup_zip = os.path.join(folder, "_HOTA BACKUP.zip")
    global tmpl_folder, data_folder
    tmpl_folder = os.path.join(folder, tmpl_folder)
#    data_folder = os.path.join(folder, data_folder)

    #determine game version and make sure old is uninstalled
    create_backup()
#    language = check_language()

#    if language in ("polish"):
#        global polish_folder_inside_exe
#        polish_folder = polish_folder_inside_exe
#        choice = messagebox.askokcancel("Polish Version detected", "The HexSwapper will install Polish translation. \n\nProceed? \n\n(Recommended: Yes)")
#        if choice:
#            install_mod_files(mod_folder, folder)
#            install_mod_files(polish_folder, folder)
#        else:
#            choice = messagebox.askyesno("Are you absolutely sure?", "Do you want to install the English version despite the game seemingly being in Polish? \n\n(Highly Reocommended: No)")
#            if choice:
#                if messagebox.askyesno("Cancel?", "Do you want to cancel the installation now?"):
#                    messagebox.showinfo("Cancelled", "Installation cancelled")
#                    sys.exit()
#                install_mod_files(mod_folder, folder)
#                messagebox.showinfo("Warning", "Installed the English version, as requested. Please make sure your game is actually in English.")
#            else: 
#                install_mod_files(mod_folder, folder)
#    else:

    install_mod_files(mod_folder, folder)

    messagebox.showinfo("Success", "Files installed successfully!")

    hexswapper_exe = os.path.join(folder, "HexSwapper.exe")

    if not os.path.exists(hexswapper_exe):
        print(f"Error. Game executable not found at: {hexswapper_exe}")
        return

    shortcut_icon = os.path.join(folder, "pp_icon.ico")
    create_shortcut(hexswapper_exe, "Play Pumpkin Patch", shortcut_icon)

    try:
        subprocess.Popen([hexswapper_exe], cwd=folder)
    except Exception as e:
        print(f"Failed to launch HexSwapper: {e}")

    sys.exit()
    
    

def get_file_list_relative(directory):
    file_list = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, directory)  # Rel ModFiles
            file_list.append(rel_path)
    return file_list

def get_file_list(directory = None):
    if directory == None:    
        directory = mod_folder
    
    file_list = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            file_list.append(os.path.join(dirpath, f))
    return file_list

def create_backup():
    mod_files_list = get_file_list(mod_folder)

    print(mod_files_list)


    #removes old files
    delete_maps_list = ["Sir Mullich's Charge", "Secrets of the Pumpkin Patch", "Secrets of the PP", "[Pumpkin Patch] Secrets", "[Pumpkin Patch] Secrets - Copy", "[Pumpkin Patch] Charge", "The Mysterious Island - Allies"]
    delete_templates_list = ["Duel 3.0", "Duel 3.0 t+", "Duel 3.0a", "Duel 3.0a t+", "Jebus Cross Pumpkin Patch", "Jebus Cross - PP", "Jebus Cross PP", "Memory Lane 1.8.2 PP", "Memory Lane PP", "Memory Lane 1.90", "Memory Lane - PP", "Memory Lane", "Memory Lane 1.8.2 - PP", "Memory Lane 1.9.0 PP", "Memory Lane 1.9.0 - PP", "6lm10a - PP", "6lm10a PP", "Memory Lane 1.82 PP", "Memory Lane 1.90 - PP"]
    delete_folders_list = ["alternative", "Icons", "mkc", "modded", "original"]
    delete_files_list = ["HexSwapper.exe"]

    if os.path.isfile(backup_zip):
        try:
            with zipfile.ZipFile(backup_zip, 'r') as backup:
                backup.extractall(folder)
        except Exception:
            pass

    for mapname in delete_maps_list:
        mapname = str(mapname) + ".h3m"
        try:
            winshell.delete_file(os.path.join(folder, "Maps", mapname), no_confirm = True)
        except Exception:
            pass
        try:
            winshell.delete_file(os.path.join(folder, "Maps", mapname.lower()), no_confirm = True)
        except Exception:
            pass
    
    for templatename in delete_templates_list:
        templatename = str(templatename) + ".h3t"
        try:
            winshell.delete_file(os.path.join(folder, "HotA_RMGTemplates", templatename), no_confirm = True)
        except Exception:
            pass
        try:
            winshell.delete_file(os.path.join(folder, "HotA_RMGTemplates", templatename.lower()), no_confirm = True)
        except Exception:
            pass


    for foldername in delete_folders_list:
        if foldername is not None:
            try:
                winshell.delete_file(os.path.join(folder, "Data", str(foldername)), no_confirm = True)
            except Exception:
                pass
            try:
                winshell.delete_file(os.path.join(folder, "Data", str(foldername).lower()), no_confirm = True)
            except Exception:
                pass

    for filename in delete_files_list:
        if filename is not None:
            try:
                winshell.delete_file(os.path.join(folder, str(filename)), no_confirm = True)
            except Exception:
                pass
            try:
                winshell.delete_file(os.path.join(folder, str(filename).lower()), no_confirm = True)
            except Exception:
                pass


    try:
        with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as backup:
            # Backup game files corresponding to mod files
            #Backup templates folder once
            for dirpath, _, filenames in os.walk(tmpl_folder):
                for file in filenames:
                    full_path = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(full_path, tmpl_folder)
                    arcname = os.path.join("HotA_RMGTemplates", rel_path)
                    backup.write(full_path, arcname=arcname)

            print(f"Templates backed up into: {backup_zip} under 'HotA_RMGTemplates/' folder")
            messagebox.showinfo("Backup created", ("Backup location:  " + os.path.join(folder, "_HOTA BACKUP.zip")))
            return
        return
    except Exception as e:
        messagebox.showinfo("Error", f"Backup creation failed: {e}")
    return


if __name__ == "__main__":
    main()



