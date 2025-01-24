import clr
import json
import logging
import os
import time
from base64 import b64decode
from tkinter import messagebox
from .Resources import SongName, SaveDataInfo, MapDataInfo, MapInfo

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
	"""docstring for MUSYNCSavProcess""";
	def __init__(self, savFile=''):
		super(MUSYNCSavProcess, self).__init__()
		self.savPath:str = savFile;
		self.userMemory:SaveDataInfo = SaveDataInfo();
		self.saveDataDict:dict[str,any] = dict();
		self.FavSong:list[str] = list();
		self.__logger:logging.Logger = logging.getLogger("MUSYNCSavDecode.MUSYNCSavProcess");
		self.__logger.info("creating an instance in MUSYNCSavDecode");

	def Main(self):
		if os.path.isfile(self.savPath):
			self.LoadSaveFile();
			self.FixUserMemory();
			self.FavFix()
		else:
			self.__logger.error(f"文件夹\"{self.savPath}\"内找不到存档文件.")
			messagebox.showerror("Error", "文件夹内找不到存档文件.")

	def LoadSaveFile(self)->None:
		'''加载存档文件并进行base64解码''';
		startTime:int = time.perf_counter_ns();
		self.__logger.debug("LoadSaveFile Start.");
		with open(self.savPath, 'r') as file:
			base64_data = file.read()
		self.Deserialize(b64decode(base64_data));
		self.__logger.debug("LoadSaveFile End.");
		self.__logger.info("LoadSaveFile Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000));

	def Deserialize(self, data)->None:
		"""反序列化存档数据""";
		startTime:int = time.perf_counter_ns();
		self.__logger.debug("SaveDeserialize Start.");
		userMemoryPy:SaveDataInfo = SaveDataInfo();
		stream:MemoryStream = MemoryStream(data);
		userMemory = (BinaryFormatter().Deserialize(stream));
		userMemoryTypeInfo = userMemory.GetType()

		def GetNonPublicField(field,typeInfo=userMemoryTypeInfo,instance=userMemory)->any:
			'''获取非公开的字段''';
			anyVar = typeInfo.GetField(field, Reflection.BindingFlags.NonPublic | Reflection.BindingFlags.Instance);
			return anyVar.GetValue(instance);

		def GetNonPublicMethod(field:str,typeInfo=userMemoryTypeInfo,instance=userMemory)->any:
			'''获取非公开的Get方法''';
			# 获取 internal 属性的 PropertyInfo
			propertyInfo = typeInfo.GetProperty(field, Reflection.BindingFlags.Instance | Reflection.BindingFlags.NonPublic);
			# 获取属性值（调用 get 方法）
			method = propertyInfo.GetGetMethod(nonPublic=True);
			return method.Invoke(instance, None);

		def NetListToPyList(saveInfoList)->MapDataInfo:
			'''将C# List<SongSaveInfo>转换为Python List[SongSaveInfoPy]''';
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
				# self.logger.debug(saveInfoPy);
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
		self.__logger.debug(userMemoryPy);
		self.userMemory = userMemoryPy;
		self.saveDataDict = userMemoryPy.ToDict();
		self.__logger.debug("SaveDeserialize End.");
		self.__logger.info("SaveDeserialize Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000));

	def FixUserMemory(self)->None:
		"""补全缺失数据""";
		startTime:int = time.perf_counter_ns();
		self.__logger.debug("UserMemoryToJson Start.");

		def GetSongName(songId:str)->MapInfo|None:
			"获取谱面对应的信息";
			songData:list|None = allSongData.get(songId);
			if songData is None:
				return None;
			return MapInfo(songData);

		def NoCopyright(songId:str)->bool:
			"标记无版权曲目";
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
				];
			return (True if songId in NCR else False);

		def OldAprilFoolsDay(songId):
			"标记愚人节谱面";
			OAFD = [
				];
			return (True if songId in OAFD else False);

		allSongData:dict[str,list] = SongName.SongNameData;
		removeIndexList:list[int] = list();
		self.__logger.debug("|  SongID  | SpeedStall | SyncNumber |     UploadScore     | PlayCount |  state  |")
		# 遍历列表
		for saveIndex in range(len(self.userMemory.saveInfoList)):
			mapData:MapDataInfo = self.userMemory.saveInfoList[saveIndex];
			mapInfo:MapInfo = GetSongName(mapData.SongId);
			if mapData.SongInfo is None:
				mapData.state = "NoName";
				removeIndexList.insert(0,saveIndex);
			elif mapData.Isfav:
				self.FavSong.append(mapInfo.songName);
				mapData.state = "Favo";
			elif OldAprilFoolsDay(mapData.SongId):
				mapData.state = "Fool";
			elif NoCopyright(mapData.SongId):
				mapData.state = "NoCR";

			self.__logger.debug(f'| {"%08X"%mapData.SongId:>8} | {"%08X"%mapData.SpeedStall:^10} | {"%f%%"%(mapData.SyncNumber/100):>10} | {"%f%%"%(mapData.UploadScore*100):>19} | {mapData.PlayCount:>9} | {mapData.state:>7} |');
			mapData.SongInfo = mapInfo;
			self.userMemory.saveInfoList[saveIndex] = mapData;
		for removeIndex in removeIndexList:
			self.userMemory.saveInfoList.pop(removeIndex);
		self.__logger.debug("UserMemoryToJson End.");
		self.__logger.info("UserMemoryToJson Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000));

	def FavFix(self):
		"修复收藏仅应用于每首歌的4KEZ谱面的问题";
		startTime = time.perf_counter_ns()
		self.__logger.debug("FavFix Start.");
		allSongData:dict[str,list] = SongName.SongNameData;
		self.__logger.debug(f"Favorites List：{self.FavSong}");
		for index in range(len(self.userMemory.saveInfoList)):
			if self.userMemory.saveInfoList[index].name in self.FavSong:
				self.userMemory.saveInfoList[index].state = "Favo"
		self.userMemory.ToJson();
		self.__logger.debug("FavFix End.");
		self.__logger.info("FavFix Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000));

if __name__ == '__main__':
	#Config#
	savPath = "D:/Program Files/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav"
	# savPath = "C:/Users/Ginsakura/Documents/Tencent Files/2602961063/FileRecv/savedata.sav"

	#Run#
	Object = MUSYNCSavProcess(savPath)
	Object.Main()
