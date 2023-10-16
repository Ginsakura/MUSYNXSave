cd ./musync_data
if not exist ico.res (
  windres ico.rc -O coff -o ico.res
)
cd ..
g++ -o .\Luncher.exe .\MusyncSavDecodeLuncher.cpp .\musync_data\ico.res