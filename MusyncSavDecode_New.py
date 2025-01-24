from pickle import OBJ
import clr
import json
import logging
import os
import time
# import traceback

from base64 import b64decode
from struct import unpack
from tkinter import messagebox
from Resources import SongName
from SaveStruct import SaveDataInfo, MapDataInfo, MapInfo

logger = logging.getLogger("MUSYNCSavDecode")

# Load C# Lib
# clr.AddReference("System.Runtime.Serialization.Formatters.Binary")
clr.AddReference("mscorlib")
from System import Reflection
from System.IO import MemoryStream
from System.Reflection import Assembly
from System.Runtime.Serialization.Formatters.Binary import BinaryFormatter
try:
	with open('./musync_data/ExtraFunction.cfg','r',encoding='utf8') as confFile:
		config = json.load(confFile)
	assembly = Assembly.LoadFrom(config['MainExecPath']+'MUSYNX_Data/Managed/Assembly-CSharp.dll')
	# 动态获取类的类型
	UserMemory = assembly.GetType("Assembly-CSharp.UserMemory")
	SongSaveInfo = assembly.GetType("Assembly-CSharp.SaveInfoList")
except Exception:
	logger.exception(f"Failed to Load {config['MainExecPath']}MUSYNX_Data/Managed/Assembly-CSharp.dll")

