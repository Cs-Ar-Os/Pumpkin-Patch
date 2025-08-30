# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 19:15:13 2025

@author: Csaros
"""

import os
import sys
import subprocess
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
import winshell

EXE_NAME = "h3hota HD.exe"
PP_Folder = "PumpkinPatch"
MOD_FOLDER_INSIDE_EXE = "ModFiles"
Polish_Folder_Inside_EXE = "PolishFiles"
backup_zip = "_HOTA BACKUP.zip"
DAT = "HotA.dat"
polish_sample = b"\x74\x6F\x77\x61\x72\x7A\x79\x73\x74\x77"
tmpl_folder = "HotA_RMGTemplates"
hd_dll = "HD_HOTA.dll"

new_text = b"\x4F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x20\x69\x73\x20\x70\x61\x72\x74\x20\x6F\x66\x20\x74\x68\x65\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x48\x6F\x74\x41\x20\x43\x72\x65\x77\x20\x68\x61\x73\x20\x7B\x6E\x6F\x74\x68\x69\x6E\x67\x7D\x20\x74\x6F\x20\x64\x6F\x20\x77\x69\x74\x68\x20\x74\x68\x65\x20\x64\x65\x76\x65\x6C\x6F\x70\x6D\x65\x6E\x74\x20\x61\x6E\x64\x20\x73\x75\x70\x70\x6F\x72\x74\x20\x6F\x66\x20\x6F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x2E\x0A\x0A\x7B\x50\x75\x6D\x70\x6B\x69\x6E\x7D\x20\x7B\x50\x61\x74\x63\x68\x7D\x20\x66\x75\x6E\x63\x74\x69\x6F\x6E\x73\x20\x77\x69\x74\x68\x20\x74\x68\x65\x20\x6F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x2C\x20\x62\x75\x74\x20\x79\x6F\x75\x20\x73\x68\x6F\x75\x6C\x64\x6E\x27\x74\x20\x70\x6C\x61\x79\x20\x72\x61\x6E\x6B\x65\x64\x20\x67\x61\x6D\x65\x73\x20\x77\x69\x74\x68\x20\x69\x74\x2E\x20\x57\x68\x65\x6E\x20\x69\x6E\x20\x64\x6F\x75\x62\x74\x2C\x20\x76\x69\x73\x69\x74\x20\x74\x68\x65\x20\x50\x50\x20\x44\x69\x73\x63\x6F\x72\x64\x20\x73\x65\x72\x76\x65\x72\x2E\x20\x0A\x0A"
original_text = b"\x4F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x20\x69\x73\x20\x70\x61\x72\x74\x20\x6F\x66\x20\x74\x68\x65\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x48\x6F\x74\x41\x20\x43\x72\x65\x77\x20\x7B\x68\x61\x73\x7D\x20\x7B\x6E\x6F\x74\x68\x69\x6E\x67\x7D\x20\x7B\x74\x6F\x7D\x20\x7B\x64\x6F\x7D\x20\x77\x69\x74\x68\x20\x74\x68\x65\x20\x64\x65\x76\x65\x6C\x6F\x70\x6D\x65\x6E\x74\x20\x61\x6E\x64\x20\x73\x75\x70\x70\x6F\x72\x74\x20\x6F\x66\x20\x6F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x2E\x20\x49\x6E\x20\x63\x61\x73\x65\x20\x6F\x66\x20\x69\x73\x73\x75\x65\x73\x20\x77\x68\x65\x6E\x20\x61\x63\x63\x65\x73\x73\x69\x6E\x67\x20\x74\x68\x65\x20\x6C\x6F\x62\x62\x79\x2C\x20\x70\x6C\x65\x61\x73\x65\x20\x61\x62\x73\x74\x61\x69\x6E\x20\x66\x72\x6F\x6D\x20\x70\x6F\x73\x74\x69\x6E\x67\x20\x63\x6F\x6D\x70\x6C\x61\x69\x6E\x74\x73\x20\x6F\x6E\x20\x74\x68\x65\x20\x44\x69\x73\x63\x6F\x72\x64\x20\x63\x68\x61\x6E\x6E\x65\x6C\x20\x61\x6E\x64\x20\x6F\x6E\x20\x6F\x74\x68\x65\x72\x20\x70\x72\x6F\x6A\x65\x63\x74\x27\x73\x20\x70\x61\x67\x65\x73\x2E\x0A\x0A\x48\x6F\x74\x41\x20\x69\x73\x20\x61\x20\x6E\x6F\x6E\x2D\x70\x72\x6F\x66\x69\x74\x20\x70\x72\x6F\x6A\x65\x63\x74\x2C\x20\x61\x6E\x64\x20\x74\x68\x65\x20\x48\x6F\x74\x41\x20\x43\x72\x65\x77\x20\x68\x61\x73\x20\x6E\x65\x76\x65\x72\x20\x6F\x6E\x63\x65\x20\x61\x63\x63\x65\x70\x74\x65\x64\x20\x64\x6F\x6E\x61\x74\x69\x6F\x6E\x73\x20\x6F\x76\x65\x72\x20\x31\x36\x20\x79\x65\x61\x72\x73\x20\x6F\x66\x20\x64\x65\x76\x65\x6C\x6F\x70\x6D\x65\x6E\x74\x2E\x20\x42\x79\x20\x73\x75\x70\x70\x6F\x72\x74\x69\x6E\x67\x20\x74\x68\x65\x20\x6C\x6F\x62\x62\x79\x20\x79\x6F\x75\x20\x73\x75\x70\x70\x6F\x72\x74\x20\x74\x68\x65\x20\x63\x72\x65\x61\x74\x6F\x72\x20\x6F\x66\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x2C\x20\x6E\x6F\x74\x20\x74\x68\x65\x20\x48\x6F\x74\x41\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E"

if getattr(sys, 'frozen', False):
    polish_folder_inside_exe = os.path.join(sys._MEIPASS, PP_Folder, Polish_Folder_Inside_EXE)
else:
    polish_folder_inside_exe = os.path.join(os.path.dirname(__file__), PP_Folder, Polish_Folder_Inside_EXE)            

if getattr(sys, 'frozen', False):
    mod_folder_inside_exe = os.path.join(sys._MEIPASS, PP_Folder, MOD_FOLDER_INSIDE_EXE)
else:
    mod_folder_inside_exe = os.path.join(os.path.dirname(__file__), PP_Folder, MOD_FOLDER_INSIDE_EXE)    

def create_shortcut(target_path, shortcut_name="Play Pumpkin Patch", icon_path=None):
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")

    winshell.CreateShortcut(
        Path=shortcut_path,
        Target=target_path,
        Icon=(icon_path, 0) if icon_path else None
    )

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

            os.makedirs(os.path.dirname(target_path), exist_ok=True)


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

def check_language():
    polish_offset = find_hex(DAT, polish_sample)
    if len(polish_offset) >= 1:
        language = "polish"
        return language
    else: 
        language = "english"
        return language

def main():
    global folder
    global mod_folder
    mod_folder = mod_folder_inside_exe

    root = tk.Tk()
    root.withdraw()  # Hide the root window
            
    icon_path = os.path.join(mod_folder, "pp_icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    
#    search_paths = [
#        "C:/Program Files",
#        "C:/Program Files (x86)",
#        "C:/Games",
#        "C:/gry",
#        "C:/Heroes of Might and Magic 3 Complete Edition",
#        "D:/Games",
#        os.environ.get("USERPROFILE", "") + "/Desktop"
#    ]

#    print("Searching for game folder...")
#    folder = find_any_game_folder(search_paths)
    #folder = find_latest_game_folder(search_paths)
    
#    if not folder:
#        print("Game folder not found. Please select it manually.")
#        folder = filedialog.askdirectory(title="Select Your Game Folder")

    folder = filedialog.askdirectory(title="Select Your Game Folder")


    folder = ask_user_to_confirm_folder(folder)
    if not folder:
        messagebox.showerror("Cancelled", "Installation cancelled.")
        return

    global backup_zip
    backup_zip = os.path.join(folder, "_HOTA BACKUP.zip")
    global tmpl_folder
    tmpl_folder = os.path.join(folder, tmpl_folder)

    #determine game version and make sure old is uninstalled
    DAT = os.path.join(folder, "HotA.dat")
    var = find_hex(DAT, b"\x31\x2E\x34\x2E", DAT)
    if var:
        var = var[0]
        old_backup = os.path.join(folder, 'BACKUP_HOTA173')
        with open(DAT, "r+b") as f:
            f.seek(var+4)
            version = f.read(1)
            version = int(version.decode('ascii'))
            version_text = "1.4." + str(version)
        if version < 3:
            message = "Version:" + version_text + " \n\nPlease make sure to backup HotA files manually, or uninstall the mod before proceeding further with the installation."
            messagebox.showinfo("Pumpkin Patch detected", message)
            if not messagebox.askyesno("Proceed?", "Do you want to continue the installation?"):
                messagebox.showinfo("Cancelled", "Installation cancelled")
                sys.exit()
            if os.path.exists(old_backup):
                with zipfile.ZipFile(old_backup, 'r') as backup:
                    backup.extractall(folder)
            else: 
                create_backup()                
            if os.path.exists(os.path.join(folder, 'Icons')):
                shutil.rmtree(os.path.join(folder, 'Icons'))        
            if os.path.exists(os.path.join(folder, 'Data', 'Icons')):
                shutil.rmtree(os.path.join(folder, 'Data', 'Icons'))        
        elif version > 3:
            if os.path.exists(backup_zip):
                with zipfile.ZipFile(backup_zip, 'r') as backup:
                    backup.extractall(folder)
            if os.path.exists(os.path.join(folder, 'Icons')):
                shutil.rmtree(os.path.join(folder, 'Icons'))        
            if os.path.exists(os.path.join(folder, 'Data', 'Icons')):
                shutil.rmtree(os.path.join(folder, 'Data', 'Icons'))     
        else:
            create_backup()
    else:
        create_backup()
    messagebox.showinfo("Backup created", ("Backup location" + os.path.join(folder, "_HOTA BACKUP.zip")))
    language = check_language()

    if language in ("polish"):
        global polish_folder_inside_exe
        polish_folder = polish_folder_inside_exe
        choice = messagebox.askokcancel("Polish Version detected", "The HexSwapper will install Polish translation. \n\nProceed? \n\n(Recommended: Yes)")
        if choice:
            install_mod_files(mod_folder, folder)
            install_mod_files(polish_folder, folder)
        else:
            choice = messagebox.askyesno("Are you absolutely sure?", "Do you want to install the English version despite the game seemingly being in Polish? \n\n(Highly Reocommended: No)")
            if choice:
                if messagebox.askyesno("Cancel?", "Do you want to cancel the installation now?"):
                    messagebox.showinfo("Cancelled", "Installation cancelled")
                    sys.exit()
                install_mod_files(mod_folder, folder)
                messagebox.showinfo("Warning", "Installed the English version, as requested. Please make sure your game is actually in English.")
            else: 
                install_mod_files(mod_folder, folder)
    else:
        install_mod_files(mod_folder, folder)


    messagebox.showinfo("Success", "Files installed successfully!")

    hexswapper_exe = os.path.join(folder, "HexSwapper.exe")

    if not os.path.exists(hexswapper_exe):
        print(f"Error. Game executable not found at: {hexswapper_exe}")
        return

    shortcut_icon = os.path.join(mod_folder, "pp_icon.ico")
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
    global folder
    if directory == None:    
        directory = MOD_FOLDER_INSIDE_EXE
    
    file_list = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            file_list.append(os.path.join(dirpath, f))
    return file_list

def create_backup():
    mod_files_list = get_file_list(MOD_FOLDER_INSIDE_EXE)
    
    print(mod_files_list)
    
    with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as backup:
        for full_mod_path in mod_files_list:
            rel_path_inside_mod = os.path.relpath(full_mod_path, MOD_FOLDER_INSIDE_EXE)

            # This is the actual path in the game folder that is to be overwritten
            path_in_game = os.path.join(folder, rel_path_inside_mod)

            if os.path.isfile(path_in_game):
                backup.write(path_in_game, arcname=rel_path_inside_mod)
                print(f"Backed up: {rel_path_inside_mod}")
            else:
                print(f"File not found in {folder}, skipping: {rel_path_inside_mod}")


    with zipfile.ZipFile(backup_zip, 'a', zipfile.ZIP_DEFLATED) as backup:
        for dirpath, _, filenames in os.walk(tmpl_folder):
            for file in filenames:
                full_path = os.path.join(dirpath, file)
                rel_path = os.path.relpath(full_path, tmpl_folder)
                arcname = os.path.join("HotA_RMGTemplates", rel_path)  # <- place inside subfolder!!!
                backup.write(full_path, arcname=arcname)

    print(f"Templates backed up into: {backup_zip} under 'HotA_RMGTemplates/' folder") 


if __name__ == "__main__":
    main()



