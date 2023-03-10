Remove-Item -Path ".\dist\MusyncSavDecodeGUI_WithConsole.exe"
Remove-Item -Path ".\dist\MusyncSavDecodeGUI_NoConsole.exe"
pyinstaller -F -i ./musync/Musync.ico ./MusyncSavDecodeGUI.py -w
Rename-Item -Path ".\dist\MusyncSavDecodeGUI.exe" -NewName "MusyncSavDecodeGUI_NoConsole.exe"
pyinstaller -F -i ./musync/Musync.ico ./MusyncSavDecodeGUI.py
Rename-Item -Path ".\dist\MusyncSavDecodeGUI.exe" -NewName "MusyncSavDecodeGUI_WithConsole.exe"
Start-Sleep -Seconds 5
Copy-Item -Path ".\dist\MusyncSavDecodeGUI_WithConsole.exe" -Destination "./MusyncSavDecodeGUI.exe"