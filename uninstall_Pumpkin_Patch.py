# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 18:55:03 2025

@author: CsArOs
"""

import sys
import os
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox

if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
backup_zip = os.path.join(script_dir, "_HOTA BACKUP.zip")
hota_EXE = os.path.join(script_dir, "h3hota HD.exe")
hexswapper_EXE = os.path.join(script_dir, "HexSwapper.exe")
Icons = os.path.join(script_dir, "Data", "Icons")
pp_INI = os.path.join(script_dir, "PP.ini")
pp_version_TXT = os.path.join(script_dir, "PP_version.txt")
readme = os.path.join(script_dir, "README Pumpkin Patch.txt")

hd_dll = "HD_HOTA.dll"

new_text = b"\x4F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x20\x69\x73\x20\x70\x61\x72\x74\x20\x6F\x66\x20\x74\x68\x65\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x48\x6F\x74\x41\x20\x43\x72\x65\x77\x20\x68\x61\x73"
original_text = b"\x4F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x20\x69\x73\x20\x70\x61\x72\x74\x20\x6F\x66\x20\x74\x68\x65\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x48\x6F\x74\x41\x20\x43\x72\x65\x77\x20\x7B\x68\x61\x73\x7D\x20\x7B\x6E\x6F\x74\x68\x69\x6E\x67\x7D\x20\x7B\x74\x6F\x7D\x20\x7B\x64\x6F\x7D\x20\x77\x69\x74\x68\x20\x74\x68\x65\x20\x64\x65\x76\x65\x6C\x6F\x70\x6D\x65\x6E\x74\x20\x61\x6E\x64\x20\x73\x75\x70\x70\x6F\x72\x74\x20\x6F\x66\x20\x6F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x2E\x20\x49\x6E\x20\x63\x61\x73\x65\x20\x6F\x66\x20\x69\x73\x73\x75\x65\x73\x20\x77\x68\x65\x6E\x20\x61\x63\x63\x65\x73\x73\x69\x6E\x67\x20\x74\x68\x65\x20\x6C\x6F\x62\x62\x79\x2C\x20\x70\x6C\x65\x61\x73\x65\x20\x61\x62\x73\x74\x61\x69\x6E\x20\x66\x72\x6F\x6D\x20\x70\x6F\x73\x74\x69\x6E\x67\x20\x63\x6F\x6D\x70\x6C\x61\x69\x6E\x74\x73\x20\x6F\x6E\x20\x74\x68\x65\x20\x44\x69\x73\x63\x6F\x72\x64\x20\x63\x68\x61\x6E\x6E\x65\x6C\x20\x61\x6E\x64\x20\x6F\x6E\x20\x6F\x74\x68\x65\x72\x20\x70\x72\x6F\x6A\x65\x63\x74\x27\x73\x20\x70\x61\x67\x65\x73\x2E\x0A\x0A\x48\x6F\x74\x41\x20\x69\x73\x20\x61\x20\x6E\x6F\x6E\x2D\x70\x72\x6F\x66\x69\x74\x20\x70\x72\x6F\x6A\x65\x63\x74\x2C\x20\x61\x6E\x64\x20\x74\x68\x65\x20\x48\x6F\x74\x41\x20\x43\x72\x65\x77\x20\x68\x61\x73\x20\x6E\x65\x76\x65\x72\x20\x6F\x6E\x63\x65\x20\x61\x63\x63\x65\x70\x74\x65\x64\x20\x64\x6F\x6E\x61\x74\x69\x6F\x6E\x73\x20\x6F\x76\x65\x72\x20\x31\x36\x20\x79\x65\x61\x72\x73\x20\x6F\x66\x20\x64\x65\x76\x65\x6C\x6F\x70\x6D\x65\x6E\x74\x2E\x20\x42\x79\x20\x73\x75\x70\x70\x6F\x72\x74\x69\x6E\x67\x20\x74\x68\x65\x20\x6C\x6F\x62\x62\x79\x20\x79\x6F\x75\x20\x73\x75\x70\x70\x6F\x72\x74\x20\x74\x68\x65\x20\x63\x72\x65\x61\x74\x6F\x72\x20\x6F\x66\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x2C\x20\x6E\x6F\x74\x20\x74\x68\x65\x20\x48\x6F\x74\x41\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E"

def swaphex(file, offset, bytes, filepath = None):
    if filepath == None:
        global script_dir
        path = os.path.join(script_dir, file)
    else:
        path = filepath

    if type(offset) is list:
        offset = offset[0]
    if offset < 25:
#        logging.info("While editing", path, "offset was stated as ", offset, "\nMost likely source is an error when performing the find_hex function.")
        return

    if not os.path.isfile(path):
        error_message = "File not found: " + path
        messagebox.showinfo("File not found", error_message)
        return
    for _ in range(3):
        try:
            with open(path, "r+b") as f:
#debug                f.seek(offset)
#debug                read = f.read(len(bytes))
#debug                f.flush()
                f.seek(offset)
                f.write(bytes)
                f.flush()
                f.seek(offset)
                written = f.read(len(bytes))
#debug                if read != bytes:
#debug                    print(f"MISMATCH in {file}, offset: 0x{offset:X}")
#debug                    print(f"in_default: {read}")
#debug                    print(f"in_MKC_false: {written}")
                if written != bytes:
                    raise IOError("Verification failed")
            print(f"{file} patched at 0x{offset:X}") 
#            if file == DAT:
#                print(f"{file} patched at 0x{offset:X}") 
            return
        except PermissionError:
            pass
#            time.sleep(0.1)
        except IOError as e:
            messagebox.showinfo("IOError while verifying %s: %s", e)

    messagebox.showinfo("Failed to patch %s at offset 0x%X", path, offset)
    messagebox.showinfo("Expected bytes: %s, got: %s", bytes, written)
    
    
def find_hex(file, hex_to_find, filepath = None, def0 = True):
    offsets = []
    if filepath == None:
        global script_dir
        path = os.path.join(script_dir, file)
    else:
        path = filepath
    if not os.path.isfile(path):
#        logging.error("File not found: %s", path)
#        raise FileNotFoundError(path)
        offsets = [0]
        return offsets
    with open(path, 'rb') as f:
        data = f.read()
        index = data.find(hex_to_find)
        while index != -1:
            offsets.append(index)
            index = data.find(hex_to_find, index + 1)
    if def0 and not offsets:
        offsets = [0]
    return offsets


def main():
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        confirmation = messagebox.askokcancel("Uninstalling Pumpkin Patch", "Are you sure you want to uninstall the Pumpkin Patch?")
        if not confirmation:
            return
        
        if not os.path.isfile(hota_EXE):
            messagebox.showerror("ERROR - Wrong Folder", "Uninstaller run in incorrect folder. Please run the uninstaller in a folder containing the Pumpkin Patch.")
            return
        if not os.path.isfile(backup_zip):
            messagebox.showerror('BACKUP folder not found.')
            return
        with zipfile.ZipFile(backup_zip, 'r') as backup:
            uninstaller_names = {
                "uninstall_pumpkin_patch.exe",
                "uninstall_pp.exe",
                "uninstallpp.exe",
            }
        
            for member in backup.infolist():
                filename = os.path.basename(member.filename).lower()
        
                if filename in uninstaller_names:
                    print(f"Skipping {member.filename}")
                    continue
        
                backup.extract(member, script_dir)
                print(f"Restored: {member.filename}")

        messagebox.showinfo("Backup restored", f"Backup restored into: {script_dir}")

        delete_maps_list = ["Sir Mullich's Charge", "Secrets of the Pumpkin Patch", "Secrets of the PP", "[Pumpkin Patch] Secrets", "[Pumpkin Patch] Secrets - Copy", "[Pumpkin Patch] Charge"]
        delete_templates_list = ["Duel 3.0", "Duel 3.0 t+", "Duel 3.0a", "Duel 3.0a t+", "Jebus Cross Pumpkin Patch", "Jebus Cross - PP", "Jebus Cross PP", "Memory Lane 1.8.2 PP", "Memory Lane PP", "Memory Lane 1.90", "Memory Lane - PP", "Memory Lane", "Memory Lane 1.8.2 - PP", "Memory Lane 1.9.0 PP", "Memory Lane 1.9.0 - PP", "6lm10a - PP", "6lm10a PP", "Memory Lane 1.82 PP", "Memory Lane 1.90 - PP"]
        delete_folders_list = ["alternative", "Icons", "mkc", "modded", "original"]
        delete_files_in_data_list = ["UnFacNJ.wav", "UnFact.wav"]
        delete_files_list = ["_HOTA BACKUP.zip", "HexSwapper.exe"]
    
        for mapname in delete_maps_list:
            mapname = str(mapname) + ".h3m"
            try:
                os.remove(os.path.join(script_dir, "Maps", mapname))
            except Exception:
                pass
            try:
                os.remove(os.path.join(script_dir, "Maps", mapname.lower()))
            except Exception:
                pass
        
        for templatename in delete_templates_list:
            templatename = str(templatename) + ".h3t"
            try:
                os.remove(os.path.join(script_dir, "HotA_RMGTemplates", templatename))
            except Exception:
                pass
            try:
                os.remove(os.path.join(script_dir, "HotA_RMGTemplates", templatename.lower()))
            except Exception:
                pass
    
    
        for filename in delete_files_in_data_list:
            if filename is not None:
                try:
                    os.remove(os.path.join(script_dir, "Data", str(filename)))
                except Exception:
                    pass
                try:
                    os.remove(os.path.join(script_dir, "Data", str(filename).lower()))
                except Exception:
                    pass
    
        for foldername in delete_folders_list:
            if foldername is not None:
                try:
                    shutil.rmtree(os.path.join(script_dir, "Data", str(foldername)))
                except Exception:
                    pass
                try:
                    shutil.rmtree(os.path.join(script_dir, "Data", str(foldername).lower()))
                except Exception:
                    pass

        text_offset = find_hex(hd_dll, new_text)[0]
        if not text_offset:
            print("Could not find hex offset in DLL.")
        #update_specialty_images(b"\x32", b"\x34")

        path = os.path.join(script_dir, hd_dll)
        if os.path.isfile(path):
           swaphex(hd_dll, text_offset, original_text)

        messagebox.showinfo("HD_HOTA.dll updated", "Pumpkin changes have been reverted for the file.")

        if os.path.exists(hexswapper_EXE):
            os.remove(hexswapper_EXE)
            
        if os.path.exists(Icons):
            shutil.rmtree(Icons)

        messagebox.showinfo("HexSwapper removed", "HexSwapper.exe has been deleted. ")

    except Exception as e:
        messagebox.showinfo("Error", f"Uninstaller failed: {e}")

if __name__ == "__main__":
    main()















