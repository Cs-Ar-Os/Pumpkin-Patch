# Pumpkin-Patch
A modification for Heroes 3: Horn of the Abyss which provides more gameplay variety, balance, quality of life options and various improvements / minor additions. All changes are meant to be balanced, lore-friendly and relatively small. 


To use the code you need the MMArchiveCLI by Imahero: https://github.com/imahero1492/MMArchiveCLI

To build the app, I use the following:

Hexswapper:
py -3.13 -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
python -m pip install pyinstaller psutil winshell pillow requests
:: pip install pipreqs
:: pipreqs . --force
:: pip install -r requirements.txt
python -m PyInstaller --clean --onefile --windowed --add-data "Icons/*;Icons" --noconsole --icon=pp_icon.ico HexSwapper.py

Installer:
python -m pip install --upgrade pywin32
python -m pywin32_postinstall -install

py -m pip install pywin32 
py -m PyInstaller ^
--clean ^
--onefile ^
--windowed ^
--noconsole ^
--icon=pp_icon.ico ^
--add-data "Modfiles/*;PumpkinPatch/Modfiles" ^
--hidden-import=win32con ^
--hidden-import=win32api ^
--hidden-import=win32com ^
--hidden-import=pythoncom ^
install_Pumpkin_Patch.py
