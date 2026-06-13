# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 19:15:13 2025

@author: CsArOs
"""

import configparser, time, sys, subprocess, os, webbrowser, datetime, psutil, base64
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from MMArchiveCLI import add_to_archive

#Get the folder where the EXE or script is actually running from
if getattr(sys, 'frozen', False):
    #Running as .exe (frozen by PyInstaller)
    script_dir = os.path.dirname(sys.executable)
else:
    #Running as .py script
    script_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(script_dir)

from SpellBook import HEX, HEX_EN, HEX_MKC, HEX_Presets #, HEX_ES, HEX_PL, 


if getattr(sys, 'frozen', False):
    #Running as .exe (frozen by PyInstaller)
    icons_dir = sys._MEIPASS
else:
    #Running as .py script
    icons_dir = os.path.dirname(os.path.abspath(__file__))

icons_dir = os.path.join(icons_dir, "Icons")

ini_path = os.path.join(script_dir, 'PP.ini')

#File definitions
EXE = "h3hota HD.exe"
DAT = "HotA.dat"
MPD = "h3hota_maped.exe"
hd_dll = "HD_HOTA.dll"
hota_dll = "HotA.dll"
EXE_DUEL = "h3hota 1hero.exe"
DAT_DUEL = "HoPP.dat"
hota_dll_DUEL = "HoPP.dll"
#swaphex_tracker = False

MEDIAFIRE_PAGE = (
    "https://www.mediafire.com/file/x0f010q9nk9pomc/Pumpkin_Patch.zip/file"
)  # human-facing link
FILE_KEY = "x0f010q9nk9pomc"  # the bit after /file/
VERSION_FILE = "PP_version.txt"
ZIP_NAME = "Pumpkin_Patch.zip"
TEMP_DIR = "PP_temp"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get_remote_info() -> str:
    url = (
        f"https://www.mediafire.com/api/file/get_info.php?"
        f"quick_key={FILE_KEY}&response_format=json"
    )
    data = requests.get(url, headers=UA, timeout=20).json()
    if data["response"]["result"] != "Success":
        raise RuntimeError(data["response"]["message"])

    info = data["response"]["file_info"]

    created_raw = info["created"]            # may be "2025-07-29 11:10:21"
    if created_raw.isdigit():                # old epoch format
        date_str = datetime.datetime.utcfromtimestamp(int(created_raw)).strftime("%Y-%m-%d")
    else:                                    # parse "YYYY-MM-DD HH:MM:SS"
        date_str = created_raw.split(" ")[0]

    return date_str

def check_for_updates():
    version_path = os.path.join(script_dir, VERSION_FILE)

    if os.path.exists(version_path):
        with open(version_path, "r", encoding="utf-8") as f:
            local_date = f.read()
    else:
        local_date = "1970-01-01"
           
    # remote version
    try:
        remote_date = get_remote_info()
    except Exception as e:
        print(e)
        return

    try:
        datetime.datetime.strptime(local_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showinfo("New version detected", ("Update available! Please visit the wiki and download the new version of the mod. \n\nMod last updated: " + local_date + "\nNew version uploaded: " + remote_date))
#        webbrowser.open("https://drive.google.com/file/d/1XuZ5PwzePxSIgP6uMOXN96jt0F5QpEBU/view?usp=sharing")
        webbrowser.open("https://www.mediafire.com/file/x0f010q9nk9pomc/Pumpkin_Patch.zip/file")
        return        

    try:
        datetime.datetime.strptime(local_date, "%Y-%m-%d")
    except ValueError:
        return        

    if remote_date > local_date:
        messagebox.showinfo("New version detected", ("Update available! Please visit the wiki and download the new version of the mod. \n\nMod last updated: " + local_date + "\nNew version uploaded: " + remote_date))
#        webbrowser.open("https://drive.google.com/file/d/1XuZ5PwzePxSIgP6uMOXN96jt0F5QpEBU/view?usp=sharing")
        webbrowser.open("https://www.mediafire.com/file/x0f010q9nk9pomc/Pumpkin_Patch.zip/file")
        return

    return


def confirmhex(filename, offset, byte, filepath = None):
    if filepath == None:
        global script_dir
        path = os.path.join(script_dir, filename)
    else:
        path = filepath

    if type(offset) is list:
        offset = offset[0]
    
    if offset < 150:
        return True

    if not os.path.isfile(path):
        error_message = "File not found: " + path
        messagebox.showinfo("File not found", error_message)
        return False
    for i in range(3):
        try:
            with open(path, "r+b") as f:
                f.seek(offset)
                read = f.read(len(byte))
                if read != byte:
                    #print(f"0x{offset:X}, read: {read}, bytes: {byte}")
                    return False
                return True
        except PermissionError:
            time.sleep(0.01)
        except IOError as e:
            messagebox.showerror("Error", f"IOError while verifying {e}: {e}")
    return True

def swaphex(filename, offset, byte, filepath = None, find_and_swap = False, byte_to_find = None, skip_zero = False):    
#    global swaphex_tracker 
    global file_not_found
    if filepath == None:
        global script_dir
        path = os.path.join(script_dir, filename)
    else:
        path = filepath

#    print(filename, offset, byte, find_and_swap, byte_to_find, filepath, skip_zero)

    if find_and_swap:
        offset = find_hex(filename, byte_to_find)[0]
    if type(offset) is list:
        offset = offset[0]
    if offset < 100:
#        print("While editing", path, "offset was stated as ", offset, "\nMost likely source is an error when performing the find_hex function.")
        return

    if not os.path.isfile(path):
        if not file_not_found:
            error_message = "File not found: " + path
            messagebox.showinfo("File not found", error_message)
            file_not_found = True
        return
    for i in range(3):
        try:
            with open(path, "r+b") as f:
#debug                f.seek(offset)
#debug                read = f.read(len(byte))
#debug                f.flush()
                f.seek(offset)
                f.write(byte)
                f.flush()
                f.seek(offset)
                read = f.read(len(byte))
#                if read != byte:
#                    print(f"MISMATCH in {filename}, offset: 0x{offset:X}")
#                    print(f"in_default: {read}")
#                    print(f"in swap: {byte}")
                if read != byte:
                    if not confirmhex(filename, offset, byte):
                        messagebox.showinfo("Warning", f"Failed to patch {path} at offset 0x{offset:X}. Expected bytes: {byte}, got: {read}")
                    raise IOError("Verification failed")
            print(f"{filename} patched at 0x{offset:X}") 
#            if filename == DAT:
#                print(f"{filename} patched at 0x{offset:X}, with {byte[:20]}") 
#            if swaphex_tracker:
#                messagebox.showinfo("Debug", f"Just swapped hex in {filename}, at 0x{offset:X}. \n\n{byte}")
            return
        except PermissionError:
            time.sleep(0.1)
        except IOError as e:
            messagebox.showerror("Error", f"IOError while verifying {e}: {e}")
    return


def find_hex(file, hex_to_find, filepath = None, def0 = True):
    offsets = []
    if filepath == None:
        global script_dir
        path = os.path.join(script_dir, file)
    else:
        path = filepath
    if not os.path.isfile(path):
        #print("File not found: %s", path)
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


def LOD_ADD(folder, filename, archive):
    MMArchiveConfig = type('Config', (), {'ignore_unzip_errors': True})()
    archivepath = os.path.join(script_dir, "Data", archive)
    if folder == "":
        filepath = os.path.join(script_dir, "Data", filename)
    else:
        filepath = os.path.join(script_dir, "Data", folder, filename)
    add_to_archive(archivepath, filepath, MMArchiveConfig)
    #print("from folder", folder)

def check_language():
    polish_sample = b"towarzystw"
    polish_offset_list = find_hex(DAT, polish_sample)
    if len(polish_offset_list) > 1:
        language = "polish"
    else: 
        language = "english"
    return language

#Read the INI file. 
config = configparser.ConfigParser()
config.optionxform = str  #preserve original key casing
if not os.path.exists(ini_path):
    config.add_section("HexSwapper")
    config.set("HexSwapper", "Language", str(check_language()))
    config.set("HexSwapper", "Balanced", str(False))   
    config.set("HexSwapper", "Custom", str(False))   
    config.set("HexSwapper", "Duel", str(False))   
    config.set("HexSwapper", "Basic", str(True))   
    config.add_section("Optional features")
    config.add_section("Skins")
    config.set("Skins", "Catherine", str("dor"))
    with open(ini_path, "w") as f:
        config.write(f)

config.read(ini_path)
if 'HexSwapper' in config:
    main = config['HexSwapper']
else:
    config.add_section("HexSwapper")
    main = config['HexSwapper']
    config.set("HexSwapper", "Balanced", str(False))   
    config.set("HexSwapper", "Custom", str(False))   
    config.set("HexSwapper", "Duel", str(False))   
    config.set("HexSwapper", "Basic", str(True))   
    config.set("HexSwapper", "Language", str(check_language()))
    print("Warning: [HexSwapper] section was missing, added empty one.")

if 'Optional features' in config:
    features = config['Optional features']
else:
    config.add_section("Optional features")
    features = config['Optional features'] = {}
    print("Warning: [Optional features] section was missing, added empty one.")

if 'Skins' in config:
    skins = config['Skins']
else:
    config.add_section("Skins")
    skins = config['Skins']
    config.set("Skins", "Catherine", str("dor"))
    print("Warning: [Skins] section was missing, added empty one.")

for i, spell in enumerate(HEX):
    patches = HEX.get(spell, {})
    if not patches:
        print("Unknown key in INI: %s", spell)
        continue
    entries = patches.get('link', [])
    if entries is None or not entries:
        break
    link = str(entries[0])
    config.set("HexSwapper", spell, link)             
    if i > 5:
        break
with open(ini_path, "w") as f:
    config.write(f) 
        
#language_local = main.get('Language', fallback='english')
#if language_local == 'english':
#    print("THE LANGUAGE IS ENGLISH")
extra_hex = HEX_EN
#elif language_local == 'polish':
#    print("THE LANGUAGE IS POLISH")
#    extra_hex = HEX_PL
#else:
#    hota_ini_path = os.path.join(script_dir, 'HotA_Settings.ini')
#    config.read(hota_ini_path)
#    if 'Global Settings' in config:
#        hota_ini = config['Global Settings']
#        language = hota_ini.get('Language', fallback=0)
#        extra_hex = HEX_EN
#    else: 
#        language = 0
#        extra_hex = HEX_EN

#    if language == 2: 
#        extra_hex = HEX_PL
#    else: 
#        extra_hex = HEX_EN    

#HD DLL stuff
original_text = b"\x4F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x20\x69\x73\x20\x70\x61\x72\x74\x20\x6F\x66\x20\x74\x68\x65\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x48\x6F\x74\x41\x20\x43\x72\x65\x77"
new_text = b"\x4F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x20\x69\x73\x20\x70\x61\x72\x74\x20\x6F\x66\x20\x74\x68\x65\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x48\x6F\x74\x41\x20\x43\x72\x65\x77\x20\x68\x61\x73\x20\x7B\x6E\x6F\x74\x68\x69\x6E\x67\x7D\x20\x74\x6F\x20\x64\x6F\x20\x77\x69\x74\x68\x20\x74\x68\x65\x20\x6F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x2E\x0A\x0A\x48\x6F\x74\x41\x20\x69\x73\x20\x61\x20\x6E\x6F\x6E\x2D\x70\x72\x6F\x66\x69\x74\x20\x70\x72\x6F\x6A\x65\x63\x74\x2C\x20\x61\x6E\x64\x20\x74\x68\x65\x79\x20\x68\x61\x76\x65\x6E\x27\x74\x20\x61\x63\x63\x65\x70\x74\x65\x64\x20\x61\x6E\x79\x20\x64\x6F\x6E\x61\x74\x69\x6F\x6E\x73\x20\x6F\x76\x65\x72\x20\x31\x36\x20\x79\x65\x61\x72\x73\x20\x6F\x66\x20\x64\x65\x76\x65\x6C\x6F\x70\x6D\x65\x6E\x74\x2E\x20\x42\x79\x20\x73\x75\x70\x70\x6F\x72\x74\x69\x6E\x67\x20\x74\x68\x65\x20\x6C\x6F\x62\x62\x79\x20\x79\x6F\x75\x20\x73\x75\x70\x70\x6F\x72\x74\x20\x74\x68\x65\x20\x63\x72\x65\x61\x74\x6F\x72\x20\x6F\x66\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x2C\x20\x6E\x6F\x74\x20\x74\x68\x65\x20\x48\x6F\x74\x41\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x0A\x0A\x0A\x16\x18\x43\x73\x41\x72\x4F\x73\x7D\x3A\x0A\x7B\x50\x75\x6D\x70\x6B\x69\x6E\x7D\x20\x7B\x50\x61\x74\x63\x68\x7D\x20\x69\x73\x20\x63\x6F\x6D\x70\x61\x74\x69\x62\x6C\x65\x20\x77\x69\x74\x68\x20\x74\x68\x65\x20\x6F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x2C\x20\x62\x75\x74\x20\x69\x74\x20\x69\x73\x20\x6E\x6F\x74\x20\x61\x64\x76\x69\x73\x65\x64\x20\x74\x6F\x20\x70\x6C\x61\x79\x20\x61\x6E\x79\x20\x72\x61\x6E\x6B\x65\x64\x20\x67\x61\x6D\x65\x73\x2E\x20\x49\x6E\x20\x63\x61\x73\x65\x20\x6F\x66\x20\x61\x6E\x79\x20\x69\x73\x73\x75\x65\x73\x2C\x20\x76\x69\x73\x69\x74\x20\x74\x68\x65\x20\x50\x75\x6D\x70\x6B\x69\x6E\x20\x50\x61\x74\x63\x68\x20\x44\x69\x73\x63\x6F\x72\x64\x20\x73\x65\x72\x76\x65\x72\x2E\x20"

data_dir = os.path.join(script_dir, "Data")
mod_dir = os.path.join(script_dir, "Pumpkin Patch.zip")
PL_dir = os.path.join(script_dir, "Polish version.zip")

HEX |= extra_hex
HEX |= HEX_MKC

def list_templates_and_names():
    global script_dir
    if not os.path.exists(os.path.join(script_dir, "HotA_RMGTemplates")):
        templates, template_names = [], []
        return templates, template_names
    else: 
        directory = os.path.join(script_dir, "HotA_RMGTemplates")
    templates = [
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]
    template_names = [os.path.splitext(t)[0] for t in templates]
    return templates, template_names

def confirm(name, state, depth = False, override = False, MKC = True, MKC_only = False):
    #print("confirming:", name, state)
    patches = HEX.get(name, {})
    if not patches:
        print("Unknown key in INI: %s", name)
        return

    entries = patches.get(state, [])
    if not entries:
        print(f"No entries found for state {state} in key {name}")
        return

    if name in ["MKC_balance", "MKC_compatibility", "MKC_TRUE"]:
        Accuracy_local = 100
    elif name in skins_list:
        Accuracy_local = 1
    if depth is not False:
        try:
            Accuracy_local = int(depth)
        except ValueError:
            Accuracy_local = 3
    else:
        Accuracy_local = 1        
    swaps = min(len(entries), int(Accuracy_local))
    i = 0
    while i < swaps:
        entry = entries[i]
    
        if isinstance(entry, tuple) and entry[0] == 'file':
            _, folder, filename, archive = entry
            LOD_ADD(folder, filename, archive)
    
            if swaps < len(entries):
                swaps += 1

        else:
            target, offset, data = entry
            if name in ["MKC_balance", "MKC_compatibility", "MKC_TRUE"]:
                TARGET_DUEL_MAP = {
                    EXE: EXE_DUEL,
                    EXE_DUEL: EXE_DUEL,
                    hota_dll: hota_dll_DUEL,
                    DAT: DAT_DUEL,
                    hd_dll: hd_dll,
                    MPD: MPD,
                    }        
                target_duel = TARGET_DUEL_MAP.get(target)
                if not target_duel is None:
                    target = target_duel
                else:
                    break
            if not confirmhex(target, offset, data):
                apply(name, state, override = override, MKC = MKC, MKC_only = MKC_only)
                break    
        i += 1
        
    #print("confirmed", name, state)
    return

def apply(name, state, override = False, MKC = True, MKC_only = False):
    global file_not_found
    file_not_found = False
    patches = HEX.get(name, {})
    if not patches:
        print("Unknown key in INI: %s", name)
        return

    entries = patches.get(state, [])
    if not entries:
        print(f"No entries found for state {state} in key {name}")
        return

#    global swaphex_tracker 
#    if not messagebox.askyesno("DEBUG", f"Trying to apply {name}, {state}. Continue?"):
#        swaphex_tracker = True
#    else:
#        swaphex_tracker = False        

    for entry in entries:
        if isinstance(entry, tuple) and entry[0] == 'file':
            _, folder, filename, archive = entry
            LOD_ADD(folder, filename, archive)
        else:
            target, offset, data = entry
            if (not (MKC_only or (name == "MKC_TRUE" and not override))):
                swaphex(target, offset, data)
#                text = "APPLIED" + str(name) + str(state)
#                messagebox.showinfo("info", text)
#            else:
#                print("DID NOT APPLY", name, "with state", state, "; MKC_TRUE:", bool(name == 'MKC_TRUE'), "OVERRIDE", bool(override), "MKC_ONLY:", bool(MKC_only))
                
            if MKC and (name in skins_list or (
                    not get_preset_state("Duel", name) is None and state == get_preset_state("Duel", name)
                    )):
                TARGET_DUEL_MAP = {
                    EXE: EXE_DUEL,
                    EXE_DUEL: EXE_DUEL,
                    hota_dll: hota_dll_DUEL,
                    DAT: DAT_DUEL,
                    hd_dll: hd_dll,
                    MPD: MPD,
                    }        
                target_duel = TARGET_DUEL_MAP.get(target)
                if not target_duel is None:
                    swaphex(target_duel, offset, data)                        
    return

def convert_value(value):
    true_values = {'true', 'yes', 'on'}
    false_values = {'false', 'no', 'off'}

    lower_val = value.strip().lower()

    if lower_val in true_values:
        return True
    elif lower_val in false_values:
        return False

    try:
        return int(lower_val)
    except ValueError:
        try:
            return float(lower_val)
        except ValueError:
            return lower_val

def get_valid_states(key):
#    print("\n getting valid state of:", key)
    patch_dict = HEX.get(key, {})
    return list(patch_dict.keys())

current_states = {}

def get_hex_state(name, category):
    value = category.get(name)
    if value is None:
        #print("state of", name, "was None, so now its", value)
        values_list = get_valid_states(name)
        value = values_list[0] if values_list else None
        return value
    converted = convert_value(value)
    valid_states = HEX.get(name, {}).keys()
    if converted in valid_states:
        #print("getting hex state of:", name, "which IS", value)
        return converted
    else:
        values_list = get_valid_states(name)
        value = values_list[0] if values_list else None
        confirm(name, value, depth=False)
        #print("resetting hex state for:", name, "to:", value)
        return value

def safe_config_set(config, section, key, value):
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, key, str(value))
    with open(ini_path, 'w') as configfile:
        config.write(configfile)

def update_ini():
    #writes reseted ini
    for btn_list in [
            BUTTONS_Gameplay, 
            BUTTONS_Skins, 
            BUTTONS_Skins2, 
            BUTTONS_Skins3, 
            BUTTONS_PRESET, 
            ]:
        for b in btn_list:
            name = b['name']
            if b['current_state'] is None and not b['arrow']:
                b['current_state'] = get_hex_state(name, b['category'])
            if b['category_name'] is not None:
                config.set(b['category_name'], name, str(b['current_state']))
    with open(ini_path, 'w') as configfile:
        config.write(configfile)
    return

def is_exe_open():
    global script_dir
    game_exe = os.path.normcase(os.path.join(script_dir, EXE))

    for proc in psutil.process_iter(['exe']):
        try:
            exe_path = proc.info['exe']
            if exe_path and os.path.normcase(exe_path) == game_exe:
                return True
        except Exception as e:
            print(e)
            continue  # skip if we can't access exe, f.e. because its Linux
    return False
    
def on_apply_preset(preset, presets_only = False):
    global Preset_On
    if not (preset == "MKC_balance" and Preset_On == "Duel"):
        Preset_On = preset

    for master_state, item_list in HEX_Presets[preset].items():
        for item in item_list:
            if presets_only and not item in preset_list:
                continue

            print(item)
            button1 = BUTTONS_Gameplay_MAP.get(item)
            button2 = BUTTONS_PRESET_MAP.get(item)
            #print(item, "gmpl btn", button1, "preset btn", button2)
            #bandaid solution
            if str(item).lower() == str(Preset_On).lower():
                for button in [button1, button2]:
                    if button is None:
                        continue
                    button['current_state'] = True
                    if button['category_name'] is not None:
                        config.set(button['category_name'], Preset_On, str(True))
            elif master_state == "self":
                continue
            elif master_state == "extra":
                if item == "HeroLimit":
                    state = 11
                else:
                    state = True
                if not (Preset_On in ["Duel"]):
                    apply(item, state)
                for button in [button1, button2]:
                    if button is None:
                        continue
                    button['current_state'] = state
                    if button['category_name'] is not None:
                        config.set(button['category_name'], button['name'], str(state))
            elif master_state == "ANTIextra":
                state = False
                if not (Preset_On in ["Duel"]):
                    apply(item, state)
                for button in [button1, button2]:
                    if button is None:
                        continue
                    button['current_state'] = state
                    if button['category_name'] is not None:
                        config.set(button['category_name'], button['name'], str(state))
            elif str(item).lower() == "catherine":
                button3 = BUTTONS_Skins_Map.get(item)
                state = master_state
                apply(item, state)
                #print(button3)
                button3['current_state'] = state
                if button3['category_name'] is not None:
                    config.set(button3['category_name'], button3['name'], str(state))
            else:
                state = master_state
                for button in [button1, button2]:
                    if button is None:
                        continue
                    current_state = button['current_state']
                    if current_state != state:
                        if not (Preset_On in ["Duel"]):
                            apply(item, state)
                        button['current_state'] = state
                        if button['category_name'] is not None:
                            config.set(button['category_name'], button['name'], str(state))
                    else:
                        confirm(button['name'], state, depth=4)
                
    with open(ini_path, 'w') as configfile:
        config.write(configfile)
    check_swaps(depth=4)
    return

def get_preset_state(preset_name, item_name):
    #print("\ngetting preset state of:", item_name, "for preset:", preset_name)
    for state, items in HEX_Presets[preset_name].items():
        if item_name in items:
            return state
    return None


x_pos_list_skins = (70, 150, 230, 310, 390, 470, 70, 150, 230, 310, 390, 470, 70, 150, 230, 310, 390, 470, 70, 150, 230, 310, 390, 470, 70, 150, 230, 310, 0)
y_pos_list_skins = (151, 151, 151, 151, 151, 151, 237, 237, 237, 237, 237, 237, 323, 323, 323, 323, 323, 323, 409, 409, 409, 409, 409, 409, 495, 495, 495, 495, 0)


x_pos_list_features = (56, 314, 56, 314, 56, 314, 56, 314, 56, 314, 56, 314, 56, 314, 56, 314, 56, 314, 56, 314, 56, 314, 0)
y_pos_list_features = (144, 144, 188, 188, 232, 232, 276, 276, 320, 320, 364, 364, 408, 408, 452, 452, 496, 496, 0)


NONE_DICT = [
    {'pos': None, 'arrow': None, 'current_state': None, 'button': None},
    ]

ARROW_DICT = [
    {'arrow': True, 'current_state': True, 'button': True},
    ]


BUTTONS_HexSwapperMenu = [
    {'name': 'Home', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (615, 25), 'description': "HexSwapper's Main Menu"},
    {'name': 'Gameplay', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (587, 142), 'description': "Gameplay Menu"},
    {'name': 'Skins', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (620, 257), 'description': "Skins Menu"},
    {'name': 'Reset', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (622, 365), 'description': "Reset all options to their default values. \n\nTakes a few seconds to load."},
    {'name': 'Play', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (625, 477), 'description': "Close the HexSwapper and play!"},
]

BUTTONS_HOME2 = [
#    {'name': 'HallOfFame_pressed', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (430, 506), 'description': "Hall of Fame"},
    {'name': 'PumpkinRace2025', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (124, 182), 'description': "Heroes 3 Wiki"},
    {'name': 'Popawasia', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (261, 182), 'description': "Popawasia's twitch channel"},
    {'name': 'Keszu', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (339, 182), 'description': "Keszu's youtube channel"},
    {'name': 'Qweder', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (417, 182), 'description': "Qweder's channel"},
]

BUTTONS_HOME = [
#    {'name': 'Wiki2', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (465, 455), 'description': "Full Changelog"},
    {'name': 'HallOfFame', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (430, 506), 'description': "Hall of Fame"},
    {'name': 'Wiki2', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (74, 546), 'description': "Full Changelog"},
    {'name': 'Wiki', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (76, 497), 'description': "Heroes 3 Wiki"},
    {'name': 'Feedback', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (75, 522), 'description': "Feedback Form"},   
    {'name': 'Coffee', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (235, 495), 'description': "You can buy me a coffee here"},   
    {'name': 'Discord', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (236, 523), 'description': "Discord: Pumpkin Patch server"},
    {'name': 'Youtube', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (237, 549), 'description': "Youtube: CsArOs"},   
    {'name': '-Wiki2', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (96, 548), 'description': "Full Changelog"},
    {'name': '-Wiki', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (96, 499), 'description': "Heroes 3 Wiki"},
    {'name': '-Discord', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (257, 523), 'description': "Discord: Pumpkin Patch server"},
    {'name': '-Youtube', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (257, 548), 'description': "Youtube: CsArOs"},   
    {'name': '-Feedback', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (96, 523), 'description': "Feedback Form"},   
    {'name': '-Coffee', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (257, 499), 'description': "You can buy me a coffee here"},   
#    {'name': 'LinkTree', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (250, 492), 'description': "LinkTree"},   
#    {'name': 'DeveloperMode', 'category': main, 'category_name': "HexSwapper", **NONE_DICT[0], 'pos': (509, 439), 'description': "Activate developer mode."},   
]


BUTTONS_PRESET = [
    {'name': 'Basic', 'Priority': False, 'category': main, 'category_name': "HexSwapper", **NONE_DICT[0], 'pos': (64, 177), 'description': 'Select the Basic preset. \n\nDisables all optional features. \nSets the hero limit to 8, and the luck and morale scale from -3 to 3.'},        
    {'name': 'Balanced', 'Priority': False, 'category': main, 'category_name': "HexSwapper", **NONE_DICT[0], 'pos': (64, 251), 'description': "Select the Balanced preset. \n\nEnables the following settings:\nExpanded Luck and Morale limit (5), \nNew heroes on random maps, \nZenith replaces Straker, \nUnique starting armies, \nNew creature banks for Landlocked maps, \nNew creature skills, \nPrimary stat increase is constant, \nRemove Pandora pop-ups, \nLift magic skill restrictions, \nStatic spell specialties, \nMerge Artillery and Ballistics."},        
    {'name': 'Duel', 'Priority': True, 'category': main, 'category_name': "HexSwapper", **NONE_DICT[0], 'pos': (64, 325), 'description': "Select the Duel preset. \n\nDisables all optional features except for the following:\nHero Limit (1), \nExpanded Luck and Morale limit (5), \nNew Heroes on random maps, \nRemove Pandora pop-ups, \nSkill rebalance for 1-hero, \nMKC's gameplay rebalance, \nControl Scrolls from day 1, \nDuel 3.0 generation."},        
    {'name': 'Custom', 'Priority': False, 'category': main, 'category_name': "HexSwapper", **NONE_DICT[0], 'pos': (64, 399), 'description': "Select a Custom preset."},        
    ]

preset_list = ["Duel", "MKC_duel", "MKC_balance"] + [p["name"] for p in BUTTONS_PRESET]#, "DeveloperMode"]

Preset_On = False

for preset in preset_list:
    #print(preset, "is in preset list")
    if preset in ["Duel", "MKC_balance"]:
        if get_hex_state(preset, features):
            Preset_On = preset
            #print("ON!!!", Preset_On)
            break
    if get_hex_state(preset, main):
        Preset_On = preset
        #print("on!!!", Preset_On)
        break

if Preset_On == False:
    Preset_On = "Custom"

BUTTONS_Gameplay = [
    {'name': 'HeroLimit', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Switch between 1-hero, 3-hero and 8-hero modes. \n1 hero: Players cannot purchase more than 1 hero to wander the map at once. \nAI does not buy more than 1 hero. View Air shows enemy heroes without Air Magic skill. \n\n3 hero: Players can only purchase 3 heroes at a time, including the garrisoned heroes. \nAI purchases less heroes than before. \n\n8 heroes: Standard heroes 3 gameplay."},  
    {'name': 'ExpandedLuckMoraleScale', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Expands the maximum and minimum Morale and Luck to the chosen value. \nThe odds scale linearly, i.e. +5 luck is 5/24 odds for a lucky strike."},
    {'name': 'NewHeroesByDefault', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Enables the following heroes on random maps: \nAthe (Heretic, Diplomacy specialist), \nArchibald (Warlock, Tactics specialist), \nGwenneth (Cleric, Scholar specialist), \nWinstan (Alchemist, Precision specialist)."},
    {'name': 'Zenith', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Replaces Straker (Death Knight, Zombie specialist) with Zenith (Necromancer, Mummy specialist). \nZenith can upgrade Walking Dead and Zombies into Mummies."},
    {'name': 'UniqueStartingArmies', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "All heroes start with units they specialize in, except for the level 7 units."},
    {'name': 'PrimaryStatsIncreaseIsConstant', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Primary stat increase for each hero class does not change after level 10."},
    {'name': 'StaticSpellSpecialties', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Changes all level-scaling spell speciatlies for a static 25% bonus."},
    {'name': 'LiftMagicRestrictions', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Allows Rangers, Overlords, Beastmasters, Barbarians and Mercenaries to learn Water and Fire magic, but with very low probability."},
    {'name': 'NewCreatureSkills', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Familiars can fly, at an increased price per unit. \nWar Unicorns can cast Magic Mirror for 3 rounds, once per battle.\nHorned demons benefit from the jousting bonus, \nat an increased price and decreased health per unit. "},
    {'name': 'RemoveBallistics', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Merges the Artillery and Ballistics skills."},
    {'name': 'NoPandoraConfirmation', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Replaces pick-up and fight messages from Pandora boxes. Not recommended for custom scenarios."},
    {'name': 'MKC_scrolls', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "All heroes start with the three control spell scrolls. \nRecommended for Duel 3.0."},
    {'name': 'NewCreatureBanks', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Adds two new creature banks: Mountain Caverns and Underground Factories."},
    {'name': 'MKC_skills', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Improves Estates, First Aid and Mysticism; reduces the bonus of Scouting and Logistics."},
    {'name': 'MergeTPDD', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Moves Town Portal and Dimension Door both to all schoools of magic.\n\nWhile the option is disabled, Town Portal belongs to Earth and Water magic, \nwhile Dimension Door belongs to Air and Fire magic."},
]

BUTTONS_Hidden = [
#    {'name': 'MKC_duel', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Activates the Duel preset."},
    {'name': 'StaticSpellSpecialties2', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "No description"},
    {'name': 'MKC_TRUE', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "No description"},
    {'name': 'MKC_compatibility', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "No description"},
    {'name': 'XPcalc', 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "XP is a function of AI value / 16, instead of the enemy HP."},
    {'name': 'MKC_balance', 'Priority': True, 'category': features, 'category_name': "Optional features", **NONE_DICT[0], 'description': "Extensive gameplay rebalance for 1hero gameplay, designed by MKC. \nEnabling this setting may switch some of the other options. \nYou can read more about it on https://www.h3templates.com/content/po \n\nDue to the sheer number of changes, it takes a few seconds to load."},
]

BUTTONS_PRESET_MAP = {b["name"]: b for b in  BUTTONS_PRESET + BUTTONS_HOME}
BUTTONS_Gameplay_MAP = {b["name"]: b for b in  BUTTONS_Gameplay + BUTTONS_Hidden}

BUTTONS_Skins = [
    {'name': 'Edric', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Edric"},
    {'name': 'LordHaart', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Lord Haart"},
    {'name': 'Catherine', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Sorsha / Catherine"},
    {'name': 'Christian', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Christian"},
    {'name': 'Tyris', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Tyris"},
    {'name': 'Roland', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Roland"},
    {'name': 'Rion', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Rion"},
    {'name': 'Adelaide', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Adelaide"},
    {'name': 'Gwenneth', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Gwenneth"},
    {'name': 'Mephala', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Mephala"},
    {'name': 'Jenova', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Jenova"},
    {'name': 'Ivor', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Ivor"},
    {'name': 'Clancy', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Clancy"},
    {'name': 'Gelu', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Gelu"},
    {'name': 'Gem', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Gem"},
    {'name': 'Josephine', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Josephine"},
    {'name': 'Iona', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Iona"},
    {'name': 'Halon', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Halon"},
    {'name': 'Theodorus', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Theodorus"},    
    {'name': 'Solmyr', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Solmyr"},
    {'name': 'Dracon', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Dracon"},
    {'name': 'Fiona', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Fiona"},
    {'name': 'Rashka', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Rashka"},
    {'name': 'Nymus', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Nymus"},
    {'name': 'Xyron', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Xyron"},    
    {'name': 'Zydar', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Zydar"},
    {'name': 'Moandor', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Moandor"},
    {'name': 'Charna', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Charna"},

    {'name': 'Arrow_right', 'category': main, 'category_name': None, **ARROW_DICT[0], 'pos': (470, 511), 'description': "Turn the page"},
]

BUTTONS_Skins2 = [  
    {'name': 'Tamika', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Tamika"},
    {'name': 'Ranloo', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Ranloo"},
    {'name': 'Sandro', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Sandro"},
    {'name': 'Thant', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Thant"},
    {'name': 'Vidomina', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Vidomina"},
    {'name': 'Zenith2', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Zenith"},
    {'name': 'Dace', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Dace"},
    {'name': 'Gunnar', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Gunnar"},
    {'name': 'Archibald2', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Archibald"},
    {'name': 'Mutare', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Mutare (Drake)"},     
    {'name': 'Alamar', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Alamar"},
    {'name': 'Malekith', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Malekith"},
    {'name': 'Jeddite', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Jeddite"},
    {'name': 'Deemer', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Deemer"},
    {'name': 'Sephinroth', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Sephinroth"},
    {'name': 'Darkstorn', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Darkstorn"},
    {'name': 'Yog', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Yog"},
    {'name': 'Shiva', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Shiva"},
    {'name': 'CragHack', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Crag Hack"},
    {'name': 'Tyraxor', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Tyraxor"},
    {'name': 'Gundula', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Gundula"},
    {'name': 'Kilgor', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Kilgor"},
    {'name': 'Bron', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Bron"},
    {'name': 'Drakon', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Drakon"},
    {'name': 'Tazar', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Tazar"}, 
    {'name': 'Wystan', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Wystan"}, 
    {'name': 'Monere', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Monere"},
    {'name': 'Erdamon', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Erdamon"},
#    {'name': 'MainMenu', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Main Menu screen"},    
    {'name': 'Arrow_left', 'category': main, 'category_name': None, **ARROW_DICT[0], 'pos': (390, 511), 'description': "Turn the page"},
    {'name': 'Arrow_right', 'category': main, 'category_name': None, **ARROW_DICT[0], 'pos': (470, 511), 'description': "Turn the page"},
]

BUTTONS_Skins3 = [  
    {'name': 'Luna', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Luna"},
    {'name': 'Ciele', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Ciele"},
    {'name': 'Astra', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Astra"}, 
    {'name': 'Wynona', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Wynona"},
    {'name': 'Wrathmont', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Wrathmont"},
    {'name': 'Agar', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Agar"},
    {'name': 'Wraith', 'category': skins, 'category_name': "Skins", **NONE_DICT[0], 'description': "Wraith"},    
    {'name': 'Arrow_left', 'category': main, 'category_name': "HexSwapper", **ARROW_DICT[0], 'pos': (390, 511), 'description': "Turn the page"},
]

BUTTONS_Skins_Map = {b["name"]: b for b in BUTTONS_Skins3 + BUTTONS_Skins2 + BUTTONS_Skins}
skins_list = [s["name"] for s in BUTTONS_Skins + BUTTONS_Skins2 + BUTTONS_Skins3 if s["name"] ]#not in ["Catherine"]]

def check_swaps(depth = 2, complete = False):
    #print("run check_swaps")
    global Preset_On
    preset_applied = False
    extra_keys = False
    if get_hex_state("Duel", main):
        extra_key, extra_key_state = "MKC_balance", True
        extra_key2, extra_key2_state = "Catherine", "dor"
        extra_key3, extra_key3_state = "MKC_TRUE", True 
        extra_keys = True
    else:
        extra_key, extra_key_state = None, None
        extra_key2, extra_key2_state = None, None
        extra_key3, extra_key3_state = None, None
        
    if get_hex_state("MKC_scrolls", features):
        extra_key4, extra_key4_state = "NoPandoraConfirmation", True
        extra_keys = True
    else:
        extra_key4, extra_key4_state = None, None

    if get_hex_state("Duel", main):
        extra_key5, extra_key5_state = "NewCreatureBanks", True
        extra_keys = True
    else:
        extra_key5, extra_key5_state = None, None

    if get_hex_state("MKC_balance", features):
        extra_key8, extra_key8_state = "HeroLimit", 11
        extra_key9, extra_key9_state = "SeparateTPDD", False
        extra_key10, extra_key10_state = "CompleteSpellRedesign", False
        extra_keys = True
    else:
        extra_key8, extra_key8_state = None, None
        extra_key9, extra_key9_state = None, None
        extra_key10, extra_key10_state = None, None

    if extra_keys:        
        for key, key_state in [
                (extra_key, extra_key_state), 
                (extra_key2, extra_key2_state),
                (extra_key3, extra_key3_state),
                (extra_key4, extra_key4_state),
                (extra_key5, extra_key5_state),
                (extra_key8, extra_key8_state),
                (extra_key9, extra_key9_state),
                (extra_key10, extra_key10_state),
                ]:
            if key is not None:
                print(key, key_state)
                apply(key, key_state)
                #print("KEYS:", key, key_state)
                button_extra = BUTTONS_Gameplay_MAP.get(key)
                if button_extra is None:
                    button_extra = BUTTONS_Skins_Map.get(key)
                if button_extra is None:
                    button_extra = BUTTONS_PRESET_MAP.get(key)
                if button_extra is not None:
                    if button_extra['category_name'] is not None:
                        config.set(button_extra['category_name'], key, str(key_state))
                        button_extra['current_state'] = key_state

    with open(ini_path, 'w') as configfile:
        config.write(configfile)

    if complete:
        button_lists_list = [
                BUTTONS_Skins3,
                BUTTONS_Skins2,
                BUTTONS_Skins,
                BUTTONS_Gameplay,
                ]
    else:
        button_lists_list = [BUTTONS_Gameplay]

    for btn_list in button_lists_list:
        for b in btn_list:
            if b['arrow'] is True:
                continue
            name = b['name']
            if b['current_state'] is None:
                b['current_state'] = get_hex_state(name, b['category'])
            else:
                if b['category_name'] is not None:
                    config.set(b['category_name'], b['name'], str(b['current_state']))
                with open(ini_path, 'w') as configfile:
                    config.write(configfile)
            
            if Preset_On:
#                print("ON!!!!!!!!", Preset_On)
                state = get_preset_state(Preset_On, name)
                if state is not None:
                    confirm(name, state, depth=4)
                    preset_applied = True

            if preset_applied or (b['category'] not in [features, skins]):
                preset_applied = False
                continue

            confirm(name, b['current_state'], depth=depth)

    if get_hex_state("Duel", main):
        apply("Duel", True)
        confirm("MKC_balance", True)
        apply("MKC_compatibility", True)
    elif get_hex_state("MKC_balance", features):
        apply("MKC_balance", True)
        apply("MKC_compatibility", True)
    else:
        pass
#        if get_hex_state("MKC_scrolls", features):
#            apply("MKC_scrolls", True)
        confirm("Zenith", get_hex_state("Zenith", features), depth=4)
#        confirm("Catherine", get_hex_state("Catherine", features), depth=3)
#        confirm("NewCreatureSkills", get_hex_state("NewCreatureSkills", features), depth=3)
#        confirm("NewCreatureBanks", get_hex_state("NewCreatureBanks", features), depth=3)
    return
            

def get_pass():
    pass_base_number = 1073741824 #2^30
    PASScode = pass_base_number  
    if get_hex_state("Duel", main):
        PASSWORD = 'Duel 160'
        bytePASS = PASSWORD.encode('utf-8')
        return bytePASS
    elif get_hex_state("Basic", main):
        PASSWORD = 'Base 160'
    elif get_hex_state("Balanced", main) and get_hex_state("HeroLimit", features) == 8:
        PASSWORD = 'PP160 8h'
    elif get_hex_state("Balanced", main) and get_hex_state("HeroLimit", features) == 3:
        PASSWORD = 'PP160 3h'
    else:
        for i, g in enumerate(BUTTONS_Gameplay):
            if i > 9:
                i = i - 1
            
#        print(g['current_state'])
            if g['current_state'] is None:
                #print("found as none")
                g['current_state'] = get_hex_state(g['name'], g['category'])        
#        print(g['current_state'])


            if g['name'] == "HeroLimit":
                if int(g['current_state']) != 8:
                    PASScode = PASScode + 1
                elif int(g['current_state']) < 8:
                    PASScode = PASScode + 1 + 2 * pass_base_number
            elif g['name'] == "ExpandedLuckMoraleScale":
                PASScode = PASScode + int(g['current_state']) * 4 * pass_base_number
            elif g['name'] in ["NewMainMenu", "Arrow_left", "Arrow_right"]:
                pass
            elif g['current_state']:
                PASScode = PASScode + 2 ** i

        PASScode_bytes = PASScode.to_bytes((PASScode.bit_length() + 7) // 8 or 1, 'big')
        PASScode_b64 = base64.urlsafe_b64encode(PASScode_bytes).decode().rstrip('=')

        PASSWORD = str(PASScode_b64)
    while len(PASSWORD) < 8:
        PASSWORD += ' ' 
    bytePASS = PASSWORD.encode('utf-8')
    return bytePASS

def is_utf8_encodable(s: str) -> bool:
    try:
        s.encode('utf-8')
        return True
    except UnicodeEncodeError:
        return False
    
def update_templates():
    global script_dir

    bytePASS = get_pass()

    if not os.path.exists(os.path.join(script_dir, "HotA_RMGTemplates")):
        return
    templates, name_list = list_templates_and_names()
    for i, tmpl in enumerate(templates):
        tmpl_dir = os.path.join(script_dir, "HotA_RMGTemplates", tmpl)
        name = name_list[i]
        if str(name).lower() in ["jebus cross", "6lm10a", "memory lane 1.90", "memory lane", "default random map"]:
            name = str(name) + " - PP"

        if str(name).lower() in ["duel 3.0", "duel 3.0 t+", "duel 3.0a", "duel 3.0a t+", "duel 3.1", "duel 3.1 t+", "jebus cross - pp", "memory lane - pp", "default random map - pp", "6lm10a - pp"]:
            name = "{" + str(name) + "}"

        if is_utf8_encodable(name):
            bytename = name.encode('utf-8')
            tmpl_offset = find_hex(tmpl, bytename, tmpl_dir)

        if tmpl_offset == [] or tmpl_offset == [0]:
            continue
        
        if len(tmpl_offset) >= 1:
            offset = tmpl_offset[0] + len(name) + 2
            swaphex(tmpl, offset, bytePASS, tmpl_dir)
        else:
            print(name, "misses its own title")
    #print("templates patched") 

def update_button_image(btn_dict, suffix=""):
    name = btn_dict['name']
    state = str(btn_dict['current_state']).lower()
    if not btn_dict['arrow']:
        state_ini = str(get_hex_state(name, btn_dict['category'])).lower()
        if state != state_ini:
            state = state_ini
            btn_dict['current_state'] = state
    if btn_dict['category'] == features:
        if btn_dict['name'] in ['Zenith', 'Archibald', 'Gwenneth_gameplay', 'Winstan', 'Athe']:
            #print("file:", name, state)
            filename = f"{name}_{state}{suffix}.png"
        else: 
#            filename = f"{name}_{state}{suffix}.png"
            filename = f"{state}{suffix}.png"
    elif btn_dict['name'] in preset_list:
        if suffix != "":
            filename = f"{name}{suffix}.png"
        else:
            filename = f"{name}_{state}.png"            
        #print("button image name in preset list")
    elif btn_dict['category'] == main:
        filename = f"{name}{suffix}.png"
    else:
        filename = f"{name}_{state}{suffix}.png"
    image_path = os.path.join(icons_dir, filename)

    if not os.path.isfile(image_path):
        if suffix != "":
            return update_button_image(btn_dict, suffix="")
        else:
            btn_dict['button'].config(text=f"{name}{state}", image='', compound='none')
            return

    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)
    btn_dict['image'] = photo  #prevents garbage
    btn_dict['button'].config(image=photo, text="", compound="center")
    #print("shenanigans", image_path)
    return

    
bgRGB = "#724826"
bg2RGB = "#505050"
bg3RGB = "#f7de7b"


class HexSwapper:
    def __init__(self, root):
        global script_dir
        #creating the hexswapper app
        self.root = root
        self.root.title("HexSwapper")
        self.root.resizable(False, False)

        if getattr(sys, 'frozen', False):
            #Running as .exe (frozen by PyInstaller)
            icon_path = os.path.join(os.path.dirname(sys.executable), "pp_icon.png")
        else:
            #Running as .py script
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pp_icon.png")

#        apply("MKC_balance", False)
#        on_apply_preset("Basic")
#        messagebox.showinfo("x", "y")

        #icon image
        if os.path.exists(icon_path):
            img = ImageTk.PhotoImage(Image.open(icon_path))
            self.root.iconphoto(False, img)
        elif os.path.exists(os.path.join(script_dir, "pp_icon.png")):
            img = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "pp_icon.png")))
            self.root.iconphoto(False, img)
        else:
            pass

        #hexswapper image
        image1_path = os.path.join(icons_dir, "HexSwapper.png")
        image1 = Image.open(image1_path)
        self.bg_photo1 = ImageTk.PhotoImage(image1)
        self.canvas = tk.Canvas(root, width=self.bg_photo1.width(), height=self.bg_photo1.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.bg_photo1, anchor="nw")

        check_for_updates()
        #setting current states, based on category. This is the initial states based on INI. 
        for btn_list in [
                BUTTONS_Gameplay, 
                BUTTONS_Skins, 
                BUTTONS_Skins2, 
                BUTTONS_Skins3, 
                BUTTONS_PRESET,
                ]:
            for b in btn_list:
                name = b['name']
                if not b['arrow']:
                    b['current_state'] = get_hex_state(name, b['category'])
        update_ini()
                
        #print("PRESETON is", Preset_On)
        #checks swaps on startup. Deep. 
        global RESET, devmode
        RESET = False
        RESET = convert_value(main.get('RESET', fallback='False'))
        devmode = convert_value(main.get('DeveloperMode', fallback='False'))

        self.all_buttons = []
        self.menu_state = None        
        self.overlay_image_id = None  #Track canvas image ID for overlay
        self.init_menu_button()
        self.update_menu_state()
        self.tooltip_popup = None
        if not is_exe_open():
            self.dont_ranked()
            apply("LOD_FIX", True)
            print(get_hex_state("Duel", main))
            mkc_is_on_list = [[],[],[]] 
            mkc_is_on_list[0] = find_hex(EXE, b"movemmkc") 
            mkc_is_on_list[1] = find_hex(hota_dll, b"\x6A\x01\x6A\x1D\xFF\xD3\x84\xC0\x74\x10\x6A\x32\x6A\x01\x6A\xFF\x6A\x02\x6A\xFF") 
            mkc_is_on_list[2] = find_hex(DAT, b"{Dreadnoughts") 
            MKC_IS_ON = False
            for mkc_offset in mkc_is_on_list:
                if mkc_offset != [0]:
                    MKC_IS_ON = True
                    break
            if MKC_IS_ON:
                apply("MKC_TRUE", False, override=True, MKC = False)
            confirm("MKC_TRUE", get_hex_state("Duel", main), True, override = False, MKC_only = True)
            check_swaps(depth=4)
            update_templates()

    def show_description(self, event, btn_dict):
        desc = btn_dict.get('description')

        if self.tooltip_popup is not None:
            self.tooltip_popup.destroy()

        popup = tk.Toplevel(self.root)
        popup.wm_overrideredirect(True)  #Remove window decorations
        popup.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
    
        label = tk.Label(popup, text=desc, bg=bg3RGB, fg="black", relief="solid", borderwidth=1, font=("Sans Serif", 13))
        label.pack(ipadx=5, ipady=3)

        self.tooltip_popup = popup

    def hide_description(self, event=None):
        if self.tooltip_popup:
            self.tooltip_popup.destroy()
            self.tooltip_popup = None
    
    def cannot_swap_hex(self, preset_name, state):
        if not state:
            messagebox.showinfo("Cannot Swap Hex", f"You have enabled the {preset_name} preset, which forces this setting inactive.")
        else:
            messagebox.showinfo("Cannot Swap Hex", f"You have enabled the {preset_name} preset, which forces this setting to be always active.")
            return    

    def make_button_callback(self, btn_dict):
        def callback():
            #exe is open -> quit function
            if is_exe_open():
                messagebox.showwarning("Warning!", "The game is open! \n\nYou cannot use the HexSwapper to edit the game while it's open!\n\nIf you're getting this error despite having closed the game, please check the Task Manager or restart the system.")
                return

            global Preset_On
            #print("ON????", Preset_On)
            btn_name = btn_dict['name']
            btn_category = btn_dict['category']
            valid_states = get_valid_states(btn_name)
            current_state = btn_dict['current_state']
            norm_states = [str(s).strip().lower() for s in valid_states]
            norm_current = str(current_state).strip().lower()
            try:
                i = norm_states.index(norm_current)
                new_state = valid_states[(i + 1) % len(valid_states)]
            except ValueError:
                print("\n\n, VALUE ERROR\n\n")
                new_state = valid_states[0]

#here all the skips start. Incompatible options, options that need to be "skipped" and we apply the next one, 
            #skip if you want to turn off Pandora Confirmation, since MKC's scrolls has it always on; 
            if btn_name == "NoPandoraConfirmation" and not new_state and get_hex_state("MKC_scrolls", features):
                messagebox.showinfo("Cannot Swap Hex", 'You have enabled the "Control scrolls from day 1" setting, which forces this option to always be active.')
                return            
            elif btn_name == "NewCreatureBanks" and not new_state and get_hex_state("Duel", main):
                messagebox.showinfo("Cannot Swap Hex", 'You have enabled the "Duel 3.0 generation" setting, which forces this option to always be active.')
                return            
            elif str(btn_name).lower() == str(Preset_On).lower():
                if btn_name.lower() == "custom":
                    self.update_menu_state("Gameplay")
                return            
            elif (
                btn_name == "Catherine"
                and not new_state
                and (get_hex_state("Duel", main) or get_hex_state("MKC_balance", features))
                ):
#                messagebox.showinfo("Skipping option: 8-hero", 'You have enabled one of the enabled the "Skill rebalance for 1-hero" settings, which disable this skin.')
                try:
                    i = valid_states.index(current_state)
                    new_state = valid_states[(i + 2) % len(valid_states)]
                except ValueError:
                    new_state = valid_states[1]                
            elif (
                    new_state == 8 
                     and btn_name == "HeroLimit" 
                     and (get_hex_state("MKC_skills", features) or get_hex_state("Duel", main) or get_hex_state("MKC_balance", features))
                    
                ):
                messagebox.showinfo("Skipping option: 8-hero", 'You have enabled one of the 1 hero settings, which disable the 8-hero gameplay.')
                try:
                    i = valid_states.index(current_state)
                    new_state = valid_states[(i + 2) % len(valid_states)]
                except ValueError:
                    new_state = valid_states[1]
                        
#we check gameplay and preset buttons of whether they match the preset. 
#If preset on has "Priority" or its MKC preset, we block them; otherwise, the buttons ALSO turn off the preset. 
            extra_key, extra_key_state = None, None
            preset_dict = BUTTONS_PRESET_MAP.get(Preset_On)
            preset_dict2 = BUTTONS_Gameplay_MAP.get(Preset_On)

            if btn_dict['category'] != skins and Preset_On:
                preset = Preset_On
                state = get_preset_state(preset, btn_name)
                if state is not None:
                    if ( #case 1: "cant swap hex" popup. 
                        (preset in ["Duel", "MKC_balance"] or preset_dict['Priority']) 
                        and btn_name != "Duel" 
                        and not (str(state).lower() in ["extra", "antiextra"])
                        and not str(btn_name).lower() == str(preset).lower()
                            ):   
                        if preset == "Duel":
                            preset = "MKC's Duel 3.0"
                        if preset == "MKC_balance":
                            preset = "MKC's Gameplay Rebalance"                            
                        self.cannot_swap_hex(preset, state)
                        print("CASE ONE")
                        return
                    elif preset == "Duel" and btn_name == "Duel" and not new_state:
                        Preset_On = "MKC_balance"
                        apply(preset, False)                           
                        for button in [preset_dict, preset_dict2]:
                            if button is None:
                                continue
                            button['current_state'] = False
                            if button['category_name'] is not None:
                                config.set(button['category_name'], button['name'], str(False))
                        with open(ini_path, 'w') as configfile:
                            config.write(configfile)                                
                        on_apply_preset("MKC_balance")
                        extra_key, extra_key_state = "MKC_balance", True
                        print("CASE 1.5")
                    elif ( #case 5: set different preset. 
                        btn_name in preset_list 
                        and new_state
                        ):
                        Preset_On = btn_name
                        apply(preset, True)
                        for button in [preset_dict, preset_dict2]:
                            if button is None:
                                continue
                            button['current_state'] = True
                            if button['category_name'] is not None:
                                config.set(button['category_name'], button['name'], str(True))
                        with open(ini_path, 'w') as configfile:
                            config.write(configfile)
                        print("CASE FIVE")
                    elif ( #case 4: set preset. 
                        (btn_name in preset_list and not new_state and not (btn_name in ["Duel", "MKC_balance"]))
                        or 
                            (
                            not new_state and 
                                btn_name.lower() == str(Preset_On).lower()
                            )
                        ):
                        apply(preset, False)
                        for button in [preset_dict, preset_dict2]:
                            if button is None:
                                continue
                            button['current_state'] = False
                            if button['category_name'] is not None:
                                config.set(button['category_name'], button['name'], str(False))
                        with open(ini_path, 'w') as configfile:
                            config.write(configfile)
                        self.update_preset_custom()
                        print("CASE FOUR")
                    elif ( #case 2: disable preset. 
                        (btn_name in preset_list and new_state and (str(btn_name).lower() != str(preset).lower())) 
                        or (btn_name in preset_list and not new_state and not (btn_name in ["Duel", "MKC_balance"]))
                        or (not new_state and btn_name == preset)
                        ):
                        if not messagebox.askyesno(f"Do you want to disable preset {Preset_On}", 
                                               f"""Preset "{Preset_On}" is active. Do you want to disable it to edit the gameplay settings?"""):
                            return
                        apply(preset, False)
                        for button in [preset_dict, preset_dict2]:
                            if button is None:
                                continue
                            button['current_state'] = False
                            if button['category_name'] is not None:
                                config.set(button['category_name'], button['name'], str(False))
                        with open(ini_path, 'w') as configfile:
                            config.write(configfile)
                        self.update_preset_custom()
                        print("CASE TWO")
                    else: #exception handling
                        if Preset_On is not False:
                            if not messagebox.askyesno(f"Do you want to disable preset {Preset_On}", 
                                                   f"""Preset "{Preset_On}" is active. Do you want to disable it to edit the gameplay settings?"""):
                                return
                        apply(preset, False)
                        for button in [preset_dict, preset_dict2]:
                            if button is None:
                                continue
                            button['current_state'] = False
                            if button['category_name'] is not None:
                                config.set(button['category_name'], button['name'], str(False))
                        with open(ini_path, 'w') as configfile:
                            config.write(configfile)
                        self.update_preset_custom()
                        print("EXCEPTION HANDLING")
                            
            btn_dict['current_state'] = new_state

            #print("applying", btn_dict['name'], new_state)
            apply(btn_dict['name'], new_state)

            if (btn_name in preset_list) and new_state:
                #print("trying to apply preset", btn_name, "\n\n\n")
                print("applied preset!", btn_name)
                on_apply_preset(btn_name)
                #print("\n\n\nSUCCESSFULLY APPLIED PRESET: ", btn_name, "\n\n\n")
                self.update_menu_state(self.menu_state, refresh=True)                
                for preset in preset_list:
                    if (btn_name in preset_list):
                        if new_state and not (str(btn_name).lower() == str(preset).lower()) and not ( (btn_name == "MKC_balance" and preset == "Duel") or (btn_name == "Duel" and preset == "MKC_balance") ):
                            #print("DISABLED PRESET", preset, "SINCE", btn_name, "IS ACTIVE")
                            apply(preset, False)
                            preset_dict3 = BUTTONS_PRESET_MAP.get(Preset_On)
                            preset_dict4 = BUTTONS_Gameplay_MAP.get(Preset_On)
                            for button in [preset_dict3, preset_dict4]:
                                if button is None:
                                    continue
                                button['current_state'] = False
                                if button['category_name'] is not None:
                                    config.set(button['category_name'], button['name'], str(False))
                            with open(ini_path, 'w') as configfile:
                                config.write(configfile)

            elif (btn_name in preset_list) and not new_state:
                if btn_name == "Duel" and Preset_On == "Duel":
                    Preset_On = "MKC_balance"
                else:
                    apply(Preset_On, False)
                    Preset_On = "Custom"
                    for button in [preset_dict, preset_dict2]:
                        if button is None:
                            continue
                        button['current_state'] = False
                        if button['category_name'] is not None:
                            config.set(button['category_name'], button['name'], str(False))
                    with open(ini_path, 'w') as configfile:
                        config.write(configfile)
            elif btn_name == "Balanced":
                extra_key, extra_key_state = "HeroLimit", 8
            elif btn_name == "MKC_balance":
                extra_key, extra_key_state = "MKC_skills", new_state
            elif btn_name == "StaticSpellSpecialties":
                extra_key, extra_key_state = "StaticSpellSpecialties2", new_state
            elif btn_name == "MKC_scrolls" and new_state:
                extra_key, extra_key_state = "NoPandoraConfirmation", True
            elif btn_name == "MKC_duel" and new_state:
                extra_key, extra_key_state = "NewCreatureBanks", True
            elif btn_name in ["Duel", "MKC_skills", "MKC_balance"] and new_state:
                extra_key, extra_key_state = "HeroLimit", 11

            if extra_key is not None:
                confirm(extra_key, extra_key_state, depth=4)
                button_extra = BUTTONS_Gameplay_MAP.get(extra_key)
                if button_extra['category_name'] is not None:
                    config.set(button_extra['category_name'], extra_key, str(extra_key_state))
                button_extra['current_state'] = extra_key_state
                with open(ini_path, 'w') as configfile:
                    config.write(configfile)
                if not button_extra['button'] is None:
                    if button_extra['button'].winfo_exists():
                        update_button_image(button_extra)

            if btn_dict['category_name'] is not None:
                config.set(btn_dict['category_name'], btn_dict['name'], str(new_state))
            with open(ini_path, 'w') as configfile:
                config.write(configfile)

            if btn_category != skins:
                update_templates()
                
            if btn_dict['button'].winfo_exists():
                update_button_image(btn_dict)

            confirm(btn_dict['name'], new_state)            
        return callback
    
    def init_menu_button(self):
        #sets up buttons for home menu that are always present
        for i, btn in enumerate(BUTTONS_HexSwapperMenu):
            name = btn['name']

            if name.lower() in ["gameplay", "skins", "home", "halloffame", "halloffame_pressed"]:
                btn_widget = tk.Button(
                    self.root,
                    command=lambda name=name: self.update_menu_state(name),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, bd=0, takefocus=0, bg=bgRGB, activebackground=bgRGB
#                    fg="black",
                )                   
            elif name.lower() == "reset":
                btn_widget = tk.Button(
                    self.root, 
                    command = self.reset_all, 
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, bd=0, takefocus=0, bg=bgRGB, activebackground=bgRGB)
            elif name.lower() == "play": 
                btn_widget = tk.Button(
                    self.root, 
                    command = self.game, 
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, bd=0, takefocus=0, 
                    bg=bgRGB, activebackground=bgRGB)
            elif name.lower() in [
                    "discord", "youtube", "wiki", "wiki2", "coffee", "feedback", 
                    '-discord', '-youtube', '-wiki', '-wiki2', '-coffee', '-feedback',
                    'linktree']: 
                btn_widget = tk.Button(
                    self.root, 
                    command=lambda site=HEX[name]['link'][0]: self.open_website(site), 
                    borderwidth=0, relief="flat", overrelief="flat", 
                    highlightthickness=0, bd=0, takefocus=0, bg=bg2RGB, activebackground=bg2RGB)
            else:
                btn_widget = tk.Button(
                    self.root, 
                    command=self.make_button_callback(btn), 
                    borderwidth=0, relief="flat", overrelief="flat", 
                    highlightthickness=0, takefocus=0, bg=bgRGB, activebackground=bgRGB)

            btn['button'] = btn_widget
            if not btn['category'] in [features, skins]:
                btn_widget.bind("<Enter>", lambda e, b=btn: update_button_image(b, suffix="_hover"))
                btn_widget.bind("<Leave>", lambda e, b=btn: update_button_image(b))
                btn_widget.bind("<ButtonPress-1>", lambda e, b=btn: update_button_image(b, suffix="_press"))
                btn_widget.bind("<ButtonRelease-1>", lambda e, b=btn: update_button_image(b, suffix=""))
            btn_widget.bind("<ButtonPress-3>", lambda e, btn=btn: self.show_description(e, btn))
            btn_widget.bind("<ButtonRelease-3>", self.hide_description)
            if btn['category'] == skins:
                x, y = x_pos_list_skins[i], y_pos_list_skins[i]
            elif btn['category'] == features:
                x, y = x_pos_list_features[i], y_pos_list_features[i]
            else:
                x, y = btn['pos']
            btn_widget.place(x=x, y=y)
            update_button_image(btn)
            self.all_buttons.append(btn_widget)
         

    def open_website(self, site):
        link = 'https://' + site
        webbrowser.open(link)
    
    def update_preset_custom(self):
        global Preset_On 
        Preset_On = "Custom"
        preset_dict = BUTTONS_PRESET_MAP.get(Preset_On)
        if preset_dict is None:
            return
        preset_dict['current_state'] = False
        if preset_dict['category_name'] is not None:
            config.set(preset_dict['category_name'], preset_dict['name'], str(True))
        if preset_dict['button'].winfo_exists():
            update_button_image(preset_dict)
        with open(ini_path, 'w') as configfile:
            config.write(configfile)                                
        on_apply_preset("Custom")
#        if self.menu_state in ["Home", None]:
#            self.update_menu_state("Home", refresh = True)
        return

    def reset_all(self):
        if is_exe_open():
            messagebox.showwarning("Warning!", "The game is open! \n\nYou cannot use the HexSwapper to edit the game while it's open!\n\nIf you're getting this error despite having closed the game, please check the Task Manager or restart the system.")
            return
        global Preset_On
        Preset_On = "Basic"
        config.set("HexSwapper", "RESET", "True")
        if str(self.menu_state).lower() in ["gameplay", "gameplay2", "home", None, "reset"]:
            button_dictionaries = [
                BUTTONS_Gameplay, 
                BUTTONS_PRESET, 
                BUTTONS_Hidden,
                ]
        elif str(self.menu_state).lower() in ["skins", "skins2", "sknis3"]:
            button_dictionaries = [
                BUTTONS_Skins, 
                BUTTONS_Skins2, 
                BUTTONS_Skins3, 
                ]
        else:
            button_dictionaries = [
                BUTTONS_Gameplay, 
                BUTTONS_PRESET, 
                BUTTONS_Skins, 
                BUTTONS_Skins2, 
                BUTTONS_Skins3, 
                BUTTONS_Hidden,
                ]
        #print("RESETING DICTS:", button_dictionaries)
        for btn_list in button_dictionaries:
            for b in btn_list:
                name = b['name']
                valid_states = get_valid_states(name)
                default_state = valid_states[0]
                current_state = b['current_state']
                if current_state != default_state:
                    b['current_state'] = default_state               
                    #print("confirming", name)
                    apply(name, default_state)
                else:
                    confirm(name, default_state, depth=4)
                if b['category_name'] is not None:
                    config.set(b['category_name'], name, str(default_state))
                #print("reset", name, "to state", b['current_state'])

        self.update_menu_state("Home", refresh = True)
        confirm("StaticSpellSpecialties2", False, depth=4)
        on_apply_preset("Basic")
        update_ini()
        self.menu_state = None
        update_templates()
#        check_swaps()

    def flip_page(self, Forward=True):
        global page1, page2, page3, pageA, pageB
        if str(self.menu_state).lower() == page2:
            pageA = page1
            pageB = page3
        else:
            pageA = page2
            pageB = page2

        if Forward:
            requested_state = pageB
        else:
            requested_state = pageA        

        self.update_menu_state(requested_state)

    def switch_developer_mode(self):
        global devmode
        devmode = not devmode
        button = BUTTONS_PRESET_MAP.get("DeveloperMode")
        #print("SETTING DEVMODE TO", devmode)
        button['current_state'] = devmode
        config.set("HexSwapper", "DeveloperMode", str(devmode))
        with open(ini_path, "w") as f:
            config.write(f)
        update_button_image(button)
        self.update_menu_state("Home", refresh = True)

    def update_menu_state(self, requested_state="Home", refresh=True):
        if requested_state is None or requested_state is False or requested_state.lower() == "halloffame_pressed":
            requested_state = "Home"
        requested_state = requested_state.lower()
        if str(self.menu_state).lower() == requested_state and not refresh:
            return
        global page1, page2, page3, pageA, pageB
        if requested_state.lower() in ["skins", "skins2", "skins3"]:
            page1 = "skins"            
        else:
            page1 = "gameplay"
        page2 = page1 + '2'
        page3 = page1 + '3'
        
        self.menu_state = requested_state

        for btn in self.all_buttons[5:]:
            btn.destroy()
        self.all_buttons = self.all_buttons[:5]

        if self.overlay_image_id:
            self.canvas.delete(self.overlay_image_id)
            self.overlay_image_id = None

        menu_map = {
            "skins": BUTTONS_Skins,
            "skins2": BUTTONS_Skins2,
            "skins3": BUTTONS_Skins3,
            "gameplay": BUTTONS_Gameplay,
            "home": BUTTONS_HOME + BUTTONS_PRESET,
            "halloffame": BUTTONS_HOME2
        }

        try:
            buttons = menu_map.get(requested_state)
        except ValueError:
            buttons = BUTTONS_HOME + BUTTONS_PRESET
        color = bgRGB
        
        for i, btn in enumerate(buttons):
            name = btn['name']
            if btn['current_state'] == None and (btn['category'] != main or btn['name'] in preset_list):
                btn['current_state'] = get_hex_state(name, btn['category'])

            if name.lower() == "developermode":
                btn_widget = tk.Button(
                    self.root,
                    command=lambda: self.switch_developer_mode(),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, takefocus = 0,
                    bg=color,
                    activebackground=color
                    )                
            elif name.lower() == "arrow_right":
                btn_widget = tk.Button(
                    self.root,
                    command=lambda: self.flip_page(True),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, takefocus = 0,
                    bg=color,
                    activebackground=color
                    )                
            elif name.lower() == "arrow_left":
                btn_widget = tk.Button(
                    self.root,
                    command=lambda: self.flip_page(False),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, takefocus = 0,
                    bg=color,
                    activebackground=color
                    )
            elif name.lower() in ["halloffame", "halloffame_pressed"]:
                btn_widget = tk.Button(
                    self.root,
                    command=lambda name=name: self.update_menu_state(name),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, bd=0, takefocus=0, bg=bgRGB, activebackground=bgRGB
                    )
            elif name.lower() in [
                    "discord", "youtube", "wiki", "wiki2", "coffee", "feedback", 
                    '-discord', '-youtube', '-wiki', '-wiki2', '-coffee', '-feedback', 
                    "pumpkinrace2025", "popawasia", "keszu", "qweder", 'linktree']: 
                btn_widget = tk.Button(
                    self.root, 
                    command=lambda site=HEX[name]['link'][0]: self.open_website(site), 
                    borderwidth=0, relief="flat", overrelief="flat", 
                    highlightthickness=0, bd=0, takefocus=0, bg=bg2RGB, activebackground=bg2RGB)
            else: 
                btn_widget = tk.Button(
                    self.root,
                    command=self.make_button_callback(btn),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, takefocus = 0,
                    bg=color,
                    activebackground=color
                    )

            btn['button'] = btn_widget
            btn_widget.bind("<Enter>", lambda e, b=btn: update_button_image(b, suffix="_hover"))
            btn_widget.bind("<Leave>", lambda e, b=btn: update_button_image(b))
            btn_widget.bind("<ButtonPress-1>", lambda e, b=btn: update_button_image(b, suffix="_press"))
            btn_widget.bind("<ButtonRelease-1>", lambda e, b=btn: update_button_image(b, suffix=""))
            btn_widget.bind("<ButtonPress-3>", lambda e, btn=btn: self.show_description(e, btn))
            btn_widget.bind("<ButtonRelease-3>", self.hide_description)

            if btn['pos'] is None:                
                if btn['category'] == skins:
                    x, y = x_pos_list_skins[i], y_pos_list_skins[i]
                elif btn['category'] == features:
                    x, y = x_pos_list_features[i], y_pos_list_features[i]
            else:
                x, y = btn['pos']
            btn_widget.place(x=x, y=y)
            btn_widget.place(x=x, y=y)

            update_button_image(btn)
            self.all_buttons.append(btn_widget)

        if str(requested_state).lower() == "gameplay":
            overlay = os.path.join(icons_dir, "GameplayOverlay.png")
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(50, 140, image=self.bg_photo2, anchor="nw")
#            overlay2 = os.path.join(icons_dir, "Arrow_left_false.png")
#            image3 = Image.open(overlay2)
#            self.bg_photo3 = ImageTk.PhotoImage(image3)
#            self.overlay_image_id = self.canvas.create_image(230, 511, image=self.bg_photo3, anchor="nw")
        elif str(requested_state).lower() == "gameplay2":
            overlay = os.path.join(icons_dir, "GameplayOverlay2.png")
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(50, 140, image=self.bg_photo2, anchor="nw")
            overlay2 = os.path.join(icons_dir, "Arrow_right_false.png")
            image3 = Image.open(overlay2)
            self.bg_photo3 = ImageTk.PhotoImage(image3)
            self.overlay_image_id = self.canvas.create_image(310, 511, image=self.bg_photo3, anchor="nw")
        elif str(requested_state).lower() == "skins":
            overlay = os.path.join(icons_dir, "Arrow_left_false.png")
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(390, 511, image=self.bg_photo2, anchor="nw")
        elif str(requested_state).lower() == "skins3":
            overlay = os.path.join(icons_dir, "Arrow_right_false.png")
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(470, 511, image=self.bg_photo2, anchor="nw")
        elif str(requested_state).lower() == "skins2":
            pass
        elif str(requested_state).lower() == "halloffame":
            overlay = os.path.join(icons_dir, "Hall Of Fame.png")
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(50, 140, image=self.bg_photo2, anchor="nw")            
        elif (str(requested_state).lower() == "home" or requested_state is None):
#            if devmode:
            overlay = os.path.join(icons_dir, "Home Overlay.png")
#            else:
#               overlay = os.path.join(icons_dir, "Home Overlay2.png")                
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(50, 140, image=self.bg_photo2, anchor="nw")
            

    def dont_ranked(self):
        if is_exe_open():
            return
        text_offset = find_hex(hd_dll, original_text)[0]
        if text_offset == 0:
            text_offset = find_hex(hd_dll, original_text)[0]
        path = os.path.join(script_dir, hd_dll)
        if os.path.isfile(path):
            swaphex(hd_dll, text_offset, new_text)

    def game(self):
        #check_for_updates()
        global devmode
        RESET = get_hex_state("RESET", main)
        if not RESET and (Preset_On in [False, "Custom", "MKC_balance"]) and not devmode:
            #rand = random.randint(1,2)
            #if rand == 1:
            if messagebox.askyesno("Warning", """To play online multiplayer, both players must have the same settings. 
                                       \nConfirm with your friends that you have the same settings. 
                                       \n\nDo you want to go back to HexSwapper?"""):
                self.update_menu_state("gameplay")
                return
            #elif rand == 2:
                #if not messagebox.askyesno("Warning", """To play online multiplayer, both players must have the same settings. 
                #                           \nConfirm with your friends that you have the same settings. 
                #                           \n\nDo you want to proceed to the game?"""):
                #    self.update_menu_state("gameplay")
                #    return
        if Preset_On != "Duel":
            check_swaps(depth=4)
        update_templates()
#        print(Preset_On)
        if getattr(sys, 'frozen', False):
            #Running as .exe (frozen by PyInstaller)
            game_dir = os.path.dirname(sys.executable)
        else:
            #Running as .py script
            game_dir = os.path.dirname(os.path.abspath(__file__))
        
        if Preset_On == "Duel":
            game_exe = os.path.join(game_dir, EXE_DUEL)
        else:
            game_exe = os.path.join(game_dir, EXE)
        if not os.path.exists(game_exe):
            messagebox.showerror("Error", f"Game executable not found at: {game_exe}")
            return

        system_exit = True
        for i in range(3):
            try:
                subprocess.Popen([game_exe], cwd=game_dir)
                self.root.destroy()
                sys.exit()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch game: {e}")
                system_exit = False
        if system_exit:
            self.root.destroy()
            sys.exit()

#Run
if __name__ == "__main__":
    root = tk.Tk()
    app = HexSwapper(root)
    root.mainloop()






