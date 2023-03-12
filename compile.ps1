$version = (py -c "import MusyncSavDecodeGUI;print(MusyncSavDecodeGUI.version)")
Remove-Item -Path ./dist/*
pyinstaller -F -i ./musync_data/Musync.ico ./MusyncSavDecodeGUI.py -w
Rename-Item -Path ./dist/MusyncSavDecodeGUI.exe -NewName ("MusyncSavDecodeGUI_NoConsole_"+$version+".exe")
pyinstaller -F -i ./musync_data/Musync.ico ./MusyncSavDecodeGUI.py
Rename-Item -Path ./dist/MusyncSavDecodeGUI.exe -NewName ("MusyncSavDecodeGUI_WithConsole_"+$version+".exe")
Start-Sleep -Seconds 5
Copy-Item -Path ("./dist/MusyncSavDecodeGUI_WithConsole_"+$version+".exe") -Destination "./MusyncSavDecodeGUI.exe"