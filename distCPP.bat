cd ./musync_data
windres .\ico.rc -O coff -o ico.res
cd ..
g++ -o .\MusyncSavDecodeLuncher.exe .\MusyncSavDecodeLuncher.cpp .\musync_data\ico.res