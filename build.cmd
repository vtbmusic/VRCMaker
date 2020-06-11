pyinstaller --hidden-import=queue -w -i assets/icon/main.ico main.py

xcopy assets dist\main\assets\ /e