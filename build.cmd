@echo off
python -OO -m PyInstaller --hidden-import=missingmodule -w -i assets/icon/main.ico main.py --add-data "assets;assets"