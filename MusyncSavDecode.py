import json
import os
import time
# import traceback

from struct import unpack
from tkinter import messagebox

from base64 import b64decode,b64encode

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
		self.FavSong = list()
		
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
		startTime = time.perf_counter_ns()
		print("SaveFileAnalyze Start.")
		self.savBinFile = open(f'./musync_data/SavDecode.decode','rb+')
		self.savAnalyzeFile = open(f'./musync_data/SavAnalyze.analyze','w+')
		self.SaveBinFileRead(22)
		self.SaveBinFileRead(92)
		self.SaveBinFileRead(518)
		self.SaveBinFileRead(41)
		self.SaveBinFileRead(121)
		binTemp = self.savBinFile.read(1)
		while (binTemp != b'\x55'): # UIB_PlayingScene
			binTemp = self.savBinFile.read(1)
		self.SaveBinFileRead(21)
		while True:
			binTemp = self.savBinFile.read(1)
			if binTemp == b'\x06':
				self.SaveAnalyzeFileWrite(f'上次游玩曲目: {"".join(self.lastPlaySong)}')
				break
			else:
				self.lastPlaySong.append(binTemp.decode('ascii'))
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
		self.Analyze2Json()
		self.savBinFile.close()
		self.savAnalyzeFile.close()
		print("SaveFileAnalyze End.")
		endTime = time.perf_counter_ns()
		print("SaveFileAnalyze Run Time: %f ms"%((endTime - startTime)/1000000))


	def Analyze2Json(self):
		startTime = time.perf_counter_ns()
		print("Analyze2Json Start.")
		self.SaveAnalyzeFileWrite('| SongID | Unknown0 | SpeedStall | Unknown1 | SyncNumber |     UploadScore     | PlayCount | statu |')
		saveDataAnalyze = open(f'./musync_data/SavAnalyze.json','w+',encoding='utf8')
		# FavSong = open(f'./musync_data/FavSong.tmp','w',encoding='utf8')
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
				NCR = [
				'00019191','00019192','0001919B','0001919C', #粉色柠檬
				'000199C5','000199C6','000199CF','000199D0', #TWINKLE STAR
				'0001AC21','0001AC22','0001AC2B','0001AC2C', #为你而来
				'0001AC85','0001AC86','0001AC8F','0001AC90', #星之伊始
				'0001ACE9','0001ACEA','0001ACF3','0001ACF4', #观星者
				'0001F20D','0001F20E','0001F217','0001F218', #寓言预见遇见你的那刻
				'0001F8B1','0001F8B2','0001F8BB','0001F8BC', #404 Not Found
				'0001F915','0001F916','0001F91F','0001F920', #ArroganT
				'0001F979','0001F97A','0001F983','0001F984', #樂園 - Atlantis
				]
				if ss in NCR:return True
				else:return False
			def OldAprilFoolsDay(ss):
				OAFD = []
				if ss in OAFD:return True
				else:return False

			self.saveData = self.savBinFile.read(29)
			SongID = int.from_bytes(self.saveData[0:4], 'little')
			Unknown0 = ''.join(['%02X' % b for b in self.saveData[4:8]])
			temp = ''.join(['%02X' % b for b in self.saveData[8:12]])
			SpeedStall = temp[6:]+temp[4:6]+temp[2:4]+temp[0:2]
			Unknown1 = ''.join(['%02X' % b for b in self.saveData[12:16]])
			SyncNumber = str(int.from_bytes(self.saveData[16:20], 'little'))
			UploadScore = unpack('<f',bytes.fromhex(self.Bytes2HexString(self.saveData[20:24])))[0]
			PlayCount = int.from_bytes(self.saveData[24:28], 'little')

			if self.saveData[28]==1:
				statu = "Favo"
				# FavSong.write(songName[0]+"\n")
				self.FavSong.append(songName[0])
			else:
				statu = '    '

			if NoCopyright(SpeedStall):
				statu = "NoCR"
			if OldAprilFoolsDay(SpeedStall):
				statu = "Fool"
			songName = GetSongName(SpeedStall)
			if songName is None:
				statu = "NoName"

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

			self.SaveAnalyzeFileWrite(f'| {" "*(6-len(str(SongID)))}{SongID} | {Unknown0} |  {SpeedStall}  | {Unknown1} |    {" "*(7-len(SyncNumber))}{SyncNumber} | {" "*(19-len(UploadScore))}{UploadScore} | {" "*(9-len(str(PlayCount)))}{PlayCount} | {statu:^6} |')
			if statu == 'NoName': continue
			saveDataAnalyzeJson["SaveData"].append(dict(
				SpeedStall=SpeedStall,
				SongName=songName,
				SyncNumber=SyncNumber,
				UploadScore=UploadScore,
				PlayCount=PlayCount,
				Status=statu
				))
		json.dump(saveDataAnalyzeJson,saveDataAnalyze,indent="",ensure_ascii=False)
		saveDataAnalyze.close()
		# FavSong.close()
		print("Analyze2Json End.")
		endTime = time.perf_counter_ns()
		print("Analyze2Json Run Time: %f ms"%((endTime - startTime)/1000000))

	def SaveBinFileRead(self,lenth):
		print(self.savBinFile.read(lenth))
	def SaveAnalyzeFileWrite(self,text,end='\n',isPrint=True):
		self.savAnalyzeFile.write(f'{text}\n')
		if isPrint:
			print(text,end=end)

	def FavFix(self):
		startTime = time.perf_counter_ns()
		with open(f'./musync_data/SavAnalyze.json','r+',encoding='utf8') as saveJsonFile:
			saveJsonFavFix = json.load(saveJsonFile)
		saveJsonFile = open(f'./musync_data/SavAnalyze.json','w+',encoding='utf8')
		print(f"Favorites List：{self.FavSong}")
		for ids in range(len(saveJsonFavFix["SaveData"])):
			if saveJsonFavFix["SaveData"][ids]["SongName"][0] in self.FavSong:
				saveJsonFavFix["SaveData"][ids]["statu"] = "Favo"
		json.dump(saveJsonFavFix,saveJsonFile,indent="",ensure_ascii=False)
		saveJsonFile.close()
		endTime = time.perf_counter_ns()
		print("FavFix Run Time: %f ms"%((endTime - startTime)/1000000))

if __name__ == '__main__':
	#Config#
	# savPath = "D:/Program Files/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav"
	savPath = "C:/Users/Ginsakura/Documents/Tencent Files/2602961063/FileRecv/savedata.sav"

	#Run#
	Object = MUSYNCSavProcess(savPath)
	Object.Main()
