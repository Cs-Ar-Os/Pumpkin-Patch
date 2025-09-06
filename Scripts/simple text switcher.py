# -*- coding: utf-8 -*-
"""
simple text switcher.py

The tool checks directories and sub-directories to find relevant files and edits them by switching "key" for "new_key". 

@author: CsArOs

With a dedication for Aphra
May this tool aid the wiki wizards
"""

import os
import time

file_list = None

def find_files_with_prefix(script_dir, prefix, subfolders = "n"):
    matched_files = []
    if subfolders == "y":
        for root, dirs, files in os.walk(script_dir):
            for name in files:
                full_path = os.path.join(root, name)
                if os.path.isfile(full_path) and name.lower().startswith(prefix.lower()):
                    matched_files.append(full_path)
        return matched_files
    else:
        for name in os.listdir(script_dir):
            full_path = os.path.join(script_dir, name)
            if os.path.isfile(full_path) and name.lower().startswith(prefix.lower()):
                matched_files.append(full_path)
        return matched_files

def find_input(path, key, encoding = 'ascii'):
    key_bytes = key.encode(encoding)
    instances = []
    with open(path, 'rb') as f:
        data = f.read()
        index = data.find(key_bytes)
        while index != -1:
            instances.append(index)
            index = data.find(key_bytes, index + 1)
    return instances

def replace_text(path, key, new_key, instances=None):
    key_bytes = key.encode("ascii")
    new_key_bytes = new_key.encode("ascii")


    with open(path, 'rb') as f:
        data = f.read()

    if instances is None:  # Replace all
        data = data.replace(key_bytes, new_key_bytes)
    else:
        parts = data.split(key_bytes)
        result = []
        count = 0
        for i, part in enumerate(parts[:-1]):
            result.append(part)
            if count in instances:
                result.append(new_key_bytes)
            else:
                result.append(key_bytes)
            count += 1
        result.append(parts[-1])
        data = b"".join(result)

    with open(path, 'wb') as f:
        f.write(data)

def get_file_list():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prefix = input("Enter the prefix of files to edit:  \n(or enter gibberish to pick files manally)\n")
    subfolders = input("Do you want to search subfolders? Y/N:  ")
    file_list = find_files_with_prefix(script_dir, prefix, subfolders = subfolders.lower())
    if file_list == []:
        print("Couldn't locate any files with this prefix. Restart the program or proceed with manual file naming. ")
        num_files = int(input("Input number of files to edit: "))
        file_list = []
        for i in range(num_files):
            file = input(f"Input name for file {i+1}: ")
            file_list.append(os.path.join(script_dir, file))        

    print("Looking for files:\n", file_list)
    return file_list

def main():
    key = input("Input key to find:  ")
    new_key = input("Input new text:  ")

    instance_choice = input("Do you want all instances (a/A), or a specific number?  ")

    if instance_choice.lower() == "a":
        instances_to_edit = None
    elif not instance_choice.isdigit():
        print("An incorrect letter has been given. Please type a correct value.")
        instance_choice = input("Do you want all instances (a/A), or a specific number?  ")
        if instance_choice.lower() == "a":
            instances_to_edit = None
        elif not instance_choice.isdigit():
            print("An incorrect value has been given twice. Exiting.")
        else:
            instances_to_edit = []
            for _ in range(int(instance_choice)):
                choice = int(input("Please input the instance number (0-indexed):  "))
                instances_to_edit.append(choice)
    else:
        instances_to_edit = []
        for _ in range(int(instance_choice)):
            choice = int(input("Please input the instance number (0-indexed):  "))
            instances_to_edit.append(choice)

    for file in file_list:
        replace_text(file, key, new_key, instances_to_edit)

    print("Editing complete!")

while True:
    if file_list == None:
        file_list = get_file_list()
    main()
    exit_choice = input("Do you want to use the tool again? Y/N  ")
    if exit_choice.lower() != "y":
        time.sleep(1)
        exit()
        break
    repeat_choice = input("Do you want to edit the same files again? Y/N  ")
    if repeat_choice == "n":
        file_list = None

exit()