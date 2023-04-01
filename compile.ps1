$version = (py -c "import MusyncSavDecodeGUI;print(MusyncSavDecodeGUI.version)")
Remove-Item -Path ./Release/* -Force -Recurse

venv\Scripts\Activate.ps1

pyinstaller --distpath ./Release/NoCLI/ -D -i ./musync_data/Musync.ico ./MusyncSavDecodeGUI.py -w --clean
Compress-Archive -LiteralPath ./Release/NoCLI/MusyncSavDecodeGUI/ -DestinationPath ("./Release/MusyncSavDecodeGUI_NoConsole_"+$version+".zip")
pyinstaller --distpath ./Release/ -F -i ./musync_data/Musync.ico ./MusyncSavDecodeGUI.py -w
Rename-Item -Path ./Release/MusyncSavDecodeGUI.exe -NewName ("MusyncSavDecodeGUI_NoConsole_"+$version+"_AllInOne.exe")

pyinstaller --distpath ./Release/WithCLI/ -D -i ./musync_data/Musync.ico ./MusyncSavDecodeGUI.py
Compress-Archive -LiteralPath ./Release/WithCLI/MusyncSavDecodeGUI/ -DestinationPath ("./Release/MusyncSavDecodeGUI_WithConsole_"+$version+".zip")
pyinstaller --distpath ./Release/ -F -i ./musync_data/Musync.ico ./MusyncSavDecodeGUI.py
Rename-Item -Path ./Release/MusyncSavDecodeGUI.exe -NewName ("MusyncSavDecodeGUI_WithConsole_"+$version+"_AllInOne.exe")

Start-Sleep -Seconds 5
Copy-Item -Path ("./Release/MusyncSavDecodeGUI_WithConsole_"+$version+"_AllInOne.exe") -Destination "./MusyncSavDecodeGUI.exe"