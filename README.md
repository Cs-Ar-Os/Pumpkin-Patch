# Pumpkin-Patch
A modification for Heroes 3: Horn of the Abyss which provides more gameplay variety, balance, quality of life options and various improvements / minor additions. All changes are meant to be balanced, lore-friendly and relatively small. 


To use the code you need the MMArchiveCLI by Imahero: https://github.com/imahero1492/MMArchiveCLI

To build the app, I use the following:

Hexswapper:
python -m PyInstaller --clean --onefile --windowed --add-data "Icons/*;Icons" --noconsole --icon=pp_icon.ico HexSwapper.py

Installer:
py -m pip install pywin32 
py -m PyInstaller --onefile --windowed --add-data "PumpkinPatch/*;PumpkinPatch" install_Pumpkin_Patch.py --noconsole --onefile --icon=pp_icon.ico --hidden-import=win32com 