class MUSYNCSavProcess(object):
	"""docstring for MUSYNCSavProcess"""
	def __init__(self, savFile=''):
		super(MUSYNCSavProcess, self).__init__()
		self.savPath:str = savFile;
		self.userMemory:SaveDataInfo = SaveDataInfo();
		self.saveDataDict:dict[str,any] = dict();
		self.FavSong:list[str] = list();
		self.logger:logging.Logger = logging.getLogger("MUSYNCSavDecode.MUSYNCSavProcess");
		self.logger.info("creating an instance in MUSYNCSavDecode");

	def Main(self):
		if os.path.isfile(self.savPath):
			self.LoadSaveFile()
			self.FixUserMemory();
			self.FavFix()
		else:
			self.logger.error(f"文件夹\"{self.savPath}\"内找不到存档文件.")
			messagebox.showerror("Error", "文件夹内找不到存档文件.")

	'''加载存档文件并进行base64解码'''
	def LoadSaveFile(self)->None:
		startTime:int = time.perf_counter_ns()
		self.logger.debug("LoadSaveFile Start.")
		with open(self.savPath, 'r') as file:
			base64_data = file.read()
		self.Deserialize(b64decode(base64_data));
		self.logger.debug("LoadSaveFile End.");
		self.logger.info("LoadSaveFile Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000));

	"""反序列化存档数据"""
	def Deserialize(self, data)->None:
		startTime:int = time.perf_counter_ns()
		self.logger.debug("SaveDeserialize Start.")
		userMemoryPy:SaveDataInfo = SaveDataInfo();
		stream:MemoryStream = MemoryStream(data);
		userMemory = (BinaryFormatter().Deserialize(stream));
		userMemoryTypeInfo = userMemory.GetType()

		'''获取非公开的字段'''
		def GetNonPublicField(field,typeInfo=userMemoryTypeInfo,instance=userMemory)->any:
			anyVar = typeInfo.GetField(field, Reflection.BindingFlags.NonPublic | Reflection.BindingFlags.Instance);
			return anyVar.GetValue(instance);

		'''获取非公开的Get方法'''
		def GetNonPublicMethod(field:str,typeInfo=userMemoryTypeInfo,instance=userMemory)->any:
			# 获取 internal 属性的 PropertyInfo
			propertyInfo = typeInfo.GetProperty(field, Reflection.BindingFlags.Instance | Reflection.BindingFlags.NonPublic);
			# 获取属性值（调用 get 方法）
			method = propertyInfo.GetGetMethod(nonPublic=True);
			return method.Invoke(instance, None);

		'''将C# List<SongSaveInfo>转换为Python List[SongSaveInfoPy]'''
		def NetListToPyList(saveInfoList)->MapDataInfo:
			saveInfos:list[MapDataInfo] = list();
			for songSaveInfo in saveInfoList:
				typeInfo2 = songSaveInfo.GetType();
				saveInfoPy:MapDataInfo = MapDataInfo(
					GetNonPublicMethod("SongId", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("SpeedStall", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("SyncNumber", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("UploadScore", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("PlayCount", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("Isfav", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("CrcInt", typeInfo=typeInfo2, instance=songSaveInfo)
					);
				saveInfos.append(saveInfoPy);
				self.logger.debug(saveInfoPy);
			return saveInfos;

		# # 修改 private 字段的值
		# secret_name_field.SetValue(instance, "Bob")
		# secret_age_field.SetValue(instance, 25)
		# 获取 private 字段的值
		userMemoryPy.version = int(GetNonPublicField("version"));
		userMemoryPy.AppVersion = int(userMemory.AppVersion);
		userMemoryPy.saveInfoList = NetListToPyList(GetNonPublicField("saveInfoList"));
		userMemoryPy.purchaseIds = list(GetNonPublicField("purchaseIds"));
		userMemoryPy.crc = int(GetNonPublicField("crc"));
		userMemoryPy.songIndex = int(GetNonPublicField("songIndex"));
		userMemoryPy.isHard = int(GetNonPublicField("isHard"));
		userMemoryPy.buttonNumber = int(GetNonPublicField("buttonNumber"));
		userMemoryPy.sortNum = int(GetNonPublicField("sortNum"));
		userMemoryPy.missVibrate = bool(GetNonPublicField("missVibrate"));
		userMemoryPy.soundHelper = int(GetNonPublicField("soundHelper"));
		userMemoryPy.displayAdjustment = int(GetNonPublicField("displayAdjustment"));
		userMemoryPy.judgeCompensate = int(GetNonPublicField("judgeCompensate"));
		userMemoryPy.advSceneSettringString = str(GetNonPublicField("advSceneSettringString"));
		userMemoryPy.metronomeSquipment = str(GetNonPublicField("metronomeSquipment"));
		userMemoryPy.playTimeUIA = int(GetNonPublicField("playTimeUIA"));
		userMemoryPy.playTimeUIB = int(GetNonPublicField("playTimeUIB"));
		userMemoryPy.playTimeUIC = int(GetNonPublicField("playTimeUIC"));
		userMemoryPy.playTimeUID = int(GetNonPublicField("playTimeUID"));
		userMemoryPy.playTimeUIE = int(GetNonPublicField("playTimeUIE"));
		userMemoryPy.playTimeUIF = int(GetNonPublicField("playTimeUIF"));
		userMemoryPy.playTimeRankEX = int(GetNonPublicField("playTimeRankEX"));
		userMemoryPy.playTimeKnockEX = int(GetNonPublicField("playTimeKnockEX"));
		userMemoryPy.playTimeKnockNote = int(GetNonPublicField("playTimeKnockNote"));
		userMemoryPy.playVsync = bool(GetNonPublicField("playVsync"));
		userMemoryPy.buttonSetting4K = list(GetNonPublicField("buttonSetting4K"));
		userMemoryPy.buttonSetting6K = list(GetNonPublicField("buttonSetting6K"));
		userMemoryPy.hiddenUnlockSongs = bool(GetNonPublicField("hiddenUnlockSongs"));
		userMemoryPy.hideLeaderboardMini = bool(GetNonPublicField("hideLeaderboardMini"));
		userMemoryPy.playingSceneName = str(GetNonPublicField("playingSceneName"));
		userMemoryPy.selectSongName = str(GetNonPublicField("selectSongName"));
		userMemoryPy.sceneName = str(GetNonPublicField("sceneName"));
		userMemoryPy.busVolume = float(GetNonPublicField("busVolume"));
		userMemoryPy.advSceneSettingString = str(GetNonPublicField("advSceneSettingString"));
		userMemoryPy.dropSpeed = int(GetNonPublicField("dropSpeed"));
		userMemoryPy.isUseUserMemoryDropSpeed = bool(userMemory.isUseUserMemoryDropSpeed);
		userMemoryPy.dropSpeedFloat = float(GetNonPublicField("dropSpeedFloat"));
		userMemoryPy.isOpenVSync = bool(GetNonPublicField("isOpenVSync"));
		userMemoryPy.hadSaveFpsAndVSync = bool(GetNonPublicField("hadSaveFpsAndVSync"));
		userMemoryPy.fps = int(GetNonPublicField("fps"));
		self.logger.debug(userMemoryPy);
		self.userMemory = userMemoryPy;
		self.saveDataDict = userMemoryPy.ToDict();
		self.logger.debug("SaveDeserialize End.");
		self.logger.info("SaveDeserialize Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000));

	"""补全缺失数据"""
	def FixUserMemory(self)->None:
		startTime:int = time.perf_counter_ns()
		print("UserMemoryToJson Start.")
		allSongData:dict[str,list] = SongName.SongNameData;
		def GetSongName(songId:str)->MapInfo|None:
			songData:list|None = allSongData.get(songId);
			if songData is None:
				return None;
			return MapInfo(songData);

		def NoCopyright(songId:str)->bool:
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
			return (True if songId in NCR else False);

		def OldAprilFoolsDay(songId):
			OAFD = [
				]
			return (True if songId in OAFD else False);

		# 遍历列表
		for saveIndex in range(len(self.userMemory.saveInfoList)):
			mapData:MapDataInfo = self.userMemory.saveInfoList[saveIndex];
			mapInfo:MapInfo = GetSongName(mapData.SongId);
			if mapData.SongInfo is None:
				mapData.state = "NoName";
			elif mapData.Isfav:
				self.FavSong.append(mapInfo.songName);
				mapData.state = "Favo";
			elif OldAprilFoolsDay(mapData.SongId):
				mapData.state = "Fool"
			elif NoCopyright(mapData.SongId):
				mapData.state = "NoCR"







		print("UserMemoryToJson End.")
		print("UserMemoryToJson Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000))

	def Output(self)->None:
		self.LoadSaveFile();

if __name__ == '__main__':
	#Config#
	savPath = "D:/Program Files/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav"
	# savPath = "C:/Users/Ginsakura/Documents/Tencent Files/2602961063/FileRecv/savedata.sav"

	#Run#
	Object = MUSYNCSavProcess(savPath)
	Object.Main()
