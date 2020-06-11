#/bin/bash
pyinstaller --hidden-import=queue -w -F -i assets/icon/main.ico main.py

cp -r ./assets ./dist/main/