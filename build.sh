#/bin/bash
python -OO -m PyInstaller --hidden-import=queue -w -F -i assets/icon/main.ico main.py --add-data "assets;assets"