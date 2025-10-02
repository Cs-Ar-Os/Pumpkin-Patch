# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 19:15:13 2025

@author: Csaros
"""

import configparser, zipfile, shutil, psutil, logging, time, sys, subprocess, os, webbrowser, datetime

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

import requests


# Get the folder where the EXE or script is actually running from
if getattr(sys, 'frozen', False):
    # Running as .exe (frozen by PyInstaller)
    script_dir = os.path.dirname(sys.executable)
else:
    # Running as .py script
    script_dir = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    # Running as .exe (frozen by PyInstaller)
    icons_dir = sys._MEIPASS
else:
    # Running as .py script
    icons_dir = os.path.dirname(os.path.abspath(__file__))

icons_dir = os.path.join(icons_dir, "Icons")

ini_path = os.path.join(script_dir, 'PP.ini')


#File definitions
EXE = "h3hota HD.exe"
DAT = "HotA.dat"
MPD = "h3hota_maped.exe"
hd_dll = "HD_HOTA.dll"
hota_dll = "HotA.dll"

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
    except:
        return

    if remote_date > local_date:
        messagebox.showinfo("New version detected", ("Update available! Please visit the wiki and download the new version of the mod. \n\nMod last updated: " + local_date + "New version uploaded: " + remote_date))
        return

    return


def swaphex(file, offset, bytes, filepath = None):
    if filepath == None:
        global script_dir
        path = os.path.join(script_dir, file)
    else:
        path = filepath

    if offset == 0:
        logging.info("While editing", path, "offset was stated as ", offset, "\nMost likely source is an error when performing the find_hex function.")
        return

    if not os.path.isfile(path):
        error_message = "File not found: " + path
        messagebox.showinfo("File not found", error_message)
        return
    for _ in range(3):
        try:
            with open(path, "r+b") as f:
                f.seek(offset)
                f.write(bytes)
                f.flush()
                f.seek(offset)
                written = f.read(len(bytes))
                if written != bytes:
                    raise IOError("Verification failed")
            print(file, "patched at", offset) 
            return
        except PermissionError:
            time.sleep(0.5)
        except IOError as e:
            messagebox.showinfo("IOError while verifying %s: %s", e)

    messagebox.showinfo("Failed to patch %s at offset 0x%X", path, offset)
    messagebox.showinfo("Expected bytes: %s, got: %s", bytes, written)


def find_hex(file, hex_to_find, filepath = None, default_0 = False):
    offsets = []
    if filepath == None:
        global script_dir
        path = os.path.join(script_dir, file)
    else:
        path = filepath
    if not os.path.isfile(path):
        logging.error("File not found: %s", path)
#        raise FileNotFoundError(path)
        offsets = [0]
        return offsets
    with open(path, 'rb') as f:
        data = f.read()
        index = data.find(hex_to_find)
        while index != -1:
            offsets.append(index)
            index = data.find(hex_to_find, index + 1)
    if default_0 and not offsets:
        offsets = [0]
    return offsets


def move_file(state, skinname):
    # Determine script directory (whether running as script or executable)
    global script_dir 
    
    # Paths
    zip_path = os.path.join(script_dir, f"{state}.zip")
    target_dir = os.path.join(script_dir, "Data")
    target_path = os.path.join(target_dir, skinname)

    # Ensure the Data directory exists
    os.makedirs(target_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if skinname in zip_ref.namelist():
                with zip_ref.open(skinname) as source_file, open(target_path, 'wb') as dest_file:
                    shutil.copyfileobj(source_file, dest_file)
                #logging.info(f"Copied {skinname} from {state}.zip to Data/")
            else:
                logging.warning(f"{skinname} not found in {zip_path}")
    except FileNotFoundError:
        logging.error(f"Zip file not found: {zip_path}")
    except Exception as e:
        logging.error(f"Error copying {skinname} from {zip_path}: {e}")

def delete_file(filename):
    """Delete a file from the Data folder inside script_dir."""
    global script_dir
    target_dir = os.path.join(script_dir, "Data")
    target_path = os.path.join(target_dir, filename)

    try:
        if os.path.isfile(target_path):
            os.remove(target_path)
            logging.info(f"Deleted {filename} from Data/")
        else:
            logging.warning(f"File not found: {target_path}")
    except Exception as e:
        logging.error(f"Error deleting {filename}: {e}")

HEX = {
    "Home": {
        True: [],
    },
    "MenuSkins": {
        True: [],
    },
    "MenuGameplay": {
        True: [],
    },
    "Reset": {
        False: [],
    },
     "Play": {
        "HOTA" : [],
    },
    "LinkTree": {
        'link': ['linktr.ee/cs.ar.os'],
    },
    "Coffee": {
        'link': ['buymeacoffee.com/csaros'],
    },
    "Wiki2": {
        'link': ['heroes.thelazy.net/index.php/User:Csaros/Mod_-_Changelog'],
    },
    "Wiki": {
        'link': ['heroes.thelazy.net/index.php/User:Csaros/Pumpkin_Patch'],
    },
    "Discord": {
        'link': ['discord.com/invite/VVN5vreEaN'],
    },
    "Youtube": {
        'link': ['youtube.com/@csaros'],
    },
    "Feedback": {
        'link': ['forms.gle/Kbsct2o3iBL5wzbP6'],
    },
    "-Coffee": {
        'link': ['buymeacoffee.com/csaros'],
    },
    "-Wiki": {
        'link': ['heroes.thelazy.net/index.php/User:Csaros/Pumpkin_Patch'],
    },
    "-Discord": {
        'link': ['discord.com/invite/VVN5vreEaN'],
    },
    "-Youtube": {
        'link': ['youtube.com/@csaros'],
    },
    "-Feedback": {
        'link': ['forms.gle/Kbsct2o3iBL5wzbP6'],
    },
     "Arrow_right": {
        "true" : [],
    },
     "Arrow_left": {
        "true" : [],
    },
    "Zenith": {
        True: [
            (EXE, 0x27B4D0, b"\x01\x00\x00\x00\x08\x00\x00\x00\x09\x00\x00\x00\x0C\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x2A\x00\x00\x00\x8D\x00\x00\x00\x8D\x00\x00\x00\x8D\x00\x00\x00"),
            (EXE, 0x278E20, b"\x06\x00\x00\x00\x3A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3B\x00\x00\x00\x8D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (EXE, 0x27e93a, b"\x50\x50"),
            (EXE, 0x27e94a, b"\x50\x50"),
            (MPD, 0x187F00, b"\x01\x00\x00\x00\x08\x00\x00\x00\x09\x00\x00\x00\x0C\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x2A\x00\x00\x00\x38\x00\x00\x00\x3A\x00\x00\x00\x3C\x00\x00\x00"),
            (EXE, 0x27F15B, b"\x50"),
            (EXE, 0x28873F, b"\x50"),
            (EXE, 0x279cd3, b"\x50"),               
            (EXE, 0x2817DF, b"\x50"),         
            (EXE, 0x279D93, b"\x50"),         
            (hd_dll, find_hex(hd_dll, b"\x4E\x33\x32\x2E\x64\x65\x66", default_0=True)[0], b"\x4E\x33\x50\x2E\x64\x65\x66"),
            (hd_dll, find_hex(hd_dll, b"\x4E\x34\x34\x2E\x64\x65\x66", default_0=True)[0], b"\x4E\x34\x50\x2E\x64\x65\x66"),
            (hd_dll, find_hex(hd_dll, b"\x6E\x33\x32\x2E\x64\x65\x66", default_0=True)[0], b"\x6E\x33\x50\x2E\x64\x65\x66"),
            (hd_dll, find_hex(hd_dll, b"\x6E\x34\x34\x2E\x64\x65\x66", default_0=True)[0], b"\x6E\x34\x50\x2E\x64\x65\x66"),
        ],
        False: [
            (EXE, 0x27B4D0, b"\x00\x00\x00\x00\x07\x00\x00\x00\x08\x00\x00\x00\x0C\x00\x00\x00\x01\x00\x00\x00\x1A\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x35\x00\x00\x00\x3A\x00\x00\x00\x3A\x00\x00\x00\x3A\x00\x00\x00"),
            (EXE, 0x278E20, b"\x01\x00\x00\x00\x3A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (EXE, 0x27e93a, b"\x44\x6B"),
            (EXE, 0x27e94a, b"\x44\x6B"),
            (MPD, 0x187F00, b"\x00\x00\x00\x00\x07\x00\x00\x00\x08\x00\x00\x00\x0C\x00\x00\x00\x01\x00\x00\x00\x1A\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x35\x00\x00\x00\x3A\x00\x00\x00\x3A\x00\x00\x00\x3A\x00\x00\x00"),
            (EXE, 0x27F15B, b"\x73"),
            (EXE, 0x28873F, b"\x73"),
            (EXE, 0x279cd3, b"\x63"),         
            (EXE, 0x2817DF, b"\x32"),         
            (EXE, 0x279D93, b"\x34"),         
            (hd_dll, find_hex(hd_dll, b"\x4E\x33\x50\x2E\x64\x65\x66", default_0=True)[0], b"\x4E\x33\x33\x2E\x64\x65\x66"),
            (hd_dll, find_hex(hd_dll, b"\x4E\x34\x50\x2E\x64\x65\x66", default_0=True)[0], b"\x4E\x34\x34\x2E\x64\x65\x66"),
            (hd_dll, find_hex(hd_dll, b"\x6E\x33\x50\x2E\x64\x65\x66", default_0=True)[0], b"\x6E\x33\x33\x2E\x64\x65\x66"),
            (hd_dll, find_hex(hd_dll, b"\x6E\x34\x50\x2E\x64\x65\x66", default_0=True)[0], b"\x6E\x34\x34\x2E\x64\x65\x66"),
        ],
    },
    "Archibald": {
        True: [
            (EXE, 0x27D44C, b"\x01\x01\x00\x00"),
            (EXE, 0x27BEBC, b"\x01\x01\x01\x00"),
        ],
        False: [
            (EXE, 0x27D44C, b"\x01\x01\x01\x00"),
            (EXE, 0x27BEBC, b"\x01\x01\x00\x00"),
        ],
    },
    "Gwenneth_gameplay": {
        True: [
            (EXE, 0x27D280, b"\x01\x01\x00\x00"),
            (EXE, 0x27A2B4, b"\x01\x01\x01\x00"),
        ],
        False: [
            (EXE, 0x27D280, b"\x01\x01\x01\x00"),
            (EXE, 0x27A2B4, b"\x01\x01\x00\x00"),
        ],
    },
    "Athe": {
        True: [
            (EXE, 0x27D3F0, b"\x01\x01\x00\x00"),
            (EXE, 0x27B33C, b"\x01\x01\x01\x00"),
        ],
        False: [
            (EXE, 0x27D3F0, b"\x01\x01\x01\x00"),
            (EXE, 0x27B33C, b"\x01\x01\x00\x00"),
        ],
    },
    "Winstan": {
        True: [
            (EXE, 0x27A9E4, b"\x01\x01\x00\x00"),
            (EXE, 0x27D560, b"\x01\x01\x01\x00"),
        ],
        False: [
            (EXE, 0x27A9E4, b"\x01\x01\x01\x00"),
            (EXE, 0x27D560, b"\x01\x01\x00\x00"),
        ],
    },
    "RefuseLevelUp": {
        True: [(EXE, 0x0F9BA4, b"\xEb")],
        False: [(EXE, 0x0F9BA4, b"\x74")],
    },
    "XPcalc": {
        True: [
            (EXE, 0x069F8A, b"\x50\x52\x8B\x3D\xB0\x47\x67\x00\x6B\xF6\x1D\x8B\x44\xB7\x40\x0F\xAF\xC1\x6A\x0C\x59\x31\xD2\xF7\xF9\x01\xC3\x5A\x58\x8B\x4D\xFC\x05\x48\x05\x00\x00\x49\x89\x4D\xFC\x75\xAF\x8B\x45\xF8\x8B\x88\xC8\x53\x00\x00\x85\xC9\x74\x0E\x8B\x4D\x08\x85\xC9\x75\x07\x8B\xCB\xC1\xE9\x03\x01\xCB\x8B\x8C\x90\xCC\x53\x00\x00\x85\xC9\x74\x07\x8B\xCB\xC1\xE9\x03\x01\xCB\x89\x5D\xFC\xEB\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (EXE, 0x069F6B, b"\x3b"),
            (EXE, 0x069F77, b"\x2F"),
            (EXE, 0x069F81, b"\x25"),
        ],
        False: [
            (EXE, 0x069F8A, b"\x8D\x3C\xF5\x00\x00\x00\x00\x2B\xFE\x8D\x34\xBE\x8B\x3D\xB0\x47\x67\x00\x0F\xAF\x4C\xB7\x4C\x03\xD9\x8B\x4D\xFC\x05\x48\x05\x00\x00\x49\x89\x4D\xFC\x75\xB3\x8B\x45\xF8\x8B\x8C\x90\xCC\x53\x00\x00\x85\xC9\x74\x06\x81\xC3\xF4\x01\x00\x00\x8A\x0D\xF3\x85\x69\x00\x89\x5D\xFC\x84\xC9\x75\x0A\x8A\x0D\x94\x77\x69\x00\x84\xC9\x74\x09\x81\xC3\x0C\xFE\xFF\xFF\x89\x5D\xFC\x8B\x88\xC8\x53\x00\x00\x85\xC9\x74\x10\x8B\x4D\x08\x85\xC9\x75\x09\x81\xC3\xF4\x01\x00\x00\x89\x5D\xFC"),
            (EXE, 0x069F6B, b"\x37"),
            (EXE, 0x069F77, b"\x2b"),
            (EXE, 0x069F81, b"\x21"),        
            ],
    },
    "MaximumLuck4": {
        True: [
            (EXE, 0x03F658, b"\x04"),
            (EXE, 0x03F65F, b"\x04"),
            (EXE, 0x04153A, b"\x04"),
            (EXE, 0x041541, b"\x04"),
            (EXE, 0xCCEF5, b"\x04"),
            (EXE, 0xCCEF9, b"\x04"),            
        ],
        False: [
            (EXE, 0x03F658, b"\x03"),
            (EXE, 0x03F65F, b"\x03"),
            (EXE, 0x04153A, b"\x03"),
            (EXE, 0x041541, b"\x03"),
            (EXE, 0xCCEF5, b"\x03"),
            (EXE, 0xCCEF9, b"\x03"),            
        ],
    },
    "CompleteSpellRedesign": {
        False: [
            (EXE, 0x450E5, b'\x01'),
            (EXE, 0x4463B, b'\xE9\x00\x8B\x08\x00\x90'),
            (EXE, 0x28900A, b'\x6E\x67'),
            (EXE, 0x288362, b'\x74\x73'),
            (EXE, 0x288360, b"\x61\x69\x74\x73"),
            (EXE, 0x26020C, b"\x6C\x73"),
            (EXE, 0x28C35E, b"\x63\x72"),
            (EXE, 0x01D51F, b"\xF4\x01"),
            (EXE, 0x01D534, b"\x90\x01"),
            (EXE, 0x01D41F, b"\x90\x01"),            
            (EXE, 0x242224, b"\x06\x00\x00\x00\x06\x00\x00\x00\x07\x00\x00\x00\x08\x00\x00\x00\x06\x00\x00\x00\x06\x00\x00\x00\x07\x00\x00\x00\x08\x00\x00\x00")
        ],
        True: [
            (EXE, 0x450E5, b'\x02'),
            (EXE, 0x4463B, b'\x8B\x15\x20\x94\x69\x00'),
            (EXE, 0x28900A, b'\x50\x50'),
            (EXE, 0x288362, b'\x50\x50'),
            (EXE, 0x288360, b"\x61\x69\x50\x50"),
            (EXE, 0x26020C, b"\x50\x50"),
            (EXE, 0x28C35E, b"\x50\x50"),
            (EXE, 0x01D51F, b"\x2C\x01"),
            (EXE, 0x01D534, b"\xC8\x00"),
            (EXE, 0x01D41F, b"\xC8\x00"),
            (EXE, 0x242224, b"\x06\x00\x00\x00\x06\x00\x00\x00\x08\x00\x00\x00\x0A\x00\x00\x00\x06\x00\x00\x00\x06\x00\x00\x00\x07\x00\x00\x00\x08\x00\x00\x00")
        ],
    },
    "1hero": {
        False: [
            (EXE, 0x260518, b"\x02\x00\x00\x00\x03\x00\x00\x00\x05\x00\x00\x00\x07\x00\x00\x00\x07"),
            (EXE, 0x23E9D8, b"\x07"), 
            (EXE, 0x23E9DC, b"\x08"), 
            (hota_dll, 0x19A0E4, b"\x08"),  
            (hota_dll, 0x19A0EE, b"\x0A"),  
            (hota_dll, 0x19A0F8, b"\x0C"), 
#view air
            (EXE, 0x1FC3A6, b"\x02"),
            (EXE, 0x1FC3AA, b"\x74"),
            ],
        True: [
            (EXE, 0x260518, b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (EXE, 0x23E9D8, b"\x05"),
            (EXE, 0x23E9DC, b"\x06"), 
            (hota_dll, 0x19A0E4, b"\x06"), 
            (hota_dll, 0x19A0EE, b"\x08"), 
            (hota_dll, 0x19A0F8, b"\x0A"), 
#view air
            (EXE, 0x1FC3A6, b"\x01"),
            (EXE, 0x1FC3AA, b"\x7D"),
            ],
    },
    "UnpredictableGenies": {
        False: [
            (EXE, 0x047BF1, b"\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x55\x8B\xEC\x51\x8B\x45\x08\x53\x56\x57\x85\xC0\x0F\x8C\xDD\x00\x00\x00\x3D\xBB\x00\x00\x00\x0F\x8D\xD2\x00\x00\x00\x8B\x15\x20\x94\x69\x00\x8D\x0C\xC5\x00\x00\x00\x00\x2B\xC8\xC1\xE1\x04\x8D\x8C\x11\xC4\x01\x00\x00\xE8"),
            (EXE, 0x048464, b"\x51\x83"),
        ],
        True: [
            (EXE, 0x047BF1, b"\x31\xC9\x6A\x17\x5A\xE8\xC5\x4B\x0C\x00\x8A\x80\x1E\x7C\x44\x00\x8B\x55\x08\x8B\x0D\x20\x94\x69\x00\x6A\x06\x6A\x02\x6A\xFF\x6A\x01\x52\x50\xE8\x27\x85\x15\x00\xE9\xBF\x07\x00\x00\x1B\x1C\x1D\x1E\x1F\x20\x21\x24\x29\x2B\x2C\x2E\x30\x31\x33\x35\x37\x38\x3A\x25\x22\x41\x26\x12\x00"),
            (EXE, 0x048464, b"\xF1\x7b"),
        ],
    },
    "BalancedOldHillFort": {
        True: [
            (EXE, 0x23EB4C, b'\x00\x00\x80\x3F\x00\x00\xA0\x3F\x00\x00\xC0\x3F\x00\x00\x00\x40\x00\x00\x20\x40\x00\x00\x40\x40\x00\x00\x80\x40'),
            (EXE, 0xE8095, b"\xEB"),
#text stuff
            (EXE, 0x26028A, b"\x66"),
        ],
        False: [
            (EXE, 0x23EB4C, b'\x00\x00\x00\x00\x00\x00\x80\x3E\x00\x00\x00\x3F\x00\x00\x40\x3F\x00\x00\x80\x3F\x00\x00\x80\x3F\x00\x00\x80\x3F'),
            (EXE, 0xE8095, b"\x75"),
            (EXE, 0x26028A, b"\x6F"),
        ],
    },
    "FlyingFamiliars": {
        False: [
            (EXE, 0x27551A, b'\x74'),
            (EXE, 0x271744, b'\x10'),
        ],
        True: [
            (EXE, 0x27551A, b'\x50'),
            (EXE, 0x271744, b'\x12'),
        ],
    },
    "RegeneratingChaosHydra": {
        False: [
            (EXE, 0x27551B, b'\x73'),
            (EXE, 0x046C35, b"\x32"),
            (EXE, 0x046C2F, b"\x32"),
            (EXE, 0x04AC5B, b"\x3C"),
        ],
        True: [
            (EXE, 0x27551B, b'\x50'),
            (EXE, 0x046C35, b"\x19"),
            (EXE, 0x046C2F, b"\x19"),
            (EXE, 0x04AC5B, b"\x6F"),
        ],
    },
    "DoubleGrowth": {
        False: [
            (EXE, 0xC8892, b'\x1F'),
        ],
        True: [
            (EXE, 0xC8892, b'\x1E'),
        ],
    },
    "PandoraPumpkin": {
        True: [
            ("file", "AVA0128.def"),
            ("file", "AVA0128.msk"),
        ],
        False: [
            ("delete", "AVA0128.def"),
            ("delete", "AVA0128.msk"),
        ],
    },
    "PrimaryStatsIncreaseIsConstant": {
        False: [
            (EXE, 0x18BB9A, b'\x74\x73'),
        ],
        True: [
            (EXE, 0x18BB9A, b'\x50\x50'),
        ],
    },
    "CatherineReplacesSorsha": {
        True: [
            (EXE, 0x27F09A, b"\x50\x50"),
            (EXE, 0x27F0AA, b"\x50\x50"),
            (EXE, 0x28873E, b"\x50\x50"),
            (EXE, 0x27F15A, b"\x50"),
        ],
        "fanart": [
            (EXE, 0x27F09A, b"\x4B\x50"),
            (EXE, 0x27F0AA, b"\x4B\x50"),
            (EXE, 0x28873E, b"\x50"),
            (EXE, 0x27F15A, b"\x50"),
        ],
        "bg": [
            (EXE, 0x27F09A, b"\x42\x47"),
            (EXE, 0x27F0AA, b"\x42\x47"),
            (EXE, 0x28873E, b"\x50"),
            (EXE, 0x27F15A, b"\x50"),
        ],
        "legacy": [
            (EXE, 0x27F09A, b"\x50\x32"),
            (EXE, 0x27F0AA, b"\x50\x32"),
            (EXE, 0x28873E, b"\x50"),
            (EXE, 0x27F15A, b"\x50"),
        ],
        False: [
            (EXE, 0x27F09A, b"\x4B\x6E"),
            (EXE, 0x27F0AA, b"\x4B\x6E"),
            (EXE, 0x28873E, b"\x6F"),
            (EXE, 0x27F15A, b"\x74"),
        ],
    },
    "Sandro": {
        "default": [
            (EXE, 0x27E80A, b"\x4E\x63"),
            (EXE, 0x27E7FA, b"\x4E\x63"),
        ],
        "bg": [
            (EXE, 0x27E80A, b"\x42\x47"),
            (EXE, 0x27E7FA, b"\x42\x47"),
        ],
        "campaign": [
            (EXE, 0x27E80A, b"\x57\x7A"),
            (EXE, 0x27E7FA, b"\x57\x7A"),
        ],
        "ashan": [
            (EXE, 0x27E80A, b"\x48\x4E"),
            (EXE, 0x27E7FA, b"\x48\x4E"),
        ],
        "wow": [
            (EXE, 0x27E80A, b"\x57\x57"),
            (EXE, 0x27E7FA, b"\x57\x57"),
        ],
        "fanart": [
            (EXE, 0x27E80A, b"\x4E\x50"),
            (EXE, 0x27E7FA, b"\x4E\x50"),
        ],
        "legacy": [
            (EXE, 0x27E80A, b"\x50\x50"),
            (EXE, 0x27E7FA, b"\x50\x50"),
        ],
    },
    "Luna": {
        "default": [
            (EXE, 0x27E03A, b"\x65\x6C"),
            (EXE, 0x27E04A, b"\x65\x6C"),
        ],
        "aphra": [
            (EXE, 0x27E03A, b"\x50\x50"),
            (EXE, 0x27E04A, b"\x50\x50"),
        ],
        "legacy": [
            (EXE, 0x27E03A, b"\x4C\x47"),
            (EXE, 0x27E04A, b"\x4C\x47"),
        ],
    },
    "Gwenneth": {
        "default": [
            (EXE, 0x27DEFA, b"\x51\x63"),
            (EXE, 0x27DF0A, b"\x51\x63"),
        ],
        "legacy": [
            (EXE, 0x27DEFA, b"\x50\x50"),
            (EXE, 0x27DF0A, b"\x50\x50"),
        ],
    },
    "LordHaart": {
        "default": [
            (EXE, 0x27F0BA, b"\x4B\x6E"),
            (EXE, 0x27F0CA, b"\x4B\x6E"),
        ],
        "bg": [
            (EXE, 0x27F0BA, b"\x42\x47"),
            (EXE, 0x27F0CA, b"\x42\x47"),
        ],
        "legacy": [
            (EXE, 0x27F0BA, b"\x50\x50"),
            (EXE, 0x27F0CA, b"\x50\x50"),
        ],
        "ashan": [
            (EXE, 0x27F0BA, b"\x48\x4E"),
            (EXE, 0x27F0CA, b"\x48\x4E"),
        ],

        "lich": [
            (EXE, 0x27F0BA, b"\x44\x6B"),
            (EXE, 0x27F0CA, b"\x44\x6B"),
        ],
        "lich_bg": [
            (EXE, 0x27F0BA, b"\x44\x50"),
            (EXE, 0x27F0CA, b"\x44\x50"),
        ],
    },
    "Roland": {
        "default": [
            (EXE, 0x27DE3A, b"\x53\x68"),
            (EXE, 0x27DE4A, b"\x53\x68"),
        ],
        "legacy": [
            (EXE, 0x27DE3A, b"\x50\x50"),
            (EXE, 0x27DE4A, b"\x50\x50"),
        ],
    },
    "Mutare": {
        "default": [
            (EXE, 0x27DE1A, b"\x53\x68"),
            (EXE, 0x27DE2A, b"\x53\x68"),
        ],
        "human": [
            (EXE, 0x27DE1A, b"\x41\x42"),
            (EXE, 0x27DE2A, b"\x41\x42"),
        ],
        "bg": [
            (EXE, 0x27DE1A, b"\x53\x50"),
            (EXE, 0x27DE2A, b"\x53\x50"),
        ],
    },
    "Gem": {
        "default": [
            (EXE, 0x27EDDA, b"\x44\x72"),
            (EXE, 0x27EDEA, b"\x44\x72"),
        ],
        "bg": [
            (EXE, 0x27EDDA, b"\x42\x47"),
            (EXE, 0x27EDEA, b"\x42\x47"),
        ],
        "campaign": [
            (EXE, 0x27EDDA, b"\x4C\x47"),
            (EXE, 0x27EDEA, b"\x4C\x47"),
        ],
        "ashan": [
            (EXE, 0x27EDDA, b"\x48\x4E"),
            (EXE, 0x27EDEA, b"\x48\x4E"),
        ],
        "legacy": [
            (EXE, 0x27EDDA, b"\x50\x50"),
            (EXE, 0x27EDEA, b"\x50\x50"),
        ],
    },  
    "Halon": {
        "default": [
            (EXE, 0x27EC1A, b"\x57\x7A"),
            (EXE, 0x27EC2A, b"\x57\x7A"),
        ],
        "legacy": [
            (EXE, 0x27EC1A, b"\x50\x50"),
            (EXE, 0x27EC2A, b"\x50\x50"),
        ],
    },
    "Theodorus": {
        "default": [
            (EXE, 0x27EBBA, b"\x57\x7A"),
            (EXE, 0x27EBCA, b"\x57\x7A"),
        ],
        "ashan": [
            (EXE, 0x27EBBA, b"\x48\x4E"),
            (EXE, 0x27EBCA, b"\x48\x4E"),
        ],
    },
    "Alamar": {
        "default": [
            (EXE, 0x27E63A, b"\x57\x6C"),
            (EXE, 0x27E64A, b"\x57\x6C"),
        ],
        "bg": [
            (EXE, 0x27E63A, b"\x42\x47"),
            (EXE, 0x27E64A, b"\x42\x47"),
        ],
        "legacy": [
            (EXE, 0x27E63A, b"\x50\x50"),
            (EXE, 0x27E64A, b"\x50\x50"),
        ],
    },
    "Yog": {
        "default": [
            (EXE, 0x27E53A, b"\x42\x72"),
            (EXE, 0x27E54A, b"\x42\x72"),
        ],
        "campaign": [
            (EXE, 0x27E53A, b"\x4C\x47"),
            (EXE, 0x27E54A, b"\x4C\x47"),
        ],
        "ashan": [
            (EXE, 0x27E53A, b"\x48\x4E"),
            (EXE, 0x27E54A, b"\x48\x4E"),
        ],
        "legacy": [
            (EXE, 0x27E53A, b"\x50\x50"),
            (EXE, 0x27E54A, b"\x50\x50"),
        ],
        "bg": [
            (EXE, 0x27E53A, b"\x42\x47"),
            (EXE, 0x27E54A, b"\x42\x47"),
        ],
    },
    "CragHack": {
        "default": [
            (EXE, 0x27E47A, b"\x42\x72"),
            (EXE, 0x27E48A, b"\x42\x72"),
        ],
        "bg": [
            (EXE, 0x27E47A, b"\x42\x47"),
            (EXE, 0x27E48A, b"\x42\x47"),
        ],
        "ashan": [
            (EXE, 0x27E47A, b"\x48\x4E"),
            (EXE, 0x27E48A, b"\x48\x4E"),
        ],
        "legacy": [
            (EXE, 0x27E47A, b"\x50\x50"),
            (EXE, 0x27E48A, b"\x50\x50"),
        ],
    },
    "Shiva": {
        "default": [
            (EXE, 0x27E4DA, b"\x42\x72"),
            (EXE, 0x27E4EA, b"\x42\x72"),
        ],
        "bg": [
            (EXE, 0x27E4DA, b"\x42\x47"),
            (EXE, 0x27E4EA, b"\x42\x47"),
        ],
    },
    "Christian": {
        "default": [
            (EXE, 0x27F07A, b"\x4B\x6E"),
            (EXE, 0x27F08A, b"\x4B\x6E"),
        ],
        "ashan": [
            (EXE, 0x27F07A, b"\x48\x4E"),
            (EXE, 0x27F08A, b"\x48\x4E"),
        ],
        "campaign": [
            (EXE, 0x27F07A, b"\x4C\x47"),
            (EXE, 0x27F08A, b"\x4C\x47"),
        ],
    },
    "Edric": {
        "default": [
            (EXE, 0x27F0FA, b"\x4B\x6E"),
            (EXE, 0x27F10A, b"\x4B\x6E"),
        ],
        "ashan": [
            (EXE, 0x27F0FA, b"\x48\x4E"),
            (EXE, 0x27F10A, b"\x48\x4E"),
        ],
    },
    "Ciele": {
        "default": [
            (EXE, 0x27DFFA, b"\x65\x6C"),
            (EXE, 0x27E00A, b"\x65\x6C"),
        ],
        "ashan": [
            (EXE, 0x27DFFA, b"\x50\x50"),
            (EXE, 0x27E00A, b"\x50\x50"),
        ],
        "bg": [
            (EXE, 0x27DFFA, b"\x42\x47"),
            (EXE, 0x27E00A, b"\x42\x47"),
        ],
    },
    "Tyris": {
        "default": [
            (EXE, 0x27F05A, b"\x4B\x6E"),
            (EXE, 0x27F06A, b"\x4B\x6E"),
        ],
        "ashan": [
            (EXE, 0x27F05A, b"\x48\x4E"),
            (EXE, 0x27F06A, b"\x48\x4E"),
        ],
    },
    "Adelaide": {
        "default": [
            (EXE, 0x27EFDA, b"\x43\x6C"),
            (EXE, 0x27EFEA, b"\x43\x6C"),
        ],
        "bg": [
            (EXE, 0x27EFDA, b"\x42\x47"),
            (EXE, 0x27EFEA, b"\x42\x47"),
        ],
        "ashan": [
            (EXE, 0x27EFDA, b"\x48\x4E"),
            (EXE, 0x27EFEA, b"\x48\x4E"),
        ],
    },
    "Rion": {
        "default": [
            (EXE, 0x27F03A, b"\x43\x6C"),
            (EXE, 0x27F04A, b"\x43\x6C"),
        ],
        "bg": [
            (EXE, 0x27F03A, b"\x42\x47"),
            (EXE, 0x27F04A, b"\x42\x47"),
        ],
    },
    "Jenova": {
        "default": [
            (EXE, 0x27EEFA, b"\x52\x6E"),
            (EXE, 0x27EF0A, b"\x52\x6E"),
        ],
        "ashan": [
            (EXE, 0x27EEFA, b"\x48\x4E"),
            (EXE, 0x27EF0A, b"\x48\x4E"),
        ],
    },
    "Ivor": {
        "default": [
            (EXE, 0x27EE9A, b"\x52\x6E"),
            (EXE, 0x27EEAA, b"\x52\x6E"),
        ],
        "ashan": [
            (EXE, 0x27EE9A, b"\x48\x4E"),
            (EXE, 0x27EEAA, b"\x48\x4E"),
        ],
    },
    "Gelu": {
        "default": [
            (EXE, 0x27DEBA, b"\x53\x68"),
            (EXE, 0x27DEBA, b"\x53\x68"),
        ],
        "wow": [
            (EXE, 0x27DEBA, b"\x57\x57"),
            (EXE, 0x27DEBA, b"\x57\x57"),
        ],
    },
    "Nymus": {
        "default": [
            (EXE, 0x27EA5A, b"\x48\x72"),
            (EXE, 0x27EA6A, b"\x48\x72"),
        ],
        "wow": [
            (EXE, 0x27EA5A, b"\x57\x57"),
            (EXE, 0x27EA6A, b"\x57\x57"),
        ],
        "ashan": [
            (EXE, 0x27EA5A, b"\x48\x4E"),
            (EXE, 0x27EA6A, b"\x48\x4E"),
        ],
    },
    "Rashka": {
        "default": [
            (EXE, 0x27EB1A, b"\x48\x72"),
            (EXE, 0x27EB2A, b"\x48\x72"),
        ],
        "bg": [
            (EXE, 0x27EB1A, b"\x42\x47"),
            (EXE, 0x27EB2A, b"\x42\x47"),
        ],
        "ashan": [
            (EXE, 0x27EB1A, b"\x48\x4E"),
            (EXE, 0x27EB2A, b"\x48\x4E"),
        ],
    },
    "Moandor": {
        "default": [
            (EXE, 0x27E8FA, b"\x44\x6b"),
            (EXE, 0x27E90A, b"\x44\x6b"),
        ],
        "ashan": [
            (EXE, 0x27E8FA, b"\x48\x4E"),
            (EXE, 0x27E90A, b"\x48\x4E"),
        ],
    },
    "Charna": {
        "default": [
            (EXE, 0x27E8DA, b"\x44\x6b"),
            (EXE, 0x27E8EA, b"\x44\x6b"),
        ],
        "ashan": [
            (EXE, 0x27E8DA, b"\x48\x4E"),
            (EXE, 0x27E8EA, b"\x48\x4E"),
        ],
    },
    "Tamika": {
        "default": [
            (EXE, 0x27E8BA, b"\x44\x6b"),
            (EXE, 0x27E8CA, b"\x44\x6b"),
        ],
        "bg": [
            (EXE, 0x27E8BA, b"\x42\x47"),
            (EXE, 0x27E8CA, b"\x42\x47"),
        ],
    },
    "Sephinroth": {
        "default": [
            (EXE, 0x27E57A, b"\x57\x6C"),
            (EXE, 0x27E58A, b"\x57\x6C"),
        ],
        "ashan": [
            (EXE, 0x27E57A, b"\x48\x4E"),
            (EXE, 0x27E58A, b"\x48\x4E"),
        ],
    },
    "Darkstorn": {
        "default": [
            (EXE, 0x27E55A, b"\x57\x6C"),
            (EXE, 0x27E56A, b"\x57\x6C"),
        ],
        "ashan": [
            (EXE, 0x27E55A, b"\x48\x4E"),
            (EXE, 0x27E56A, b"\x48\x4E"),
        ],
    },
    "Drakon": {
        "default": [
            (EXE, 0x27E31A, b"\x42\x73"),
            (EXE, 0x27E32A, b"\x42\x73"),
        ],
        "ashan": [
            (EXE, 0x27E31A, b"\x48\x4E"),
            (EXE, 0x27E32A, b"\x48\x4E"),
        ],
    },
    "Tazar": {
        "default": [
            (EXE, 0x27E2DA, b"\x42\x73"),
            (EXE, 0x27E2EA, b"\x42\x73"),
        ],
        "bg": [
            (EXE, 0x27E2DA, b"\x42\x47"),
            (EXE, 0x27E2EA, b"\x42\x47"),
        ],
        "ashan": [
            (EXE, 0x27E2DA, b"\x48\x4E"),
            (EXE, 0x27E2EA, b"\x48\x4E"),
        ],
    },
    "Wystan": {
        "default": [
            (EXE, 0x27E25A, b"\x42\x73"),
            (EXE, 0x27E26A, b"\x42\x73"),
        ],
        "bg": [
            (EXE, 0x27E25A, b"\x42\x47"),
            (EXE, 0x27E26A, b"\x42\x47"),
        ],
    },
    "Thant": {
        "default": [
            (EXE, 0x27E7BA, b"\x4E\x63"),
            (EXE, 0x27E7CA, b"\x4E\x63"),
        ],
        "oe": [
            (EXE, 0x27E7BA, b"\x48\x4E"),
            (EXE, 0x27E7CA, b"\x48\x4E"),
        ],
    },
    "Vidomina": {
        "default": [
            (EXE, 0x27E77A, b"\x4E\x63"),
            (EXE, 0x27E78A, b"\x4E\x63"),
        ],
        "bg": [
            (EXE, 0x27E77A, b"\x42\x47"),
            (EXE, 0x27E78A, b"\x42\x47"),
        ],
    },
    "Adrienne": {
        "default": [
            (EXE, 0x27DF1A, b"\x53\x68"),
            (EXE, 0x27DF2A, b"\x53\x68"),
        ],
        "bg": [
            (EXE, 0x27DF1A, b"\x42\x47"),
            (EXE, 0x27DF2A, b"\x42\x47"),
        ],
    },
    "Bron": {
        "default": [
            (EXE, 0x27E33A, b"\x42\x73"),
            (EXE, 0x27E34A, b"\x42\x73"),
        ],
        "bg": [
            (EXE, 0x27E33A, b"\x42\x47"),
            (EXE, 0x27E34A, b"\x42\x47"),
        ],
    },
    "Clancy": {
        "default": [
            (EXE, 0x27EE7A, b"\x52\x6E"),
            (EXE, 0x27EE8A, b"\x52\x6e"),
        ],
        "bg": [
            (EXE, 0x27EE7A, b"\x42\x47"),
            (EXE, 0x27EE8A, b"\x42\x47"),
        ],
    },
    "Deemer": {
        "default": [
            (EXE, 0x27E5FA, b"\x57\x6C"),
            (EXE, 0x27E60A, b"\x57\x6C"),
        ],
        "bg": [
            (EXE, 0x27E5FA, b"\x42\x47"),
            (EXE, 0x27E60A, b"\x42\x47"),
        ],
    },
    "Jeddite": {
        "default": [
            (EXE, 0x27E5DA, b"\x57\x6C"),
            (EXE, 0x27E5EA, b"\x57\x6C"),
        ],
        "bg": [
            (EXE, 0x27E5DA, b"\x42\x47"),
            (EXE, 0x27E5EA, b"\x42\x47"),
        ],
    },
    "Dracon": {
        "default": [
            (EXE, 0x27DEDA, b"\x53\x68"),
            (EXE, 0x27DEEA, b"\x53\x68"),
        ],
        "bg": [
            (EXE, 0x27DEDA, b"\x42\x47"),
            (EXE, 0x27DEEA, b"\x42\x47"),
        ],
    },
    "Erdamon": {
        "default": [
            (EXE, 0x27E09A, b"\x70\x6c"),
            (EXE, 0x27E0AA, b"\x70\x6c"),
        ],
        "bg": [
            (EXE, 0x27E09A, b"\x50\x47"),
            (EXE, 0x27E0AA, b"\x50\x47"),
        ],
    },
    "Monere": {
        "default": [
            (EXE, 0x27E0BA, b"\x70\x6c"),
            (EXE, 0x27E0CA, b"\x70\x6c"),
        ],
        "bg": [
            (EXE, 0x27E0BA, b"\x50\x47"),
            (EXE, 0x27E0CA, b"\x50\x47"),
        ],
    },
    "Fiona": {
        "default": [
            (EXE, 0x27EB3A, b"\x48\x72"),
            (EXE, 0x27EB4A, b"\x48\x72"),
        ],
        "bg": [
            (EXE, 0x27EB3A, b"\x42\x47"),
            (EXE, 0x27EB4A, b"\x42\x47"),
        ],
    },
    "Gundula": {
        "default": [
            (EXE, 0x27E39A, b"\x42\x6D"),
            (EXE, 0x27E3AA, b"\x42\x6D"),
        ],
        "bg": [
            (EXE, 0x27E39A, b"\x42\x47"),
            (EXE, 0x27E3AA, b"\x42\x47"),
        ],
    },
    "Gunnar": {
        "default": [
            (EXE, 0x27E69A, b"\x4F\x76"),
            (EXE, 0x27E6AA, b"\x4F\x76"),
        ],
        "wow": [
            (EXE, 0x27E69A, b"\x57\x57"),
            (EXE, 0x27E6AA, b"\x57\x57"),
        ],
    },
    "Xyron": {
        "default": [
            (EXE, 0x27EA1A, b"\x44\x6D"),
            (EXE, 0x27EA2A, b"\x44\x6D"),
        ],
        "bg": [
            (EXE, 0x27EA1A, b"\x42\x47"),
            (EXE, 0x27EA2A, b"\x42\x47"),
        ],
    },
    "Zydar": {
        "default": [
            (EXE, 0x27E97A, b"\x44\x6D"),
            (EXE, 0x27E98A, b"\x44\x6D"),
        ],
        "bg": [
            (EXE, 0x27E97A, b"\x42\x47"),
            (EXE, 0x27E98A, b"\x42\x47"),
        ],
    },
    "Solmyr": {
        "default": [
            (EXE, 0x27EB9A, b"\x57\x7A"),
            (EXE, 0x27EBAA, b"\x57\x7A"),
        ],
        "bg": [
            (EXE, 0x27EB9A, b"\x42\x47"),
            (EXE, 0x27EBAA, b"\x42\x47"),
        ],
        "wow": [
            (EXE, 0x27EB9A, b"\x57\x57"),
            (EXE, 0x27EBAA, b"\x57\x57"),
        ],
        "ashan": [
            (EXE, 0x27EB9A, b"\x48\x4E"),
            (EXE, 0x27EBAA, b"\x48\x4E"),
        ],
    },
    "Iona": {
        "default": [
            (EXE, 0x27EC5A, b"\x41\x6c"),
            (EXE, 0x27EC6A, b"\x41\x6c"),
        ],
        "bg": [
            (EXE, 0x27EC5A, b"\x42\x47"),
            (EXE, 0x27EC6A, b"\x42\x47"),
        ],
    },
    "Josephine": {
        "default": [
            (EXE, 0x27ECFA, b"\x41\x6c"),
            (EXE, 0x27ED0A, b"\x41\x6c"),
        ],
        "bg": [
            (EXE, 0x27ECFA, b"\x42\x47"),
            (EXE, 0x27ED0A, b"\x42\x47"),
        ],
    },
    "Mephala": {
        "default": [
            (EXE, 0x27EF3A, b"\x52\x6E"),
            (EXE, 0x27EF4A, b"\x52\x6E"),
        ],
        "bg": [
            (EXE, 0x27EF3A, b"\x42\x47"),
            (EXE, 0x27EF4A, b"\x42\x47"),
        ],
        "wow": [
            (EXE, 0x27EF3A, b"\x57\x57"),
            (EXE, 0x27EF4A, b"\x57\x57"),
        ],
    },    
    "ManticoreBank": {
        False: [
#crbanks -> PP
            (EXE, 0x2703AD, b"\x6B\x73"),
#objects.txt -> tP
            (EXE, 0x27FBDA, b"\x73"),
#manticore bank code
            (EXE, 0x270340, b"\x73"),
            (EXE, 0x27039C, b"\xFF\xFF\xFF\xFF"),
            ],
        True: [
#crbanks -> PP
            (EXE, 0x2703AD, b"\x50\x50"),            
#objects.txt -> tP
            (EXE, 0x27FBDA, b"\x50"),
#manticore bank code
            (EXE, 0x270340, b"\x49"),
            (EXE, 0x27039C, b"\x50\x00\x00\x00"),
            ]                
        },    
    "MKC_skills": {
        False:
            [
#sstraits -> CC
            (EXE, 0x27F17A, b"\x74\x73"),
#objects.txt -> Ps
            (EXE, 0x27FBD9, b"\x74"),
#learning
            (EXE, 0xe4ac4, b"\x78\xea"),
#mysticism % values
            (hota_dll, 0x1Ec470, b"\xCD\xCC\xCC\x3D\xCD\xCC\x4C\x3E\x9A\x99\x99\x3E"),
            (hota_dll, 0x19a15E, b"\x05"),
            (hota_dll, 0x19a16a, b"\x0A"),
            (hota_dll, 0x19a174, b"\x0F"),
#+4 max positive morale (Luck has its own button)
            (EXE, 0x064586, b"\x03"),
            (EXE, 0x0645A0, b"\x03"),
# Tactics without the speed bonus:
            (EXE, 0xE6656, b"\x8B\x43\x1A\x8D\x14\x80"),
#logistics armorer offense learning specce
            (EXE, 0x279CD2, b"\x65"),
            (EXE, 0x0E4F1E, b"\xE4\xEA\x63\x00"),
            (EXE, 0x0E4569, b"\xE4\xEA\x63\x00"),
            (EXE, 0x0E45C9, b"\xE4\xEA\x63\x00"),
            (EXE, 0xe4af9, b"\x80\xEA\x63\x00 "),
            (DAT, find_hex(DAT, b"\x7B\x4C\x65\x61\x72\x6E\x69\x6E\x67\x7D\x0D\x0A\x0D\x0A\x52", default_0 = True)[0] + 24, b"\x20\x32\x30"),
            (DAT, find_hex(DAT, b"\x7B\x4E\x61\x75\x6B\x61\x7D\x0D\x0A\x0D\x0A", default_0 = True)[0] + 24, b"\x20\x35"),
#estates false
	(hota_dll, 0x19A102, b"\xFA\x00"),
	(hota_dll, 0x19A10C, b"\xF4\x01"),
	(hota_dll, 0x19A116, b"\xE8\x03"),
	],
	True: 
		[
#sstraits -> CC
            (EXE, 0x27F17A, b"\x63\x63"),
#objects.txt -> Ps
            (EXE, 0x27FBD9, b"\x63"),
#logistics armorer offense learning specce
            (EXE, 0x279CD2, b"\x63"),
            (EXE, 0x0E4F1E, b"\xB2\xD3\x4C\x00"),
            (EXE, 0x0E4569, b"\xB6\xD3\x4C\x00"),
            (EXE, 0x0E45C9, b"\xBA\xD3\x4C\x00"),
            (EXE, 0xe4af9, b"\xE4\xEA\x63\x00 "),
            (DAT, find_hex(DAT, b"\x7B\x4C\x65\x61\x72\x6E\x69\x6E\x67\x7D\x0D\x0A\x0D\x0A\x52", default_0 = True)[0] + 24, b"\x61\x20\x35"),
            (DAT, find_hex(DAT, b"\x7B\x4E\x61\x75\x6B\x61\x7D\x0D\x0A\x0D\x0A", default_0 = True)[0] + 24, b"\x32\x30"),
#learning
            (EXE, 0xe4ac4, b"\x58\xea"),
#mysticism % values
            (hota_dll, 0x1Ec470, b"\x9A\x99\x99\x3E\x9A\x99\x19\x3F\x66\x66\x66\x3F"),
            (hota_dll, 0x19a15E, b"\x14"),
            (hota_dll, 0x19a16a, b"\x28"),
            (hota_dll, 0x19a174, b"\x3C"),
#+4 max positive morale (Luck has its own button)
            (EXE, 0x064586, b"\x04"),
            (EXE, 0x0645A0, b"\x04"),
#Tactics give 1 speed on expert
            (EXE, 0xE6656, b"\xE8\xDA\x6c\xfe\xff\x90"),
		],
    },
    "MKC": {
        False: 
            [
#hctraits -> CC
            (EXE, 0x27F16A, b"\x74\x73"),
#movement -> movemmkc
            (EXE, 0x279CE1, b"\x65\x6E\x74"),
#artraits -> artraicc
            (EXE, 0x260b86, b"\x74\x73"),
#RESISTANCE
            (EXE, 0x0E49FF, b"\x3A"),
            (EXE, 0x0E49B9, b"\x39"),
            (EXE, 0x0E4A80, b"\x28\xEB\x63\x00"),
#cape of conjuring
            (EXE, 0x0E50E6, b"\x03"),
#recanters cloak
            (EXE, 0x19EE6C, b"\x02\x7E"),
#speed boost switch - cape of velocity vs necklace of swiftiness
            (EXE, 0x0E65FF, b"\x61"),
            (EXE, 0x0E6647, b"\x63"),
#speculum (Oh god why)
# call free space E8 F7 8F FE FF (84 C0 74 02 43 43 C3)
            (EXE, 0x0E43C2, b"\x84\xC0\x74\x01\x43"),
#Elixir of Life
            (EXE, 0xE671A, b"\x02"),
            (EXE, 0x0E66B3, b"\x02"),
            (EXE, 0x0E667C, b"\x5F"),
            (EXE, 0x0E66BB, b"\x5E"),
            (EXE, 0xe66c8, b"\xEB\x0E\xE8\x91\x2D\xFF\xFF\x84\xC0\x74\x03\x83\xC3\x03\xEB\x21\x8B\x7D\x08\x8B\x0D\xB0\x47\x67\x00\x8D\x04\xFD\x00\x00\x00\x00\x2B\xC7\x8D\x3C\x87\xC1\xE7\x02\xF6\x44\x0F\x10\x10\x74\x26\xEB\x02\xEB\x6B\x6A\x60\xEB\x57\xE8\x5C\x2D\xFF\xFF\x84\xC0\x74\x15\x8B\x15\xB0\x47\x67\x00\x8B\x44\x17\x4C\x99\x83\xE2\x03\x03\xC2\xC1\xF8\x02\x03\xD8\x8B\x46\x4C\x5F\x03\xC3\x89\x46\x4C\x5E\x5B\x8B\xE5\x5D\xC2\x08\x00\x90\x90\xB8\x04\x00\x00\x00\x83\xC1\x10\x83\x39\x00\x75\x0B\x48\x83\xE9\x04\x85\xC0\x7D\xF3\x32\xC0\xC3\xB0\x01\xC3\x90\x90\x90\x90\x90\x8B\x41\x04\xC3\xEB\x0A\x8B\x4D\xFC\xE9\x6C\xFF\xFF\xFF\x90\x90\x8B\x41\x08\xC3\xEB\x0A\x8B\x4D\xFC\x68\x83\x00\x00\x00\xEB\x8F"),
#Angelica Lyons
            (EXE, 0x64fe5, b"\x32"),
            (EXE, 0x064FE7, b"\x03"),
            (EXE, 0x23e7d4, b"01 01 01 01 02 02 02 02 02 02 02 02 03 03 03 03 03 03 03 03 04 04 04 04"),
#dragon father
            (EXE, 0x4a1eb, b"\x05"),
#statue of legion
            (EXE, 0x1BFE37, b"84\xC0\x74\x06\x83\xC7\x08\x90\x90\x90"), 
            (EXE, 0x1BFE53, b"84\xC0\x74\x07\x83\xC7\x08\x90\x90\x90\x90"), 
            (EXE, 0x1BFE74, b"84\xC0\x74\x06\x83\xC7\x06\x90\x90\x90"), 
            (EXE, 0x1BFE90, b"84\xC0\x74\x04\x83\xC7\x06\x90"), 
            (EXE, 0x1BFEAE, b"84\xC0\x74\x06\x83\xC7\x04\x90\x90\x90"), 
            (EXE, 0x1BFEC6, b"84\xC0\x74\x07\x83\xC7\x04\x90\x90\x90\x90"), 
            (EXE, 0x1BFEE7, b"84\xC0\x74\x05\x83\xC7\x03\x90\x90"), 
            (EXE, 0x1BFEFE, b"84\xC0\x74\x04\x83\xC7\x03\x90"), 
            (EXE, 0x1BFF1C, b"84\xC0\x74\x03\x83\xC7\x02"), 
            (EXE, 0x1BFF31, b"84\xC0\x74\x03\x83\xC7\x02"), 
#genies
            (EXE, 0x287735, b"\x10"), 
            (EXE, 0x2868DD, b"\x10"), 
            (EXE, 0x2866BD, b"\x40"), 
#pit lords
  		  	(EXE, 0x471D5, b"\x8B\x89\xC0\x00\x00\x00"), 
			(EXE, 0x470A1, b"\x8B\x89\xC0\x00\x00\x00"), 
			(DAT, find_hex(DAT, b"\x23\x31\x33\x36\x0D\x0A\x72\x61\x69\x73\x65\x73", default_0 = True)[0] +6, b"\x72\x61\x69\x73\x65\x73\x20\x68\x65\x61\x6C\x74\x68\x3A\x20\x25\x73\x2C\x20\x44\x65\x6D\x6F\x6E\x73\x3A\x20\x25\x73"), 
			(DAT, find_hex(DAT, b"\x23\x31\x33\x36\x0D\x0A\x77\x73\x6B\x72\x7A\x65\x73\x7A\x61", default_0 = True)[0] +6, b"\x77\x73\x6B\x72\x7A\x65\x73\x7A\x61\x20\x25\x73\x20\x70\x75\x6E\x6B\x74\xF3\x77\x20\xBF\x79\x63\x69\x61\x2C\x20\x64\x65\x6D\x6F\x6E\xF3\x77\x3A\x20\x25\x73"), 
#1-turn spells (Slow, Haste) 
   		 (EXE, 0x450DE, b"\x02\x02"),
#Berserk, Hypnotize, Blind, and Forgetfulness
			(EXE, 0x450E4, b"\x00\x01\x02\x02"),
#Antimagic to work for 2 turns, hypnotize for 1/3, prayer for 1/4. 
			(EXE, 0xCD165, b"\xEB\x1C"),
#magic mirror
  		  (EXE, 0x2867CC, b"\x45"),
#cape of conjuring
  		  (EXE, 0x0E50E6, b"\x03"),
#cape of velocity, necklace of swiftness switcheroo
 		   (EXE, 0x0E6647, b"\x63"),
  		  (EXE, 0x0E65FF, b"\x61"),
#cure
  		  (EXE, 0x286854, b"\x41"),
#jousting to 10%
   		 (EXE, 0x43095, b"\xDC\x0D\x58\xAC\x63\x00"),
#   		 (EXE, 0xcd36c, b"\x75"),
#Zombies have phoenix rebirth
        (EXE, 0x69061, b"\x0F\x85\x2B\x01\x00\x00"),
#Petrification doubles damage taken
        (EXE, 0x043D47, b"\xDC"),
        (EXE, 0x043D49, b"\x70\xAC\x63\x00"),
#earth elem air elem switcheroo
        (EXE, 0x04B2DD, b"\x06"),
        (EXE, 0x04B2DD, b"\x03"),
        (EXE, 0x04B2DD, b"\x06"),
        (EXE, 0x04B2DD, b"\x03"),
        (EXE, 0x04B2DD, b"\x05"), 
        (EXE, 0x04B2DD, b"\x02"), 
        (EXE, 0x04B2DD, b"\x05"), 
        (EXE, 0x04B2DD, b"\x02"), 
#seawitch, sorceress
        (EXE, find_hex(DAT, b"\x04\x00\x00\x00\x00\x00\x00\x00\x23\x00\x00\x00\x06\x00\x00\x00\x0C\x00\x00\x00\x07\x00\x00\x00\x0A\x00\x00\x00\x0E\x00\x00\x00\x0C\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x10\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x41\x00\x00\x00\x12\x00\x00\x00\xA2", default_0=True)[0], b"04"),
        (EXE, find_hex(DAT, b"\x04\x00\x00\x00\x00\x00\x00\x00\x23\x00\x00\x00\x07\x00\x00\x00\x0C\x00\x00\x00\x09\x00\x00\x00\x0A\x00\x00\x00\x10\x00\x00\x00\x0C\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x0C\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x41\x00\x00\x00\x12", default_0=True)[0], b"04"),
#familiar growth
        (EXE, 0x288854, b"\x09"),
        (EXE, 0x0C861E, b"\xBA\x12\x00\x00\x00\x90"),
        (EXE, 0x0CC94F, b"\xB9\x12\x00\x00\x00\x90"),
#fire elem
        (EXE, 0x273770, b"\x02"),
#Cannon
        (EXE, find_hex(DAT, b"\x03\x00\x00\x00\x07\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x92", default_0=True)[0], b"\x04\x00\x00\x00\x08"),
#archmagi and magi mana buff
        (EXE, 0xE55E7, b"\x02"),
#orcs no melee pen
        (EXE, 0x272BA9, b"\x10"),
#archmagi, magi ring of magi buff
        (EXE, 0xE55E7, b"\x02"),
        (EXE, 0xF840A, b"\x02"),
#Frederique 
        (DAT, find_hex(DAT, b"\x00\x00\x00\x00\x07\x00\x00\x00\x15\x00\x00\x00\x07\x00\x00\x00\x01\x00\x00\x00\x18\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x35\x00\x00\x00", default_0=True)[0] + 36, b"\x8A\x00\x00\x00\xB0\x00\x00\x00\xAE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x03\x00\x00\x00\x05\x00\x00\x00\x04\x00\x00\x00\x06"),
        ],
        True: [
#hctraits -> CC
            (EXE, 0x27F16A, b"\x63\x63"),
#movement -> movemmkc
            (EXE, 0x279CE1, b"\x6D\x6B\x63"),
#artraits -> artraicc
            (EXE, 0x260b86, b"\x63\x63"),
#RESISTANCE
            (EXE, 0x0E49FF, b"\x39"),
            (EXE, 0x0E49B9, b"\x3A"),
            (EXE, 0x0E4A80, b"\xE4\xEA\x63\x00"),
#cape of conjuring
            (EXE, 0x0E50E6, b"\x0A"),
#recanters cloak
            (EXE, 0x19EE6C, b"\x03\x75"),
#speed boost switch - cape of velocity vs necklace of swiftiness
            (EXE, 0x0E65FF, b"\x63"),
            (EXE, 0x0E6647, b"\x61"),
#speculum (Oh god why) 
# call free space E8 F7 8F FE FF (84 C0 74 02 43 43 C3)
            (EXE, 0x0E43C2, b"\xE8\xF7\x8F\xFE\xFF"),
#Elixir of Life
            (EXE, 0xE671A, b"\x03"),
            (EXE, 0x0E66B3, b"\x01"), 
            (EXE, 0x0E667C, b"\x5E"),
            (EXE, 0x0E66BB, b"\x5F"),
            (EXE, 0xe66c8, b"\x6A\x60\x8B\xCF\xE8\x8F\x2D\xFF\xFF\x84\xC0\x74\x03\x83\xC3\x02\x8B\x7D\x08\x8B\x0D\xB0\x47\x67\x00\x8D\x04\xFD\x00\x00\x00\x00\x2B\xC7\x8D\x3C\x87\xC1\xE7\x02\xF6\x44\x0F\x10\x10\x74\x26\x8B\x4D\xFC\x68\x83\x00\x00\x00\xE8\x5C\x2D\xFF\xFF\x84\xC0\x74\x15\x8B\x15\xB0\x47\x67\x00\x8B\x44\x17\x4C\x99\x83\xE2\x03\x03\xC2\xC1\xF8\x02\x03\xD8\x8B\x46\x4C\x5F\x03\xC3\x89\x46\x4C\x5E\x5B\x8B\xE5\x5D\xC2\x08\x00\x90\x90\xB8\x04\x00\x00\x00\x83\xC1\x10\x83\x39\x00\x75\x0B\x48\x83\xE9\x04\x85\xC0\x7D\xF3\x32\xC0\xC3\xB0\x01\xC3\x90\x90\x90\x90\x90\x8B\x41\x04\xC3\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x8B\x41\x08\xC3\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"),
#Angelica Lyons
            (EXE, 0x64fe5, b"\x05"),
            (EXE, 0x064FE7, b"\x01"),
            (EXE, 0x23e7d4, b"01 01 01 01 02 02 02 02 03 03 03 03 04 04 04 04 05 05 05 05 06 06 06 06"),
#dragon father
            (EXE, 0x4a1eb, b"\x04"), 
#statue of legion
            (EXE, 0x1BFE37, b"25\xFF\x00\x00\x00\x8B\xF8\x8D\x3C\xBF"), 
            (EXE, 0x1BFE53, b"25\xFF\x00\x00\x00\x8D\x0C\x38\x8D\x3C\x81"), 
            (EXE, 0x1BFE74, b"25\xFF\x00\x00\x00\xC1\xE0\x02\x8B\xF8"), 
            (EXE, 0x1BFE90, b"25\xFF\x00\x00\x00\x8D\x3C\x87"), 
            (EXE, 0x1BFEAE, b"25\xFF\x00\x00\x00\x8B\xF8\x8D\x3C\x7F"), 
            (EXE, 0x1BFEC6, b"25\xFF\x00\x00\x00\x8D\x14\x38\x8D\x3C\x42"), 
            (EXE, 0x1BFEE7, b"25\xFF\x00\x00\x00\xD1\xE0\x8B\xF8"), 
            (EXE, 0x1BFEFE, b"25\xFF\x00\x00\x00\x8D\x3C\x47"), 
            (EXE, 0x1BFF1C, b"25\xFF\x00\x00\x00\x8B\xF8"), 
            (EXE, 0x1BFF31, b"25\xFF\x00\x00\x00\x03\xF8"), 
#genies
            (EXE, 0x287735, b"\x18"), 
            (EXE, 0x2868DD, b"\x18"), 
            (EXE, 0x2866BD, b"\x48"), 
#pit lords
			(EXE, 0x471D5, b"\xE8\x71\x61\x08\x00\x90"), 
			(EXE, 0x470A1, b"\xE8\xA5\x62\x08\x00\x90"), 
			(DAT, find_hex(DAT, b"\x23\x31\x33\x36\x0D\x0A\x72\x61\x69\x73\x65\x73", default_0 = True)[0] +6, b"\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20"), 
			(DAT, find_hex(DAT, b"\x23\x31\x33\x36\x0D\x0A\x77\x73\x6B\x72\x7A\x65\x73\x7A\x61", default_0 = True)[0] +6, b"\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20"), 
#estates true
			(hota_dll, 0x19A102, b"\xE8\x03"),
			(hota_dll, 0x19A10C, b"\xC4\x09"),
			(hota_dll, 0x19A116, b"\x88\x13"),
#1-turn spells (Slow, Haste,
			(EXE, 0x450DE, b"\x01\x01"),
#Berserk, Hypnotize, Blind, and Forgetfulness
			(EXE, 0x450E4, b"\x01\x02\x01\x01"), 
#Antimagic to work for 2 turns, hypnotize for 1/3, prayer for 1/4. 
			(EXE, 0xCD165, b"\x90\x90"),
#magic mirror
  		  (EXE, 0x2867CC, b"\x15"),
#cape of conjuring
  		  (EXE, 0x0E50E6, b"\x0A"),
#cape of velocity, necklace of swiftness switcheroo
  		  (EXE, 0x0E6647, b"\x61"),
  		  (EXE, 0x0E65FF, b"\x63"),
#cure
  		  (EXE, 0x286854, b"\x11"),
#view air
   		 (EXE, 0x1FC3A6, b"\x01"),
#    (EXE, 0x1FC3AA, b"\x7D"),    
#jousting to 10%
   		 (EXE, 0x43095, b"\xDC\x0D\x2d\xd3\x0c\x00"),
#   		 (EXE, 0xcd36c, b"\xeb"),
#Zombies have phoenix rebirth
#0xCD31B: 81 7E 34 3B 00 00 00 0F 84 3F BD F9 FF E9 65 BE F9 FF
        (EXE, 0x69061, b"\x0f\x85\xB1\x42\x06\x00"),
#Petrification doubles damage taken
        (EXE, 0x043D47, b"\xD8"),
        (EXE, 0x043D49, b"\xA5\xAB\x63\x00"),
#earth elem air elem switcheroo
        (EXE, 0x04A6B8, b"\x05"),
        (EXE, 0x04B2D0, b"\x02"),
        (EXE, 0x04A6C7, b"\x05"),
        (EXE, 0x04B2DF, b"\x02"),
        (EXE, 0x04A6B9, b"\x06"),
        (EXE, 0x04B2D1, b"\x03"),
        (EXE, 0x04A6C5, b"\x06"),
        (EXE, 0x04B2DD, b"\x03"),
#seawitch, sorceress
        (EXE, find_hex(DAT, b"\x03\x00\x00\x00\x00\x00\x00\x00\x23\x00\x00\x00\x06\x00\x00\x00\x0C\x00\x00\x00\x07\x00\x00\x00\x0A\x00\x00\x00\x0E\x00\x00\x00\x0C\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x10\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x41\x00\x00\x00\x12\x00\x00\x00\xA2", default_0=True)[0], b"04"),
        (EXE, find_hex(DAT, b"\x03\x00\x00\x00\x00\x00\x00\x00\x23\x00\x00\x00\x07\x00\x00\x00\x0C\x00\x00\x00\x09\x00\x00\x00\x0A\x00\x00\x00\x10\x00\x00\x00\x0C\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x0C\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x41\x00\x00\x00\x12", default_0=True)[0], b"04"),
#familiar growth
        (EXE, 0x288854, b"\x08"),
        (EXE, 0x0C861E, b"\xBA\x0f\x00\x00\x00\x90"),
        (EXE, 0x0CC94F, b"\xB9\x0f\x00\x00\x00\x90"),
#fire elem
        (EXE, 0x273770, b"\x00"),
#Cannon
        (EXE, find_hex(DAT, b"\x03\x00\x00\x00\x07\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x92", default_0=True)[0], b"\x04\x00\x00\x00\x08"),
#archmagi and magi mana buff
        (EXE, 0xE55E7, b"\x03"),
#orcs melee pen
        (EXE, 0x272BA9, b"\x00"),
#archmagi, magi ring of magi buff
        (EXE, 0xE55E7, b"\x03"),
        (EXE, 0xF840A, b"\x03"),
#Frederique 
        (DAT, find_hex(DAT, b"\x00\x00\x00\x00\x07\x00\x00\x00\x15\x00\x00\x00\x07\x00\x00\x00\x01\x00\x00\x00\x18\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x35\x00\x00\x00", default_0=True)[0] + 36, b"\xB0\x00\x00\x00\xB0\x00\x00\x00\xB0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x05\x00\x00\x00\x03\x00\x00\x00\x05\x00\x00\x00\x03\x00\x00\x00\x05"),
            ],
    },
}





HEX_EN = {
    "COTUK": {
        True: [
            (EXE, 0x0E3F33, b"\x38"),
            (EXE, 0x0E3F2A, b"\x3a"),
            (EXE, 0x0E3F1F, b"\x3D"),
            (DAT, 0x1AAE7, b"\x53\x6B\x65\x6C\x65\x74\x6F\x6E\x73\x0D\x0A\x41\x64\x76\x61\x6E\x63\x65\x64\x3A\x20\x57\x61\x6C\x6B\x69\x6E\x67\x20\x44\x65\x61\x64\x0D\x0A\x45\x78\x70\x65\x72\x74\x3A\x20\x57\x72\x61\x69\x74\x68\x73\x20"),
            (EXE, 0x260B86, b"\x74\x73"),
        ],
        False: [
            (EXE, 0x0E3F33, b"\x3a"),
            (EXE, 0x0E3F2A, b"\x3c"),
            (EXE, 0x0E3F1F, b"\x40"),
            (DAT, 0x1AAE7, b"\x57\x61\x6C\x6B\x69\x6E\x67\x20\x44\x65\x61\x64\x0D\x0A\x41\x64\x76\x61\x6E\x63\x65\x64\x3A\x20\x57\x69\x67\x68\x74\x73\x0D\x0A\x45\x78\x70\x65\x72\x74\x3A\x20\x4C\x69\x63\x68\x65\x73\x20\x20\x20\x20\x20"),
            (EXE, 0x260B86, b"\x50\x50"),
        ],
    },
    "Astra": {
        "default": [
            (DAT, 0x2C828, b"\x32"),
            (DAT, 0x4b52, b"\x32"),
            (DAT, 0x4b61, b"\x32"),
            (DAT, 0x2cb4e, b"\x32"),            
        ],
        "legacy": [
            (DAT, 0x2C828, b"\x50"),
            (DAT, 0x4b52, b"\x50"),
            (DAT, 0x4b61, b"\x50"),
            (DAT, 0x2cb4e, b"\x50"),
        ],
    },
    "Agar": {
        "default": [
            (DAT, 0x2C922, b"\x39"),
            (DAT, 0x2CC4D, b"\x39"),
        ],
        "legacy": [
            (DAT, 0x2C922, b"\x50"),
            (DAT, 0x2CC4D, b"\x50"),
            
        ],
    },
    "Wrathmont": {
        "default": [
            (DAT, 0x2C93A, b"\x31"),
            (DAT, 0x2CC65, b"\x31"),
        ],
        "legacy": [
            (DAT, 0x2C93A, b"\x50"),
            (DAT, 0x2CC65, b"\x50"),
        ],
    },
    "Ranloo": {
        "default": [
            (DAT, 0x2C881, b"\x44\x58"),
            (DAT, 0x2CBAC, b"\x44\x58"),
            (DAT, 0x5E4E, b"\x44\x58"),
            (DAT, 0x5E3D, b"\x44\x58"),
        ],
        "legacy": [
            (DAT, 0x2C881, b"\x50\x50"),
            (DAT, 0x2CBAC, b"\x50\x50"),
            (DAT, 0x5E4E, b"\x50\x50"),
            (DAT, 0x5E3D, b"\x50\x50"),
        ],
    },
    "UniqueStartingArmies": {
        False: [
            (EXE, 0x27F159, b"\x69"),
#tyris
            (EXE, 0x27a07c, b"\x02"),
#ingham
            (EXE, 0x27a248, b"\x02"),
#sorsha
            (EXE, 0x279Fc4, b"\x02"),
#clancy
            (EXE, 0x27a5e0, b"\x10"),
#ryland
            (EXE, 0x27a4cc, b"\x10"),
#aeris
            (EXE, 0x27a91c, b"\x10"),
#Iona
            (EXE, 0x27abfc, b"\x1E"),
#thane
            (EXE, 0x27d550, b"\x1E"),
#fafner
            (EXE, 0x27ab44, b"\x1E"),
#fafner
            (EXE, 0x27ab44, b"\x1E"),
#theodorus            
            (EXE, 0x27adc8, b"\x1E"),
#rashka
            (EXE, 0x27af94, b"\x2C"),
#nymus
            (EXE, 0x27B1BC, b"\x2C"),
#marius
            (EXE, 0x27AFF0, b"\x2C"),
#vokial
            (EXE, 0x27B554, b"\x3A"),
#moandor
            (EXE, 0x27B5B0, b"\x3A"),
#tamika
            (EXE, 0x27B668, b"\x3A"),
#dace
            (EXE, 0x27BB70, b"\x48"),
#synca
            (EXE, 0x27BCE0, b"\x48"),
#yog
            (EXE, 0x27C078, b"\x56"),
#shiva
            (EXE, 0x27C18C, b"\x56"),
#krellion
            (EXE, 0x27C244, b"\x56"),
#vey
            (EXE, 0x27C3B4, b"\x56"),
#alkin
            (EXE, 0x27C7A8, b"\x64"),
#broghild
            (EXE, 0x27C8BC, b"\x64"),        
#casmetra false
            (DAT, 0x3cc1, b"\x9B\x00\x00\x00\x9D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x06\x00\x00\x00\x09"),
#tancred false
            (DAT, 0x6c56, b"\xAC\x00\x00\x00\xAE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x07\x00\x00\x00\x09"),   
#Agar false
            (DAT, 0x82bd, b"\xAC\x00\x00\x00\xAE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x07\x00\x00\x00\x09"),   
            ],
        True: [
            (EXE, 0x27F159, b"\x50"),
#tyris
            (EXE, 0x27a07c, b"\x0A"),
#ingham
            (EXE, 0x27a248, b"\x08"),
#sorsha
            (EXE, 0x279Fc4, b"\x06"),
#clancy
            (EXE, 0x27a5e0, b"\x18"),
#ryland
            (EXE, 0x27a4cc, b"\x16"),
#aeris
            (EXE, 0x27a91c, b"\x14"),
#Iona
            (EXE, 0x27abfc, b"\x24"),
#thane
            (EXE, 0x27d550, b"\x24"),
#fafner
            (EXE, 0x27ab44, b"\x26"),
#theodorus            
            (EXE, 0x27adc8, b"\x22"),
#rashka
            (EXE, 0x27af94, b"\x34"),
#nymus
            (EXE, 0x27B1BC, b"\x32"),
#marius
            (EXE, 0x27AFF0, b"\x30"),
#vokial
            (EXE, 0x27B554, b"\x3e"),
#moandor
            (EXE, 0x27B5B0, b"\x40"),
#tamika
            (EXE, 0x27B668, b"\x42"),
#dace
            (EXE, 0x27BB70, b"\x4e"),
#synca
            (EXE, 0x27BCE0, b"\x50"),
#yog
            (EXE, 0x27C078, b"\x5e"),
#shiva
            (EXE, 0x27C18C, b"\x5c"),
#krellion
            (EXE, 0x27C244, b"\x5a"),
#vey
            (EXE, 0x27C3B4, b"\x5a"),
#alkin
            (EXE, 0x27C7A8, b"\x66"),
#broghild
            (EXE, 0x27C8BC, b"\x6c"),        
#casmetra true
            (DAT, 0x3cc1, b"\xA1\x00\x00\x00\x9D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x02\x00\x00\x00\x03"),   
#tancred true
            (DAT, 0x6c56, b"\xB4\x00\x00\x00\xAE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x01\x00\x00\x00\x01"),   
#Agar true
            (DAT, 0x82bd, b"\xB2\x00\x00\x00\xAE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x02\x00\x00\x00\x03"),   
            ],
    },    
    "StaticSpellSpecialties": {
        False: [
            (DAT, 0x45EC, b"\x31\x30\x25\x20\x66\x6F\x72\x20\x65\x76\x65\x72\x79\x20\x6E\x20\x68\x65\x72\x6F\x20\x6C\x65\x76\x65\x6C\x73\x2C\x20\x77\x68\x65\x72\x65\x20\x6E\x20\x69\x73\x20\x74\x68\x65\x20\x6C\x65\x76\x65\x6C\x20\x6F\x66\x20\x74\x68\x65\x20\x74\x61\x72\x67\x65\x74\x65\x64\x20\x63\x72\x65\x61\x74\x75\x72\x65\x2E"),
            (DAT, 0x48DE, b"\x31\x30\x25\x20\x66\x6F\x72\x20\x65\x76\x65\x72\x79\x20\x6E\x20\x68\x65\x72\x6F\x20\x6C\x65\x76\x65\x6C\x73\x2C\x20\x77\x68\x65\x72\x65\x20\x6E\x20\x69\x73\x20\x74\x68\x65\x20\x6C\x65\x76\x65\x6C\x20\x6F\x66\x20\x74\x68\x65\x20\x74\x61\x72\x67\x65\x74\x65\x64\x20\x63\x72\x65\x61\x74\x75\x72\x65\x2E"),
            #astra below
            (DAT, 0x4BB6, b"\x31\x30\x25\x20\x66\x6F\x72\x20\x65\x76\x65\x72\x79\x20\x6E\x20\x68\x65\x72\x6F\x20\x6C\x65\x76\x65\x6C\x73\x2C\x20\x77\x68\x65\x72\x65\x20\x6E\x20\x69\x73\x20\x74\x68\x65\x20\x6C\x65\x76\x65\x6C\x20\x6F\x66\x20\x74\x68\x65\x20\x74\x61\x72\x67\x65\x74\x65\x64\x20\x63\x72\x65\x61\x74\x75\x72\x65\x2E"),            
            (DAT, 0x4E5C, b"\x31\x30\x25\x20\x66\x6F\x72\x20\x65\x76\x65\x72\x79\x20\x6E\x20\x68\x65\x72\x6F\x20\x6C\x65\x76\x65\x6C\x73\x2C\x20\x77\x68\x65\x72\x65\x20\x6E\x20\x69\x73\x20\x74\x68\x65\x20\x6C\x65\x76\x65\x6C\x20\x6F\x66\x20\x74\x68\x65\x20\x74\x61\x72\x67\x65\x74\x65\x64\x20\x63\x72\x65\x61\x74\x75\x72\x65\x2E"),
            (DAT, 0x8627, b"\x31\x30\x25\x20\x66\x6F\x72\x20\x65\x76\x65\x72\x79\x20\x6E\x20\x68\x65\x72\x6F\x20\x6C\x65\x76\x65\x6C\x73\x2C\x20\x77\x68\x65\x72\x65\x20\x6E\x20\x69\x73\x20\x74\x68\x65\x20\x6C\x65\x76\x65\x6C\x20\x6F\x66\x20\x74\x68\x65\x20\x74\x61\x72\x67\x65\x74\x65\x64\x20\x63\x72\x65\x61\x74\x75\x72\x65\x2E"),
            (DAT, 0x8937, b"\x31\x30\x25\x20\x66\x6F\x72\x20\x65\x76\x65\x72\x79\x20\x6E\x20\x68\x65\x72\x6F\x20\x6C\x65\x76\x65\x6C\x73\x2C\x20\x77\x68\x65\x72\x65\x20\x6E\x20\x69\x73\x20\x74\x68\x65\x20\x6C\x65\x76\x65\x6C\x20\x6F\x66\x20\x74\x68\x65\x20\x74\x61\x72\x67\x65\x74\x65\x64\x20\x63\x72\x65\x61\x74\x75\x72\x65\x2E"),
            (DAT, 0x8BF2, b"\x31\x30\x25\x20\x66\x6F\x72\x20\x65\x76\x65\x72\x79\x20\x6E\x20\x68\x65\x72\x6F\x20\x6C\x65\x76\x65\x6C\x73\x2C\x20\x77\x68\x65\x72\x65\x20\x6E\x20\x69\x73\x20\x74\x68\x65\x20\x6C\x65\x76\x65\x6C\x20\x6F\x66\x20\x74\x68\x65\x20\x74\x61\x72\x67\x65\x74\x65\x64\x20\x63\x72\x65\x61\x74\x75\x72\x65\x2E"),
            (EXE, 0xE6293, b"\xF3"),
            (EXE, 0xE6296, b"\x2A"),
            (EXE, 0xE6359, b"\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x02\x02\x02\x02\x03\x02\x06\x06\x04\x06\x02\x06\x05\x90\x90\x90\x90\x90\x90\x90"),
            (EXE, 0x279cd2, b"\x65"),               
        ],
        True: [
            (DAT, 0x45EC, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (DAT, 0x48DE, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            #astra below
            (DAT, 0x4BB6, b"\x35\x30\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),            
            (DAT, 0x4E5C, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (DAT, 0x8627, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (DAT, 0x8937, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (DAT, 0x8BF2, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (EXE, 0xE6293, b"\xF5"),
            (EXE, 0xE6296, b"\x2F"),
            (EXE, 0xE6359, b"\x00\x00\x06\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\x06\x06\x06\x06\x06\x01\x00\x00\x00\x00\x00\x02\x02\x02\x02\x03\x02\x06\x06\x04\x06\x02\x06\x05\x00\x06\x06\x06\x00"),
            (EXE, 0x279cd2, b"\x50"),               
        ],
    },
}

HEX_PL = {
    "COTUK": {
        True: [
            (EXE, 0x0E3F33, b"\x38"),
            (EXE, 0x0E3F2A, b"\x3a"),
            (EXE, 0x0E3F1F, b"\x3D"),
            (DAT, 0x1B612, b'\x7A\x61\x61\x77\x61\x6E\x73\x6F\x77\x6E\x79\x6D\x20\x77\x73\x6B\x72\x7A\x65\x73\x7A\x6F\x6E\x65\x20\x7A\x6F\x73\x74\x61\x6E\xB9\x20\x7A\x6F\x6D\x62\x69\x65\x2C\x20\x61\x20\x6E\x61\x20\x6D\x69\x73\x74\x72\x7A\x6F\x77\x73\x6B\x69\x6D\x20\x75\x70\x69\x6F\x72\x79\x2E\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20'),
            (EXE, 0x260B86, b"\x74\x73"),
        ],
        False: [
            (EXE, 0x0E3F33, b"\x3a"),
            (EXE, 0x0E3F2A, b"\x3c"),
            (EXE, 0x0E3F1F, b"\x40"),
            (DAT, 0x1B612, b'\x50\x6F\x64\x73\x74\x61\x77\x6F\x77\x79\x6D\x20\x77\x73\x6B\x72\x7A\x65\x73\x7A\x6F\x6E\x65\x20\x7A\x6F\x73\x74\x61\x6E\xB9\x20\x7A\x6F\x6D\x62\x69\x65\x2C\x20\x6E\x61\x20\x7A\x61\x61\x77\x61\x6E\x73\x6F\x77\x61\x6E\x79\x6D\x20\x75\x70\x69\x6F\x72\x79\x2C\x20\x61\x20\x6E\x61\x20\x6D\x69\x73\x74\x72\x7A\x6F\x77\x73\x6B\x69\x6D\x20\x6C\x69\x73\x7A\x65\x2E'),
            (EXE, 0x260B86, b"\x50\x50"),
        ],
    },
    "Astra": {
        "default": [
            (DAT, 0x4f2a, b"\x32"),
            (DAT, 0x4f39, b"\x32"),
            (DAT, 0x2e442, b"\x32"),
            (DAT, 0x2e768, b"\x32"),
        ],
        "legacy": [
            (DAT, 0x4f2a, b"\x50"),
            (DAT, 0x4f39, b"\x50"),
            (DAT, 0x2e442, b"\x50"),
            (DAT, 0x2e768, b"\x50"),
        ],
    },
    "Agar": {
        "default": [
            (DAT, 0x2E53C, b"\x39"),
            (DAT, 0x2E867, b"\x39"),
        ],
        "legacy": [
            (DAT, 0x2E53C, b"\x50"),
            (DAT, 0x2E867, b"\x50"),
        ],
    },
    "Wrathmont": {
        "default": [
            (DAT, 0x2E554, b"\x31"),
            (DAT, 0x2E87F, b"\x31"),
        ],
        "legacy": [
            (DAT, 0x2E554, b"\x50"),
            (DAT, 0x2E87F, b"\x50"),
            
        ],
    },
    "Ranloo": {
        "default": [
            (DAT, 0x62C9, b"\x44\x58"),
            (DAT, 0x62DA, b"\x44\x58"),
            (DAT, 0x2E49B, b"\x44\x58"),
            (DAT, 0x2E7C6, b"\x44\x58"),
        ],
        "legacy": [
            (DAT, 0x62C9, b"\x50\x50"),
            (DAT, 0x62DA, b"\x50\x50"),
            (DAT, 0x2E49B, b"\x50\x50"),
            (DAT, 0x2E7C6, b"\x50\x50"),
        ],
    },
    "UniqueStartingArmies": {
        False: [
            (EXE, 0x27F159, b"\x69"),
#tyris
            (EXE, 0x27a07c, b"\x02"),
#ingham
            (EXE, 0x27a248, b"\x02"),
#sorsha
            (EXE, 0x279Fc4, b"\x02"),
#clancy
            (EXE, 0x27a5e0, b"\x10"),
#ryland
            (EXE, 0x27a4cc, b"\x10"),
#aeris
            (EXE, 0x27a91c, b"\x10"),
#Iona
            (EXE, 0x27abfc, b"\x1E"),
#thane
            (EXE, 0x27d550, b"\x1E"),
#fafner
            (EXE, 0x27ab44, b"\x1E"),
#fafner
            (EXE, 0x27ab44, b"\x1E"),
#theodorus            
            (EXE, 0x27adc8, b"\x1E"),
#rashka
            (EXE, 0x27af94, b"\x2C"),
#nymus
            (EXE, 0x27B1BC, b"\x2C"),
#marius
            (EXE, 0x27AFF0, b"\x2C"),
#vokial
            (EXE, 0x27B554, b"\x3A"),
#moandor
            (EXE, 0x27B5B0, b"\x3A"),
#tamika
            (EXE, 0x27B668, b"\x3A"),
#dace
            (EXE, 0x27BB70, b"\x48"),
#synca
            (EXE, 0x27BCE0, b"\x48"),
#yog
            (EXE, 0x27C078, b"\x56"),
#shiva
            (EXE, 0x27C18C, b"\x56"),
#krellion
            (EXE, 0x27C244, b"\x56"),
#vey
            (EXE, 0x27C3B4, b"\x56"),
#alkin
            (EXE, 0x27C7A8, b"\x64"),
#broghild
            (EXE, 0x27C8BC, b"\x64"),        
#casmetra false
            (DAT, 0x3F43, b"\x9B\x00\x00\x00\x9D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x06\x00\x00\x00\x09"),
#tancred false
            (DAT, 0x7181, b"\xAC\x00\x00\x00\xAE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x07\x00\x00\x00\x09"),   
#Agar false
            (DAT, 0x8913, b"\xAC\x00\x00\x00\xAE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x07\x00\x00\x00\x09"),   
            ],
        True: [
            (EXE, 0x27F159, b"\x50"),
#tyris
            (EXE, 0x27a07c, b"\x0A"),
#ingham
            (EXE, 0x27a248, b"\x08"),
#sorsha
            (EXE, 0x279Fc4, b"\x06"),
#clancy
            (EXE, 0x27a5e0, b"\x18"),
#ryland
            (EXE, 0x27a4cc, b"\x16"),
#aeris
            (EXE, 0x27a91c, b"\x14"),
#Iona
            (EXE, 0x27abfc, b"\x24"),
#thane
            (EXE, 0x27d550, b"\x24"),
#fafner
            (EXE, 0x27ab44, b"\x26"),
#theodorus            
            (EXE, 0x27adc8, b"\x22"),
#rashka
            (EXE, 0x27af94, b"\x34"),
#nymus
            (EXE, 0x27B1BC, b"\x32"),
#marius
            (EXE, 0x27AFF0, b"\x30"),
#vokial
            (EXE, 0x27B554, b"\x3e"),
#moandor
            (EXE, 0x27B5B0, b"\x40"),
#tamika
            (EXE, 0x27B668, b"\x42"),
#dace
            (EXE, 0x27BB70, b"\x4e"),
#synca
            (EXE, 0x27BCE0, b"\x50"),
#yog
            (EXE, 0x27C078, b"\x5e"),
#shiva
            (EXE, 0x27C18C, b"\x5c"),
#krellion
            (EXE, 0x27C244, b"\x5a"),
#vey
            (EXE, 0x27C3B4, b"\x5a"),
#alkin
            (EXE, 0x27C7A8, b"\x66"),
#broghild
            (EXE, 0x27C8BC, b"\x6c"),
#casmetra true
            (DAT, 0x3F43, b"\xA1\x00\x00\x00\x9D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x02\x00\x00\x00\x03"),
#tancred true
            (DAT, 0x7181, b"\xB4\x00\x00\x00\xAE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x01\x00\x00\x00\x01"),
#Agar true
            (DAT, 0x8913, b"\xB2\x00\x00\x00\xAE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x19\x00\x00\x00\x02\x00\x00\x00\x03"),
            ],
    },        
    "StaticSpellSpecialties": {
        False: [
            (DAT, 0x2937, b"\x31\x30\x25\x20\x7A\x61\x20\x6B\x61\xBF\x64\x79\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x62\x6F\x68\x61\x74\x65\x72\x61\x2E\x20\x50\x72\x65\x6D\x69\x61\x20\x64\x7A\x69\x65\x6C\x6F\x6E\x61\x20\x6A\x65\x73\x74\x20\x70\x72\x7A\x65\x7A\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x61\x74\x61\x6B\x6F\x77\x61\x6E\x65\x6A\x20\x6A\x65\x64\x6E\x6F\x73\x74\x6B\x69\x2E"),
            (DAT, 0x4C46, b"\x31\x30\x25\x20\x7A\x61\x20\x6B\x61\xBF\x64\x79\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x62\x6F\x68\x61\x74\x65\x72\x61\x2E\x20\x50\x72\x65\x6D\x69\x61\x20\x64\x7A\x69\x65\x6C\x6F\x6E\x61\x20\x6A\x65\x73\x74\x20\x70\x72\x7A\x65\x7A\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x61\x74\x61\x6B\x6F\x77\x61\x6E\x65\x6A\x20\x6A\x65\x64\x6E\x6F\x73\x74\x6B\x69\x2E"),
            #astra below
            (DAT, 0x4FC8, b"\x31\x30\x25\x20\x7A\x61\x20\x6B\x61\xBF\x64\x79\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x62\x6F\x68\x61\x74\x65\x72\x61\x2E\x20\x50\x72\x65\x6D\x69\x61\x20\x64\x7A\x69\x65\x6C\x6F\x6E\x61\x20\x6A\x65\x73\x74\x20\x70\x72\x7A\x65\x7A\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x61\x74\x61\x6B\x6F\x77\x61\x6E\x65\x6A\x20\x6A\x65\x64\x6E\x6F\x73\x74\x6B\x69\x2E"),            
            (DAT, 0x52A5, b"\x31\x30\x25\x20\x7A\x61\x20\x6B\x61\xBF\x64\x79\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x62\x6F\x68\x61\x74\x65\x72\x61\x2E\x20\x50\x72\x65\x6D\x69\x61\x20\x64\x7A\x69\x65\x6C\x6F\x6E\x61\x20\x6A\x65\x73\x74\x20\x70\x72\x7A\x65\x7A\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x61\x74\x61\x6B\x6F\x77\x61\x6E\x65\x6A\x20\x6A\x65\x64\x6E\x6F\x73\x74\x6B\x69\x2E"),
            (DAT, 0x8CAF, b"\x31\x30\x25\x20\x7A\x61\x20\x6B\x61\xBF\x64\x79\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x62\x6F\x68\x61\x74\x65\x72\x61\x2E\x20\x50\x72\x65\x6D\x69\x61\x20\x64\x7A\x69\x65\x6C\x6F\x6E\x61\x20\x6A\x65\x73\x74\x20\x70\x72\x7A\x65\x7A\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x61\x74\x61\x6B\x6F\x77\x61\x6E\x65\x6A\x20\x6A\x65\x64\x6E\x6F\x73\x74\x6B\x69\x2E"),
            (DAT, 0x9004, b"\x31\x30\x25\x20\x7A\x61\x20\x6B\x61\xBF\x64\x79\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x62\x6F\x68\x61\x74\x65\x72\x61\x2E\x20\x50\x72\x65\x6D\x69\x61\x20\x64\x7A\x69\x65\x6C\x6F\x6E\x61\x20\x6A\x65\x73\x74\x20\x70\x72\x7A\x65\x7A\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x61\x74\x61\x6B\x6F\x77\x61\x6E\x65\x6A\x20\x6A\x65\x64\x6E\x6F\x73\x74\x6B\x69\x2E"),
            (DAT, 0x9308, b"\x31\x30\x25\x20\x7A\x61\x20\x6B\x61\xBF\x64\x79\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x62\x6F\x68\x61\x74\x65\x72\x61\x2E\x20\x50\x72\x65\x6D\x69\x61\x20\x64\x7A\x69\x65\x6C\x6F\x6E\x61\x20\x6A\x65\x73\x74\x20\x70\x72\x7A\x65\x7A\x20\x70\x6F\x7A\x69\x6F\x6D\x20\x61\x74\x61\x6B\x6F\x77\x61\x6E\x65\x6A\x20\x6A\x65\x64\x6E\x6F\x73\x74\x6B\x69\x2E"),
            (EXE, 0xE6293, b"\xF3"),
            (EXE, 0xE6296, b"\x2A"),
            (EXE, 0xE6359, b"\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x06\x02\x02\x02\x02\x03\x02\x06\x06\x04\x06\x02\x06\x05\x90\x90\x90\x90\x90\x90\x90"),
            (EXE, 0x279cd2, b"\x65"),               
        ],
        True: [
            (DAT, 0x2937, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (DAT, 0x4C46, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            #astra below
            (DAT, 0x4FC8, b"\x35\x30\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),            
            (DAT, 0x52A5, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (DAT, 0x8CAF, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (DAT, 0x9004, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (DAT, 0x9308, b"\x32\x35\x25\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            (EXE, 0xE6293, b"\xF5"),
            (EXE, 0xE6296, b"\x2F"),
            (EXE, 0xE6359, b"\x00\x00\x06\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\x06\x06\x06\x06\x06\x01\x00\x00\x00\x00\x00\x02\x02\x02\x02\x03\x02\x06\x06\x04\x06\x02\x06\x05\x00\x06\x06\x06\x00"),
            (EXE, 0x279cd2, b"\x50"),               
        ],
    },
}


HEX_ES = {}


# Read the INI file. 
config = configparser.ConfigParser()
config.optionxform = str  # preserve original key casing
config.read(ini_path)
if 'Optional features' in config:
    features = config['Optional features']
else:
    features = config['Optional features'] = {}
    print("Warning: [Optional features] section was missing, added empty one.")
if 'Skins' in config:
    skins = config['Skins']
else:
    skins = config['Skins'] = {}
    print("Warning: [Skins] section was missing, added empty one.")
if 'HexSwapper' in config:
    main = config['HexSwapper']
else:
    main = config['HexSwapper'] = {}
    print("Warning: [HexSwapper] section was missing, added empty one.")
    
    
    
language_local = main.get('Language', fallback='english')
if language_local == 'english':
    extra_hex = HEX_EN
elif language_local == 'polish':
    extra_hex = HEX_PL
else:
    hota_ini_path = os.path.join(script_dir, 'HotA_Settings.ini')
    config.read(hota_ini_path)
    if 'Global Settings' in config:
        hota_ini = config['Global Settings']
        language = hota_ini.get('Language', fallback=0)
        extra_hex = HEX_EN
    else: 
        language = 0
        extra_hex = HEX_EN

    if language == 2: 
        extra_hex = HEX_PL
    else: 
        extra_hex = HEX_EN    

INSTALLED = main.get('Installed', fallback= None)

#HD DLL stuff
original_text = b"\x4F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x20\x69\x73\x20\x70\x61\x72\x74\x20\x6F\x66\x20\x74\x68\x65\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x48\x6F\x74\x41\x20\x43\x72\x65\x77"
new_text = b"\x4F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x20\x69\x73\x20\x70\x61\x72\x74\x20\x6F\x66\x20\x74\x68\x65\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x48\x6F\x74\x41\x20\x43\x72\x65\x77\x20\x68\x61\x73\x20\x7B\x6E\x6F\x74\x68\x69\x6E\x67\x7D\x20\x74\x6F\x20\x64\x6F\x20\x77\x69\x74\x68\x20\x74\x68\x65\x20\x6F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x2E\x0A\x0A\x48\x6F\x74\x41\x20\x69\x73\x20\x61\x20\x6E\x6F\x6E\x2D\x70\x72\x6F\x66\x69\x74\x20\x70\x72\x6F\x6A\x65\x63\x74\x2C\x20\x61\x6E\x64\x20\x74\x68\x65\x79\x20\x68\x61\x76\x65\x6E\x27\x74\x20\x61\x63\x63\x65\x70\x74\x65\x64\x20\x61\x6E\x79\x20\x64\x6F\x6E\x61\x74\x69\x6F\x6E\x73\x20\x6F\x76\x65\x72\x20\x31\x36\x20\x79\x65\x61\x72\x73\x20\x6F\x66\x20\x64\x65\x76\x65\x6C\x6F\x70\x6D\x65\x6E\x74\x2E\x20\x42\x79\x20\x73\x75\x70\x70\x6F\x72\x74\x69\x6E\x67\x20\x74\x68\x65\x20\x6C\x6F\x62\x62\x79\x20\x79\x6F\x75\x20\x73\x75\x70\x70\x6F\x72\x74\x20\x74\x68\x65\x20\x63\x72\x65\x61\x74\x6F\x72\x20\x6F\x66\x20\x48\x6F\x4D\x4D\x33\x20\x48\x44\x2B\x2C\x20\x6E\x6F\x74\x20\x74\x68\x65\x20\x48\x6F\x74\x41\x20\x70\x72\x6F\x6A\x65\x63\x74\x2E\x0A\x0A\x0A\x0A\x16\x18\x43\x73\x41\x72\x4F\x73\x7D\x3A\x0A\x7B\x50\x75\x6D\x70\x6B\x69\x6E\x7D\x20\x7B\x50\x61\x74\x63\x68\x7D\x20\x69\x73\x20\x63\x6F\x6D\x70\x61\x74\x69\x62\x6C\x65\x20\x77\x69\x74\x68\x20\x74\x68\x65\x20\x6F\x6E\x6C\x69\x6E\x65\x20\x6C\x6F\x62\x62\x79\x2C\x20\x62\x75\x74\x20\x69\x74\x20\x69\x73\x20\x6E\x6F\x74\x20\x61\x64\x76\x69\x73\x65\x64\x20\x6E\x74\x6F\x20\x70\x6C\x61\x79\x20\x61\x6E\x79\x20\x72\x61\x6E\x6B\x65\x64\x20\x67\x61\x6D\x65\x73\x2E\x20\x49\x6E\x20\x63\x61\x73\x65\x20\x6F\x66\x20\x61\x6E\x79\x20\x69\x73\x73\x75\x65\x73\x2C\x20\x76\x69\x73\x69\x74\x20\x74\x68\x65\x20\x50\x75\x6D\x70\x6B\x69\x6E\x20\x50\x61\x74\x63\x68\x20\x44\x69\x73\x63\x6F\x72\x64\x20\x73\x65\x72\x76\x65\x72\x2E"


data_dir = os.path.join(script_dir, "Data")
mod_dir = os.path.join(script_dir, "Pumpkin Patch.zip")
PL_dir = os.path.join(script_dir, "Polish version.zip")



HEX |= extra_hex

def list_templates_and_names():
    global script_dir
    if not os.path.isfile(os.path.join(script_dir, "HotA_RMGTemplates")):
        templates, template_names = []
        return templates, template_names
    else: 
        directory = os.path.join(script_dir, "HotA_RMGTemplates")
    templates = [
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]
    template_names = [os.path.splitext(t)[0] for t in templates]
    return templates, template_names

def apply(name, state):
    patches = HEX.get(name, {})
    if not patches:
        logging.warning("Unknown key in INI: %s", name)
        return

    entries = patches.get(state, [])
    if not entries:
        logging.warning("No entries found for state '%s' in key '%s'", state, name)
        return

    if name.lower() == 'zenith':
        un32 = find_hex(hd_dll, b"\x75\x6E\x33") 
        if un32 == []:
            un32 = find_hex(hd_dll, b"\x55\x4E\x33") 
        
        un44 = find_hex(hd_dll, b"\x75\x6E\x34") 
        if un44 == []:
            un44 = find_hex(hd_dll, b"\x55\x4E\x34") 
            
        if not un44 ==[] and not un32 ==[]:
            offset32 = un32[0] + 3                
            offset44 = un44[0] + 3

            if state:
                swaphex(hd_dll, offset32, b"\x50")
                swaphex(hd_dll, offset44, b"\x50")
            else:
                swaphex(hd_dll, offset32, b"\x32")
                swaphex(hd_dll, offset44, b"\x34")            

    # Check if the first entry indicates a file swap patch
    if isinstance(entries[0], tuple) and entries[0][0] == 'file':
        for internalcategory, skinname in entries:
            move_file(state, skinname)
    elif isinstance(entries[0], tuple) and entries[0][0] == 'delete':
        for internalcategory, filename in entries:
            delete_file(filename)
    else:
        for target, offset, data in entries:
            swaphex(target, offset, data)

#apply("MKC", False)

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
            return lower_val  # Return lowercase string for custom states

def get_valid_states(key):
    patch_dict = HEX.get(key, {})
    return list(patch_dict.keys())

current_states = {}

def get_initial_state(name, category):
    value = category.get(name)
    if value is None:
        value = get_valid_states(name)[0]
        return value
    converted = convert_value(value)
    valid_states = HEX.get(name, {}).keys()
    return converted if converted in valid_states else None

def reset_ini():
    # Write updated config
    with open(ini_path, 'w') as configfile:
        config.write(configfile)

    for btn_list, category_name in [
            (BUTTONS_Gameplay, "Optional features"),
            (BUTTONS_Skins, "Skins"),
            (BUTTONS_Skins2, "Skins"),
            ]:
        for b in btn_list:
            name = b['name']
            b['valid_states'] = list(HEX.get(name, {}).keys())
            b['current_state'] = get_initial_state(name, b['category'])

def is_exe_open():
    game_exe = os.path.join(script_dir, EXE)
    for proc in psutil.process_iter(['exe']):
        try:
            if proc.info['exe'] and os.path.normcase(proc.info['exe']) == game_exe:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


x_pos_list = (70, 150, 230, 310, 390, 470, 70, 150, 230, 310, 390, 470, 70, 150, 230, 310, 390, 470, 70, 150, 230, 310, 390, 470, 70, 150, 230, 310)
y_pos_list = (151, 151, 151, 151, 151, 151, 237, 237, 237, 237, 237, 237, 323, 323, 323, 323, 323, 323, 409, 409, 409, 409, 409, 409, 495, 495, 495, 495)

x_pos_list_2 = (56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 314, 314, 314, 314, 314, 314, 314, 314, 314, 314, 314)
y_pos_list_2 = (144, 188, 232, 276, 320, 364, 408, 452, 496, 540, 144, 188, 232, 276, 320, 364, 408, 452, 496, 540)


BUTTONS_HexMenu = [
    {'name': 'Home', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (615, 25), 'description': "Heroes 3 Wiki"},
    {'name': 'MenuGameplay', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (587, 142), 'description': "Gameplay Menu"},
    {'name': 'MenuSkins', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (620, 257), 'description': "Skins Menu"},
    {'name': 'Reset', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (622, 365), 'description': "Reset all options to their default values. \n\nTakes a few seconds to load."},
    {'name': 'Play', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (625, 477), 'description': "Close the HexSwapper and play!"},
]

BUTTONS_HOME = [
    {'name': 'Wiki2', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (465, 455), 'description': "Full Changelog"},
    {'name': 'Wiki', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (76, 519), 'description': "Heroes 3 Wiki"},
    {'name': 'Feedback', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (75, 541), 'description': "Feedback Form"},   
    {'name': 'Coffee', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (236, 529), 'description': "You can buy me a coffee here"},   
    {'name': 'Discord', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (429, 520), 'description': "Discord: Pumpkin Patch server"},
    {'name': 'Youtube', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (429, 543), 'description': "Youtube: CsArOs"},   
    {'name': '-Wiki', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (96, 520), 'description': "Heroes 3 Wiki"},
    {'name': '-Discord', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (450, 520), 'description': "Discord: Pumpkin Patch server"},
    {'name': '-Youtube', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (449, 542), 'description': "Youtube: CsArOs"},   
    {'name': '-Feedback', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (96, 542), 'description': "Feedback Form"},   
    {'name': '-Coffee', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (257, 532), 'description': "You can buy me a coffee here"},   
    {'name': 'LinkTree', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (250, 492), 'description': "Youtube: CsArOs"},   
]

BUTTONS_Gameplay = [
    {'name': 'MaximumLuck4', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Maximum Luck of heroes and creatures is +4, \nwhich corresponds to 16.6% for a Lucky Strike."},
    {'name': 'RefuseLevelUp', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Upon Leveling up, the player may skip the choice of the new skill."},
    {'name': 'XPcalc', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "XP is a function of AI value / 12, instead of the enemy HP."},
    {'name': 'BalancedOldHillFort', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Old Hill fort will upgrade level 5-7 units \nfor a higher price."},
    {'name': 'COTUK', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Cloak of the Undead King summons Wraiths, instead of Liches."},
    {'name': 'Gwenneth_gameplay', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Switch between Gwenneth and Sanya being available by default on random maps."},
    {'name': 'Winstan', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Switch between Winstan and Thane being available by default on random maps."},
    {'name': 'Athe', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Switch between Athe and Olema being available by default on random maps."},
    {'name': 'Archibald', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Switch between Archibald and Jeddite being available by default on random maps."},
    {'name': 'Zenith', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Switch between Zenith and Straker."},
    {'name': 'FlyingFamiliars', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Allows familiars to fly, but increases their price by 10."},
    {'name': 'RegeneratingChaosHydra', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Chaos Hydras regenerate 25 hp per turn, but their speed is only 7 and their price is 4000."},
    {'name': 'StaticSpellSpecialties', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Changes the specialties of almost all mages to instead be a static 25% bonus."},
    {'name': 'UniqueStartingArmies', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "All heroes start with units they specialize in."},
    {'name': 'PrimaryStatsIncreaseIsConstant', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Primary stat increase for each hero class does not change after level 10."},
    {'name': 'CompleteSpellRedesign', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Alters the level and mana cost of almost all spells. \nMoreover, alters the cost of the resource silo. "},
    {'name': 'UnpredictableGenies', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Genies can cast any positive spell, ignoring all targetting rules. \nThey may also cast Implosion."},
    {'name': '1hero', 'category': features, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Reduces the limit of heroes an AI player can recruit to 1, regardless of difficulty. \nMoreover, increases the default scouting radius by 2, and lets you see enemy heroes with basic View Air. \nPerfect for practicing 1-hero templates against an AI opponent."},
]

BUTTONS_Skins = [
    {'name': 'Edric', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Edric"},
    {'name': 'LordHaart', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Lord Haart"},
    {'name': 'CatherineReplacesSorsha', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Sorsha / Catherine"},
    {'name': 'Christian', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Christian"},
    {'name': 'Tyris', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Tyris"},
    {'name': 'Roland', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Roland"},
    
    {'name': 'Rion', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Rion"},
    {'name': 'Adelaide', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Adelaide"},
    {'name': 'Gwenneth', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Gwenneth"},
    {'name': 'Mephala', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Mephala"},
    {'name': 'Jenova', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Jenova"},
    {'name': 'Ivor', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Ivor"},
    
    {'name': 'Clancy', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Clancy"},
    {'name': 'Gelu', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Gelu"},
    {'name': 'Gem', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Gem"},
    {'name': 'Josephine', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Josephine"},
    {'name': 'Iona', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Iona"},
    {'name': 'Halon', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Halon"},

    {'name': 'Theodorus', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Theodorus"},    
    {'name': 'Solmyr', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Solmyr"},
    {'name': 'Dracon', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Dracon"},
    {'name': 'Fiona', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Fiona"},
    {'name': 'Rashka', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Rashka"},
    {'name': 'Nymus', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Nymus"},

    {'name': 'Xyron', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Xyron"},    
    {'name': 'Zydar', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Zydar"},
    {'name': 'Moandor', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Moandor"},
    {'name': 'Charna', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Charna"},

    {'name': 'Arrow_right', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (470, 511), 'description': "Turn the page"},
]

BUTTONS_Skins2 = [  
    {'name': 'Tamika', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Tamika"},
    {'name': 'Ranloo', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Ranloo"},
    {'name': 'Sandro', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Sandro"},
    {'name': 'Thant', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Thant"},
    {'name': 'Vidomina', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Vidomina"},
    {'name': 'Gunnar', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Gunnar"},

    {'name': 'Mutare', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Mutare (Drake)"},     
    {'name': 'Alamar', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Alamar"},
    {'name': 'Deemer', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Deemer"},
    {'name': 'Jeddite', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Jeddite"},
    {'name': 'Sephinroth', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Sephinroth"},
    {'name': 'Darkstorn', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Darkstorn"},
    {'name': 'Yog', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Yog"},
    
    {'name': 'Shiva', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Shiva"},
    {'name': 'CragHack', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Crag Hack"},
    {'name': 'Gundula', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Gundula"},
    {'name': 'Bron', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Bron"},
    {'name': 'Drakon', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Drakon"},
    {'name': 'Tazar', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Tazar"}, 
    
    {'name': 'Wystan', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Wystan"}, 
    {'name': 'Monere', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Monere"},
    {'name': 'Erdamon', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Erdamon"},
    {'name': 'Luna', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Luna"},
    {'name': 'Ciele', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Ciele"},
    {'name': 'Astra', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Astra"}, 
    
    {'name': 'Wrathmont', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Wrathmont"},
    {'name': 'Agar', 'category': skins, 'current_state': None, 'button': None, 'valid_states': None, 'description': "Agar"},
    
    {'name': 'Arrow_left', 'category': main, 'current_state': None, 'button': None, 'valid_states': None, 'pos': (390, 511), 'description': "Turn the page"},
]

def update_templates():
    global script_dir
    PASScode = 500000
    for i, g in enumerate(BUTTONS_Gameplay):
        name = g['name']
        g['valid_states'] = list(HEX.get(name, {}).keys())
        if g['current_state'] == None:
            g['current_state'] = get_initial_state(g['name'], g['category'])

        if g['current_state'] == True:
            PASScode = PASScode + 2 ** i
    PASSWORD = str(PASScode)
    bytePASS = PASSWORD.encode('ASCII')
    if not os.path.isfile(os.path.join(script_dir, "HotA_RMGTemplates")):
        return
    templates, name_list = list_templates_and_names()
    for i, tmpl in enumerate(templates):
        tmpl_dir = os.path.join(script_dir, "HotA_RMGTemplates", tmpl)
        name = name_list[i]
        bytename = name.encode('ASCII')
        tmpl_offset = find_hex(tmpl, bytename, tmpl_dir, default_0=True)
        if tmpl_offset == []:
            name = name.lower()
            bytename = name.encode('ASCII')
            tmpl_offset = find_hex(tmpl_dir, bytename, default_0=True)

        if len(tmpl_offset) >= 1:
            offset = tmpl_offset[0] + len(name) + 2
            swaphex(tmpl, offset, bytePASS, tmpl_dir)
        else:
            logging.error(name, "misses its own title")
    logging.info("templates patched") 


def make_button_callback(btn_dict, script_dir):
    def callback():
        if INSTALLED == "False" or INSTALLED == "false" or INSTALLED == False:
            return
        if is_exe_open():
            messagebox.showinfo("Error!", "The game is open! \n\nYou cannot use the HexSwapper to edit the game while it's open!")
            return
        states = btn_dict['valid_states']
        current = btn_dict['current_state']
        try:
            i = states.index(current)
            new_state = states[(i + 1) % len(states)]
        except ValueError:
            new_state = states[0]
        btn_dict['current_state'] = new_state
        apply(btn_dict['name'], new_state)
        update_button_image(btn_dict, script_dir)
        
        if btn_dict['category'] == skins:
            cat = 'Skins'
        elif btn_dict['category'] == main:  
            cat = "HexSwapper"
        else:
            cat = "Optional features"
        
        if btn_dict['category'] == main:
            return callback
        elif btn_dict['category'] == features:
            config.set(cat, btn_dict['name'], str(new_state))
            update_templates()
        else: 
            config.set(cat, btn_dict['name'], str(new_state))
        with open(ini_path, 'w') as configfile:
            config.write(configfile)
    return callback

def update_button_image(btn_dict, script_dir, suffix=""):
    name = btn_dict['name']
    state = str(btn_dict.get('current_state', 'default')).lower()
    
    if btn_dict['category'] == features:
        if btn_dict['name'] in ['Zenith', 'Archibald', 'Gwenneth_gameplay', 'Winstan', 'Athe']:
            filename = f"{name}_{state}{suffix}.png"
        else: 
            filename = f"{state}{suffix}.png"
    elif btn_dict['category'] == main:
        filename = f"{name}{suffix}.png"
    else:
        filename = f"{name}_{state}{suffix}.png"

    image_path = os.path.join(icons_dir, filename)

    if not os.path.isfile(image_path):
        if suffix != "":
            return update_button_image(btn_dict, script_dir, suffix="")
        else:
            btn_dict['button'].config(text=f"{name}", image='', compound='none')
            return

    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)
    btn_dict['image'] = photo  # prevent garbage
    btn_dict['button'].config(image=photo, text="", compound="center")
    
    
bgRGB = "#724826"
bg2RGB = "#505050"
bg3RGB = "#f7de7b"


class HexSwapper:
    def __init__(self, root):
        global script_dir
        self.root = root
        self.root.title("HexSwapper")
        self.root.resizable(False, False)

        if getattr(sys, 'frozen', False):
            # Running as .exe (frozen by PyInstaller)
            icon_path = os.path.join(os.path.dirname(sys.executable), "pp_icon.png")
        else:
            # Running as .py script
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pp_icon.png")

        if os.path.exists(icon_path):
            img = ImageTk.PhotoImage(Image.open(icon_path))
            self.root.iconphoto(False, img)
        elif os.path.exists(os.path.join(script_dir, "pp_icon.png")):
            img = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "pp_icon.png")))
            self.root.iconphoto(False, img)
        else:
            pass

        image1_path = os.path.join(icons_dir, "HexSwapper.png")
        image1 = Image.open(image1_path)
        self.bg_photo1 = ImageTk.PhotoImage(image1)
        self.canvas = tk.Canvas(root, width=self.bg_photo1.width(), height=self.bg_photo1.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.bg_photo1, anchor="nw")

        self.all_buttons = []
        self.menu_state = None
        
        self.overlay_image_id = None  # Track canvas image ID for overlay
        self.init_menu_button()
        self.update_menu_state()
        self.tooltip_popup = None
                                
        for btn_list, category_name in [
                (BUTTONS_Gameplay, "Optional features"),
                (BUTTONS_Skins, "Skins"),
                (BUTTONS_Skins2, "Skins"),
                ]:
            for b in btn_list:
                name = b['name']
                b['valid_states'] = list(HEX.get(name, {}).keys())
                b['current_state'] = get_initial_state(name, b['category'])
                
        self.dont_ranked()
        update_templates()
        if is_exe_open():
            messagebox.showwarning("Warning!", "The game is open! \n\nYou cannot use the HexSwapper to edit the game while it's open!")
        apply("Zenith", get_initial_state("Zenith", features))


    def show_description(self, event, btn_dict):
        desc = btn_dict.get('description')

        if self.tooltip_popup is not None:
            self.tooltip_popup.destroy()

        popup = tk.Toplevel(self.root)
        popup.wm_overrideredirect(True)  # Remove window decorations
        popup.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
    
        label = tk.Label(popup, text=desc, bg=bg3RGB, fg="black", relief="solid", borderwidth=1, font=("Sans Serif", 11))
        label.pack(ipadx=5, ipady=3)

        self.tooltip_popup = popup

    def hide_description(self, event=None):
        if self.tooltip_popup:
            self.tooltip_popup.destroy()
            self.tooltip_popup = None
    
    def init_menu_button(self):
        for i, btn in enumerate(BUTTONS_HexMenu):
            name = btn['name']
            btn['valid_states'] = list(HEX.get(name, {}).keys())


            if name.lower() == "menugameplay":
                btn_widget = tk.Button(
                    self.root,
                    command=lambda: self.update_menu_state("gameplay"),
                    bg=bgRGB, 
                    activebackground=bgRGB,
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, bd=0, takefocus=0,
                    fg="black",
                )
                
            elif name.lower() == "menuskins":
                btn_widget = tk.Button(
                    self.root,
                    command=lambda: self.update_menu_state("skins"),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, bd=0, takefocus=0,
                    bg=bgRGB,
                    activebackground=bgRGB
                )
            elif name.lower() == "home":
                btn_widget = tk.Button(
                    self.root,
                    command=lambda: self.update_menu_state("Home"),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, bd=0, takefocus=0,
                    bg=bgRGB,
                    activebackground=bgRGB
                )

                
            elif name.lower() == "reset":
                btn_widget = tk.Button(self.root, command = self.reset_all, borderwidth=0, relief="flat", overrelief="flat", highlightthickness=0, bd=0, takefocus=0, bg=bgRGB, activebackground=bgRGB)
            elif name.lower() in ["discord", "youtube", "wiki", "wiki2", "coffee", "feedback", '-discord', '-youtube', '-wiki', '-coffee', 'linktree']: 
                btn_widget = tk.Button(self.root, command=lambda site=HEX[name]['link'][0]: self.open_website(site), borderwidth=0, relief="flat", overrelief="flat", highlightthickness=0, bd=0, takefocus=0, bg=bg2RGB, activebackground=bg2RGB)
            elif name.lower() == "language": 
                btn_widget = tk.Button(self.root, command = None)
            elif name.lower() == "play": 
                btn_widget = tk.Button(self.root, command = self.game, borderwidth=0, relief="flat", overrelief="flat", highlightthickness=0, bd=0, takefocus=0, bg=bgRGB, activebackground=bgRGB)
            else:
                btn_widget = tk.Button(self.root, command=make_button_callback(btn, script_dir), borderwidth=0, relief="flat", overrelief="flat", highlightthickness=0, takefocus=0, bg=bgRGB, activebackground=bgRGB)
    
            btn['button'] = btn_widget
            btn_widget.bind("<Enter>", lambda e, b=btn: update_button_image(b, script_dir, suffix="_hover"))
            btn_widget.bind("<Leave>", lambda e, b=btn: update_button_image(b, script_dir))

            # Pressed and Released
            btn_widget.bind("<ButtonPress-1>", lambda e, b=btn: update_button_image(b, script_dir, suffix="_press"))
            btn_widget.bind("<ButtonRelease-1>", lambda e, b=btn: update_button_image(b, script_dir, suffix=""))
            btn_widget.bind("<ButtonPress-3>", lambda e, btn=btn: self.show_description(e, btn))
            btn_widget.bind("<ButtonRelease-3>", self.hide_description)
            if btn['category'] == skins:
                x, y = x_pos_list[i], y_pos_list[i]
            elif btn['category'] == features:
                x, y = x_pos_list_2[i], y_pos_list_2[i]
            else:
                x, y = btn['pos']
            btn_widget.place(x=x, y=y)
            update_button_image(btn, script_dir)
            self.all_buttons.append(btn_widget)
        check_for_updates()

         
    def open_website(self, site):
        link = 'https://' + site
        webbrowser.open(link)
    
    
    def reset_all(self):
        for btn_list, category_name in [
            (BUTTONS_Gameplay, "Optional features"),
            (BUTTONS_Skins, "Skins"),
            (BUTTONS_Skins2, "Skins"),
            ]:
            for b in btn_list:
                name = b['name']
                valid_states = b['valid_states'] = list(HEX.get(name, {}).keys())
                default_state = valid_states[0]
                current_state = b['current_state']
                if current_state != default_state:
                    apply(name, default_state)
                    config.set(category_name, name, str(default_state))

        reset_ini()
        self.menu_state = None
        
        self.update_menu_state("Home")

        update_templates()


    def update_menu_state(self, requested_state="Home"):
        if is_exe_open():
            messagebox.showinfo("Error!", "The game is open! \n\nYou cannot use the HexSwapper to edit the game while it's open!")
        requested_state = (requested_state).lower()

        if str(self.menu_state).lower() == requested_state:
            return

        self.menu_state = requested_state

        for btn in self.all_buttons[5:]:
            btn.destroy()
        self.all_buttons = self.all_buttons[:5]

        if self.overlay_image_id:
            self.canvas.delete(self.overlay_image_id)
            self.overlay_image_id = None

        if requested_state == "skins":
            buttons = BUTTONS_Skins
            color = bgRGB
        elif requested_state == "skins2":
            buttons = BUTTONS_Skins2
            color = bgRGB
        elif requested_state == "gameplay":
            buttons = BUTTONS_Gameplay
            color = bgRGB
        else:
            buttons = BUTTONS_HOME
            color = bgRGB

        for i, btn in enumerate(buttons):
            name = btn['name']
            btn['valid_states'] = list(HEX.get(name, {}).keys())
            if btn['current_state'] == None:
                btn['current_state'] = get_initial_state(name, btn['category'])


            if name.lower() == "arrow_right":
                btn_widget = tk.Button(
                    self.root,
                    command=lambda: self.update_menu_state("skins2"),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, takefocus = 0,
                    bg=color,
                    activebackground=color
                    )
                
            elif name.lower() == "arrow_left":
                btn_widget = tk.Button(
                    self.root,
                    command=lambda: self.update_menu_state("skins"),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, takefocus = 0,
                    bg=color,
                    activebackground=color
                    )
            elif name.lower() in ["discord", "youtube", "wiki", "wiki2", "coffee", "feedback", '-discord', '-youtube', '-wiki', '-coffee', 'linktree']: 
                btn_widget = tk.Button(self.root, command=lambda site=HEX[name]['link'][0]: self.open_website(site), borderwidth=0, relief="flat", overrelief="flat", highlightthickness=0, bd=0, takefocus=0, bg=bg2RGB, activebackground=bg2RGB)
            else: 
                btn_widget = tk.Button(
                    self.root,
                    command=make_button_callback(btn, script_dir),
                    borderwidth=0, relief="flat", overrelief="flat",
                    highlightthickness=0, takefocus = 0,
                    bg=color,
                    activebackground=color
                    )

            btn['button'] = btn_widget
            btn_widget.bind("<Enter>", lambda e, b=btn: update_button_image(b, script_dir, suffix="_hover"))
            btn_widget.bind("<Leave>", lambda e, b=btn: update_button_image(b, script_dir))
            btn_widget.bind("<ButtonPress-3>", lambda e, btn=btn: self.show_description(e, btn))
            btn_widget.bind("<ButtonRelease-3>", self.hide_description)
            if btn['category'] == skins:
                x, y = x_pos_list[i], y_pos_list[i]
            elif btn['category'] == features:
                x, y = x_pos_list_2[i], y_pos_list_2[i]
            else:
                x, y = btn['pos']
            btn_widget.place(x=x, y=y)
            btn_widget.place(x=x, y=y)

            update_button_image(btn, script_dir)
            self.all_buttons.append(btn_widget)

        # Optional overlay
        if requested_state == "gameplay":
            overlay = os.path.join(icons_dir, "GameplayOverlay.png")
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(50, 140, image=self.bg_photo2, anchor="nw")
        elif requested_state == "skins":
            overlay = os.path.join(icons_dir, "Arrow_left_false.png")
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(390, 511, image=self.bg_photo2, anchor="nw")
        elif requested_state == "skins2":
            overlay = os.path.join(icons_dir, "Arrow_right_false.png")
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(470, 511, image=self.bg_photo2, anchor="nw")
        else:
            overlay = os.path.join(icons_dir, "Home Overlay.png")
            image2 = Image.open(overlay)
            self.bg_photo2 = ImageTk.PhotoImage(image2)
            self.overlay_image_id = self.canvas.create_image(50, 140, image=self.bg_photo2, anchor="nw")
            

    def dont_ranked(self):
        text_offset = find_hex(hd_dll, original_text, default_0=True)[0]
        path = os.path.join(script_dir, hd_dll)
        if not os.path.isfile(path):
            return
        else: 
            swaphex(hd_dll, text_offset, new_text)

    def game(self):
        if getattr(sys, 'frozen', False):
            # Running as .exe (frozen by PyInstaller)
            game_dir = os.path.dirname(sys.executable)
        else:
            # Running as .py script
            game_dir = os.path.dirname(os.path.abspath(__file__))
        update_templates()
        game_exe = os.path.join(game_dir, EXE)
        if not os.path.exists(game_exe):
            print(f"Game executable not found at: {game_exe}")
            return

        for i in range(3):
            try:
                subprocess.Popen([game_exe], cwd=game_dir)
            except Exception as e:
                print(f"Failed to launch game: {e}")
            self.root.destroy()
            sys.exit()
        self.root.destroy()
        sys.exit()


# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = HexSwapper(root)
    root.mainloop()






