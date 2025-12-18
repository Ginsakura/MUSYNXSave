import clr
import logging
import os
import sys
import time
from base64 import b64decode
from tkinter import messagebox

from Resources import Logger

logger:logging.Logger = Logger.GetLogger(name="MUSYNCSavDecode")
try:
	from Resources import Config, SongName, SaveDataInfo, MapDataInfo, MapInfo
	# Load C# Lib
	# clr.AddReference("System.Runtime.Serialization.Formatters.Binary")
	clr.AddReference("mscorlib")
	from System import Reflection
	from System.IO import MemoryStream
	from System.Reflection import Assembly
	from System.Runtime.Serialization.Formatters.Binary import BinaryFormatter
except Exception:
	logger.exception("Import Error.")
	sys.exit(101)

class MUSYNCSavProcess(object):
	"""docstring for MUSYNCSavProcess"""
	def __init__(self, savFile:str=''):
		super(MUSYNCSavProcess, self).__init__()
		self.__assembly_loaded:bool = False
		dllPath:str|None = None
		try:
			dllPath = os.path.join(Config.MainExecPath, 'MUSYNX_Data', 'Managed', 'Assembly-CSharp.dll')
			assembly = Assembly.LoadFrom(dllPath)
			self.__assembly = assembly
			self.__assembly_loaded = True
		except Exception:
			logger.exception(f"Failed to Load {dllPath or 'assembly (path construction failed)'}")
			raise
		self.savPath:str = savFile
		self.FavSong:list[str] = list()
		self.__logger:logging.Logger = Logger.GetLogger(name="MUSYNCSavDecode.MUSYNCSavProcess")
		self.__logger.info("creating an instance in MUSYNCSavDecode")

	def Main(self):
		if os.path.isfile(self.savPath):
			self.LoadSaveFile()
			self.FixUserMemory()
			self.FavFix()
			SaveDataInfo.DumpToJson()
		else:
			self.__logger.error(f"文件夹\"{self.savPath}\"内找不到存档文件.")
			messagebox.showerror("Error", "文件夹内找不到存档文件.")

	def LoadSaveFile(self)->None:
		'''加载存档文件并进行base64解码'''
		startTime:int = time.perf_counter_ns()
		self.__logger.debug("LoadSaveFile Start.")
		with open(self.savPath, 'r', encoding="utf-8") as file:
			base64_data = file.read()
		self.Deserialize(b64decode(base64_data))
		self.__logger.debug("LoadSaveFile End.")
		self.__logger.info("LoadSaveFile Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000))

	def Deserialize(self, data)->None:
		"""反序列化存档数据"""
		startTime:int = time.perf_counter_ns()
		self.__logger.debug("SaveDeserialize Start.")
		stream:MemoryStream = MemoryStream(data)
		try:
			userMemory = (BinaryFormatter().Deserialize(stream))
		finally:
			stream.Dispose()
		userMemoryTypeInfo = userMemory.GetType()

		def GetNonPublicField(field,typeInfo=userMemoryTypeInfo,instance=userMemory)->any:
			'''获取非公开的字段'''
			anyVar = typeInfo.GetField(field, Reflection.BindingFlags.NonPublic | Reflection.BindingFlags.Instance)
			return anyVar.GetValue(instance)

		def GetNonPublicMethod(field:str,typeInfo=userMemoryTypeInfo,instance=userMemory)->any:
			'''获取非公开的Get方法'''
			# 获取 internal 属性的 PropertyInfo
			propertyInfo = typeInfo.GetProperty(field, Reflection.BindingFlags.Instance | Reflection.BindingFlags.NonPublic)
			# 获取属性值（调用 get 方法）
			method = propertyInfo.GetGetMethod(nonPublic=True)
			return method.Invoke(instance, None)

		def NetListToPyList(saveInfoList)->list[MapDataInfo]:
			'''将C# List<SongSaveInfo>转换为Python List[SongSaveInfoPy]'''
			saveInfos:list[MapDataInfo] = list()
			for songSaveInfo in saveInfoList:
				typeInfo2 = songSaveInfo.GetType()
				saveInfoPy:MapDataInfo = MapDataInfo(
					GetNonPublicMethod("SongId", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("SpeedStall", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("SyncNumber", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("UploadScore", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("PlayCount", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("Isfav", typeInfo=typeInfo2, instance=songSaveInfo),
					GetNonPublicMethod("CrcInt", typeInfo=typeInfo2, instance=songSaveInfo)
					)
				saveInfos.append(saveInfoPy)
				# self.logger.debug(saveInfoPy)
			return saveInfos

		# # 修改 private 字段的值
		# secret_name_field.SetValue(instance, "Bob")
		# secret_age_field.SetValue(instance, 25)
		# 获取 private 字段的值
		fieldMappings: list[tuple[str, object]] = [
			("version", int),
			("crc", int),
			("saveInfoList", lambda v: NetListToPyList(v)),
			("purchaseIds", list),
			("songIndex", int),
			("isHard", int),
			("buttonNumber", int),
			("sortNum", int),
			("missVibrate", bool),
			("soundHelper", int),
			("displayAdjustment", int),
			("judgeCompensate", int),
			("advSceneSettringString", str),
			("metronomeSquipment", str),
			("playTimeUIA", int),
			("playTimeUIB", int),
			("playTimeUIC", int),
			("playTimeUID", int),
			("playTimeUIE", int),
			("playTimeUIF", int),
			("playTimeRankEX", int),
			("playTimeKnockEX", int),
			("playTimeKnockNote", int),
			("playVsync", bool),
			("buttonSetting4K", list),
			("buttonSetting6K", list),
			("hiddenUnlockSongs", bool),
			("hideLeaderboardMini", bool),
			("playingSceneName", str),
			("selectSongName", str),
			("sceneName", str),
			("busVolume", float),
			("advSceneSettingString", str),
			("dropSpeed", int),
			("dropSpeedFloat", float),
			("isOpenVSync", bool),
			("hadSaveFpsAndVSync", bool),
			("fps", int),
		]
		for field, converter in fieldMappings:
			raw_value = GetNonPublicField(field)
			setattr(SaveDataInfo, field, converter(raw_value))

		# 具有特殊来源的字段（直接从 userMemory 读取）
		SaveDataInfo.AppVersion = int(userMemory.AppVersion)
		SaveDataInfo.isUseUserMemoryDropSpeed = bool(userMemory.isUseUserMemoryDropSpeed)

		self.__logger.debug(SaveDataInfo.ToDict(debug=True))
		self.__logger.debug("SaveDeserialize End.")
		self.__logger.info("SaveDeserialize Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000))

	def FixUserMemory(self)->None:
		"""补全缺失数据"""
		startTime:int = time.perf_counter_ns()
		self.__logger.debug("UserMemoryToJson Start.")

		def GetSongName(songId:int)->MapInfo|None:
			"""获取谱面对应的信息"""
			songData:list|None = allSongData.get("%d"%songId)
			if songData is None:
				return None
			isBuiltin:bool = songData[0] in allSongData["BuiltinSong"]
			return MapInfo(songData,isBuiltin)

		def NoCopyright(songId:int)->bool:
			"""标记无版权曲目"""
			NCR = [
				102801, 102802, 102811, 102812, #粉色柠檬
				104901, 104902, 104911, 104912, #TWINKLE STAR
				109601, 109602, 109611, 109612, #为你而来
				109701, 109702, 109711, 109712, #星之伊始
				109801, 109802, 109811, 109812, #观星者
				127501, 127502, 127511, 127512, #寓言预见遇见你的那刻
				129201, 129202, 129211, 129212, #404 Not Found
				129301, 129302, 129311, 129312, #ArroganT
				129401, 129402, 129411, 129412, #樂園 - Atlantis
				]
			return songId in NCR

		def OldAprilFoolsDay(songId:int) -> bool:
			"""标记愚人节谱面"""
			OAFD = [
				]
			return songId in OAFD

		allSongData:dict[str,list] = SongName.SongNameData()
		removeIndexList:list[int] = list()
		self.__logger.debug("|  SongID  | SpeedStall | SyncNumber |         UploadScore        | PlayCount |  State  |")
		# 遍历列表
		for saveIndex, mapData in enumerate(SaveDataInfo.saveInfoList):
			mapInfo:MapInfo = GetSongName(mapData.SongId)
			if ((mapInfo is None) or (mapInfo.SongName == "")):
				mapData.State = "NoName"
				removeIndexList.insert(0,saveIndex)
			elif mapData.Isfav:
				self.FavSong.append(mapInfo.SongName)
				mapData.State = "Favo"
			elif OldAprilFoolsDay(mapData.SongId):
				mapData.State = "Fool"
			elif NoCopyright(mapData.SongId):
				mapData.State = "NoCR"
			self.__logger.debug(f'| {"%d"%mapData.SongId:>8} | {"%d"%mapData.SpeedStall:>10} | {"%.2f%%"%(mapData.SyncNumber/100):>10} | {"%.21f%%"%(mapData.UploadScore*100):>26} | {mapData.PlayCount:>9} | {mapData.State:>7} |')
			mapData.SetSongInfo(mapInfo)
			SaveDataInfo.saveInfoList[saveIndex] = mapData
		for removeIndex in removeIndexList:
			SaveDataInfo.saveInfoList.pop(removeIndex)
		self.__logger.debug("UserMemoryToJson End.")
		self.__logger.info("UserMemoryToJson Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000))

	def FavFix(self):
		"""修复收藏仅应用于每首歌的4KEZ谱面的问题"""
		startTime = time.perf_counter_ns()
		self.__logger.debug("FavFix Start.")
		# allSongData:dict[str,list] = SongName.SongNameData()
		self.__logger.debug(f"Favorites List：{self.FavSong}")
		for index, mapData in enumerate(SaveDataInfo.saveInfoList):
			if mapData.SongName in self.FavSong:
				SaveDataInfo.saveInfoList[index].State = "Favo"
		self.__logger.debug("FavFix End.")
		self.__logger.info("FavFix Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000))

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('savPath', nargs='?', default=None, help='Path to savedata.sav')
	args = parser.parse_args()

	savPath = args.savPath or os.path.join(Config.MainExecPath or '.', 'SavesDir', 'savedata.sav')

	Object = MUSYNCSavProcess(savPath)
	Object.Main()
