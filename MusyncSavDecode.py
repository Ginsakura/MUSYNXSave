import base64
import datetime
import struct
import os
from tkinter import messagebox

class MUSYNCSavProcess():
	"""docstring for MUSYNCSavProcess"""
	def __init__(self, savFile='', decodeFile=''):
		super(MUSYNCSavProcess, self).__init__()
		self.savPath = savFile
		#self.analyzeFile = analyzeFile
		self.decodeFile = decodeFile
		#self.dt = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		#self.dt = '2023-01-22_16-28-04'
		self.charDict = dict()
		self.saveData = ''
		
	def Main(self,fileExtension=''):
		if fileExtension == 'decode':
			self.SaveFileAnalyze()
		elif os.path.isfile(self.savPath):
			try:
				self.SaveFileDecode()
				self.SaveFileAnalyze()
				return self.savPath
			except:
				messagebox.showerror("Error", "存档文件不可读或文件并非MUSYNC存档.")
		else:
			messagebox.showerror("Error", "文件夹内找不到存档文件.")

	def SaveFileDecode(self):
		with open(self.savPath,'r') as savFile:
			savEncode = savFile.read()
		#print(savEncode)
		with open(f'./SavDecode.decode','wb+') as savBin:
			savBin.write(base64.standard_b64decode(savEncode))
	
	def Hex2Float_LittleEndian(self,tHex): #小端用<,大端用!或>
		return struct.unpack('<f',bytes.fromhex(tHex))[0]
	
	def Hex2Int_LittleEndian(self,tHex):
		return struct.unpack('<i',bytes.fromhex(tHex))[0]

	def Bytes2HexString(self,Bytes):
		return ''.join(['%02X' % b for b in Bytes])
	
	def SaveFileAnalyze(self):
		self.savBinFile = open(f'./SavDecode.decode','rb+')
		self.savAnalyzeFile = open(f'./SavAnalyze.analyze','w+')
		self.SaveBinFileRead(887)
		self.SaveBinFileRead(22)
		lastPlaySong = list()
		while True:
			binTemp = self.savBinFile.read(1)
			if binTemp == b'\x06':
				self.SaveAnalyzeFileWrite(f'上次游玩曲目: {"".join(lastPlaySong)}')
				break
			else:
				lastPlaySong.append(binTemp.decode())
		self.SaveBinFileRead(493)
		self.SaveBinFileRead(144)
		self.SaveAnalyzeFileWrite(self.savBinFile.read(12).decode()) #'SongSaveInfo'
		self.SaveBinFileRead(2)
		while (self.savBinFile.read(3) == b'\x00\x00\x09'):
			char = self.savBinFile.read(1)
			grop = self.savBinFile.read(1)
			try:
				self.charDict[f"{''.join(['%02X' % b for b in grop])}{''.join(['%02X' % b for b in char])}"] = char.decode()
			except:
				pass
		self.SaveAnalyzeFileWrite(self.charDict)
		self.saveData = self.savBinFile.read(185)
		print(self.saveData[0:9])
		self.SaveAnalyzeFileWrite(self.saveData[10:22].decode()) #'SongSaveInfo'
		self.SaveAnalyzeFileWrite(self.saveData[27:50].decode()) #'<SongId>k__BackingField'
		self.SaveAnalyzeFileWrite(self.saveData[51:78].decode()) #'<SpeedStall>k__BackingField'
		self.SaveAnalyzeFileWrite(self.saveData[79:106].decode()) #'<SyncNumber>k__BackingField'
		self.SaveAnalyzeFileWrite(self.saveData[107:135].decode()) #'<UploadScore>k__BackingField'
		self.SaveAnalyzeFileWrite(self.saveData[136:162].decode()) #'<PlayCount>k__BackingField'
		self.SaveAnalyzeFileWrite(self.saveData[163:185].decode()) #'<Isfav>k__BackingField'
		self.SaveBinFileRead(37)
		self.SaveAnalyzeFileWrite('| SongID | Unknown0 | SpeedStall | Unknown1 | SyncNumber |     UploadScore     | PlayCount | IsFav |')
		self.Analyze2Json()
		self.savBinFile.close()
		self.savAnalyzeFile.close()

	def Analyze2Json(self):
		saveDataAnalyze = open(f'./SavAnalyze.json','w+')
		saveDataAnalyze.write("{\n\t\"LastPlay\" : \"Yeyingwu\",\n\t\"SaveData\":[")
		songStart = True
		while (self.savBinFile.read(1) == b'\x01'):
			def ZeroFormat(score,lenth):return f'{score}{"0"*(lenth-len(str(score)))}%'

			if songStart :saveDataAnalyze.write("\n\t")
			else:saveDataAnalyze.write(",\n\t")
			songStart = False
			self.saveData = self.savBinFile.read(29)
			SongID = self.Hex2Int_LittleEndian(self.Bytes2HexString(self.saveData[0:4]))
			Unknown0 = self.Bytes2HexString(self.saveData[4:8])
			SpeedStall = self.Bytes2HexString(self.saveData[8:12])
			Unknown1 = self.Bytes2HexString(self.saveData[12:16])
			SyncNumber = str(self.Hex2Int_LittleEndian(self.Bytes2HexString(self.saveData[16:20])))
			UploadScore = self.Hex2Float_LittleEndian(self.Bytes2HexString(self.saveData[20:24]))
			PlayCount = self.Hex2Int_LittleEndian(self.Bytes2HexString(self.saveData[24:28]))
			IsFav = '0x01' if self.saveData[28]==1 else '0x00'
			if len(SyncNumber) == 5:SyncNumber = f'{SyncNumber[0:3]}.{SyncNumber[3:]}%'
			elif len(SyncNumber) == 4:SyncNumber = f'{SyncNumber[0:2]}.{SyncNumber[2:]}%'
			elif len(SyncNumber) == 3:SyncNumber = f'{SyncNumber[0]}.{SyncNumber[1:]}%'
			elif len(SyncNumber) == 2:SyncNumber = f'0.{SyncNumber}%'
			else:SyncNumber = f'0.0{SyncNumber}%'
			UploadScore = UploadScore*100
			if UploadScore == 0:UploadScore = '0.00000000000000%'
			elif UploadScore < 10:UploadScore = ZeroFormat(UploadScore,16)
			elif UploadScore < 100:UploadScore = ZeroFormat(UploadScore,17)
			else:UploadScore = ZeroFormat(UploadScore,18)
			self.SaveAnalyzeFileWrite(f'| {" "*(6-len(str(SongID)))}{SongID} | {Unknown0} |  {SpeedStall}  | {Unknown1} |    {" "*(7-len(SyncNumber))}{SyncNumber} | {" "*(19-len(UploadScore))}{UploadScore} | {" "*(9-len(str(PlayCount)))}{PlayCount} |  {IsFav} |')
			saveDataFormat = '{\"SongID\" : %d,\n\t\"SongName\" : [\"\",\"\"],\n\t\"SpeedStall\" : \"%s\",\n\t\"SyncNumber\" : \"%s\",\n\t\"UploadScore\" : \"%s\",\n\t\"PlayCount\" : %d,\n\t\"IsFav\" : \"%s\"}'%(SongID,SpeedStall,SyncNumber,UploadScore,PlayCount,IsFav)
			saveDataAnalyze.write(saveDataFormat)
		saveDataAnalyze.write('\n\t]\n}')
		saveDataAnalyze.close()

	def SaveBinFileRead(self,lenth):
		print(self.savBinFile.read(lenth))
	def SaveAnalyzeFileWrite(self,text):
		self.savAnalyzeFile.write(f'{text}\n')
		print(text)

if __name__ == '__main__':
	#Config#
	savPath = "D:/Program Files/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav"

	#Run#
	Object = MUSYNCSavProcess(savPath)
	Object.Main()
