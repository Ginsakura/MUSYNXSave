from base64 import b64decode,b64encode
from struct import unpack
import os
import json
from tkinter import messagebox

class MUSYNCSavProcess():
	"""docstring for MUSYNCSavProcess"""
	def __init__(self, savFile='', decodeFile=''):
		super(MUSYNCSavProcess, self).__init__()
		self.savPath = savFile
		self.decodeFile = decodeFile
		#self.dt = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		#self.dt = '2023-01-22_16-28-04'
		self.charDict = dict()
		self.saveData = ''
		self.lastPlaySong = list()
		
	def Main(self,fileExtension=''):
		if fileExtension == 'decode':
			self.SaveFileAnalyze()
			self.FavFix()
		elif os.path.isfile(self.savPath):
			self.SaveFileDecode()
			self.SaveFileAnalyze()
			self.FavFix()
		else:
			messagebox.showerror("Error", "文件夹内找不到存档文件.")

	def SaveFileDecode(self):
		with open(self.savPath,'r') as savFile:
			savEncode = savFile.read()
		#print(savEncode)
		with open(f'./musync_data/SavDecode.decode','wb+') as savBin:
			savBin.write(b64decode(savEncode))
	
	def Hex2Float_LittleEndian(self,tHex): #小端用<,大端用!或>
		return unpack('<f',bytes.fromhex(tHex))[0]
	
	def Hex2Int_LittleEndian(self,tHex):
		return unpack('<i',bytes.fromhex(tHex))[0]

	def Bytes2HexString(self,Bytes):
		return ''.join(['%02X' % b for b in Bytes])
	
	def SaveFileAnalyze(self):
		self.savBinFile = open(f'./musync_data/SavDecode.decode','rb+')
		self.savAnalyzeFile = open(f'./musync_data/SavAnalyze.analyze','w+')
		self.SaveBinFileRead(887)
		self.SaveBinFileRead(22)
		while True:
			binTemp = self.savBinFile.read(1)
			if binTemp == b'\x06':
				self.SaveAnalyzeFileWrite(f'上次游玩曲目: {"".join(self.lastPlaySong)}')
				break
			else:
				self.lastPlaySong.append(binTemp.decode())
		self.SaveBinFileRead(475)
		while True:
			if self.savBinFile.read(1) == b'\x02':
				break
		#self.SaveBinFileRead(143)
		while True:
			if (self.savBinFile.read(1) == b'S'):
				if self.savBinFile.read(1) == b'o':
					if self.savBinFile.read(1) == b'n':
						break
		self.SaveAnalyzeFileWrite("Son"+self.savBinFile.read(9).decode()) #'SongSaveInfo'
		self.savBinFile.read(2)
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
		saveDataAnalyze = open(f'./musync_data/SavAnalyze.json','w+',encoding='utf8')
		saveDataAnalyzeJson = dict()
		saveDataAnalyzeJson["LastPlay"] = "".join(self.lastPlaySong)
		saveDataAnalyzeJson["SaveData"] = list()
		with open("./musync_data/SongName.json",'r',encoding='utf8') as songNameFile:
			songNameJson = json.load(songNameFile)
		while (self.savBinFile.read(1) == b'\x01'):
			def GetSongName(ss):
				diffcute = ["Easy","Hard","Inferno"]
				if f'{ss}' in songNameJson:
					data = songNameJson[f'{ss}']
					songName = data[0]
					songKeys = ("4Key" if data[1]==4 else "6Key")
					songDifficulty = diffcute[int(data[2])]
					songDifficultyNumber = "%02d"%data[3]
					return [songName,songKeys,songDifficulty,songDifficultyNumber]
				else:
					return None
			def ZeroFormat(score,lenth):
				return f'{score}{"0"*(lenth-len(str(score)))}%'
			def NoCopyright(ss):
				NCR = ['0001F8B1','0001F8B2','0001F8BB','0001F8BC', #404 Not Found
				'0001F915','0001F916','0001F91F','0001F920', #ArroganT
				'000199C5','000199C6','000199CF','000199D0', #TWINKLE STAR
				'0001AC21','0001AC22','0001AC2B','0001AC2C', #为你而来
				'0001F20D','0001F20E','0001F217','0001F218', #寓言预见遇见你的那刻
				'0001AC85','0001AC86','0001AC8F','0001AC90', #星之伊始
				'0001F979','0001F97A','0001F983','0001F984', #樂園 - Atlantis
				'0001ACE9','0001ACEA','0001ACF3','0001ACF4', #观星者
				]
				if ss in NCR:return True
				else:return False
			def OldAprilFoolsDay(ss):
				OAFD = []
				if ss in OAFD:return True
				else:return False

			self.saveData = self.savBinFile.read(29)
			SongID = self.Hex2Int_LittleEndian(self.Bytes2HexString(self.saveData[0:4]))
			Unknown0 = self.Bytes2HexString(self.saveData[4:8])
			temp = self.Bytes2HexString(self.saveData[8:12])
			SpeedStall = temp[6:]+temp[4:6]+temp[2:4]+temp[0:2]
			Unknown1 = self.Bytes2HexString(self.saveData[12:16])
			SyncNumber = str(self.Hex2Int_LittleEndian(self.Bytes2HexString(self.saveData[16:20])))
			UploadScore = self.Hex2Float_LittleEndian(self.Bytes2HexString(self.saveData[20:24]))
			PlayCount = self.Hex2Int_LittleEndian(self.Bytes2HexString(self.saveData[24:28]))

			songName = GetSongName(SpeedStall)
			if songName is None:
				self.SaveAnalyzeFileWrite(SpeedStall+' ,No Name')
				continue
			if NoCopyright(SpeedStall):
				print(SpeedStall,"NoCopyright")
				continue
			if OldAprilFoolsDay(SpeedStall):
				print(SpeedStall,'OldAprilFoolsDay')
				continue

			IsFav = '0x01' if self.saveData[28]==1 else '0x00'
			if len(SyncNumber) == 5:SyncNumber = f'{SyncNumber[0:3]}.{SyncNumber[3:]}%'
			elif len(SyncNumber) == 4:SyncNumber = f'{SyncNumber[0:2]}.{SyncNumber[2:]}%'
			elif len(SyncNumber) == 3:SyncNumber = f'{SyncNumber[0]}.{SyncNumber[1:]}%'
			elif len(SyncNumber) == 2:SyncNumber = f'0.{SyncNumber}%'
			else:SyncNumber = f'0.0{SyncNumber}%'
			UploadScore = UploadScore*100
			if UploadScore == 0:UploadScore = '0.00000000000000%'
			elif UploadScore < 10:UploadScore = ZeroFormat(UploadScore,16) #'%.16f%%'%UploadScore
			elif UploadScore < 100:UploadScore = ZeroFormat(UploadScore,17)
			else:UploadScore = ZeroFormat(UploadScore,18)
			self.SaveAnalyzeFileWrite(f'| {" "*(6-len(str(SongID)))}{SongID} | {Unknown0} |  {SpeedStall}  | {Unknown1} |    {" "*(7-len(SyncNumber))}{SyncNumber} | {" "*(19-len(UploadScore))}{UploadScore} | {" "*(9-len(str(PlayCount)))}{PlayCount} |  {IsFav} |')
			saveDataAnalyzeJson["SaveData"].append(dict(SpeedStall=SpeedStall,SongName=songName,SyncNumber=SyncNumber,UploadScore=UploadScore,PlayCount=PlayCount,IsFav=IsFav))
		json.dump(saveDataAnalyzeJson,saveDataAnalyze,indent="",ensure_ascii=False)
		saveDataAnalyze.close()

	def SaveBinFileRead(self,lenth):
		print(self.savBinFile.read(lenth))
	def SaveAnalyzeFileWrite(self,text,end='\n'):
		self.savAnalyzeFile.write(f'{text}\n')
		print(text,end=end)

	def FavFix(self):
		with open(f'./musync_data/SavAnalyze.json','r+',encoding='utf8') as saveJsonFile:
			saveJson = json.load(saveJsonFile)
			saveJsonFavFix = saveJson
		saveJsonFile = open(f'./musync_data/SavAnalyze.json','w+',encoding='utf8')
		for ids in range(len(saveJson["SaveData"])):
			if saveJson["SaveData"][ids]["IsFav"] == "0x01":
				for idx in range(ids+1,len(saveJson["SaveData"])):
					oldName = ("" if saveJson["SaveData"][ids]["SongName"] is None else saveJson["SaveData"][ids]["SongName"][0])
					newName = ("" if saveJson["SaveData"][idx]["SongName"] is None else saveJson["SaveData"][idx]["SongName"][0])
					if (not oldName == "") and (oldName[:4] == newName[:4]) and (not newName == ""):
						saveJsonFavFix["SaveData"][idx]["IsFav"] = "0x01"
		json.dump(saveJsonFavFix,saveJsonFile,indent="")
		saveJsonFile.close()

if __name__ == '__main__':
	#Config#
	# savPath = "D:/Program Files/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav"
	savPath = "C:/Users/Ginsakura/Documents/Tencent Files/2602961063/FileRecv/savedata.sav"

	#Run#
	Object = MUSYNCSavProcess(savPath)
	Object.Main()
