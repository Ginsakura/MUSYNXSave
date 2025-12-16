import gzip
from hashlib import sha256
import io
import json
import logging
import os
from Resources import Config, Logger, SongName
import sqlite3 as sql
import struct
import time
from tkinter import messagebox
from win32 import win32gui, win32print
from win32.lib import win32con
from win32.win32api import GetSystemMetrics
import winreg

logger:logging.Logger = Logger().GetLogger("Toolkit")

class Toolkit(object):
	logger.debug("加载资源文件: \"./musync_data/Resources.bin\".")
	__resourceFileInfo:dict[str,dict[str,any]] = {}
	__isResourceFileInfoLoaded:bool = False
	try:
		__resourceFile:io.TextIOWrapper = open("./musync_data/Resources.bin", "rb")
		__resourceFile.seek(0)
		__infoSize:int = struct.unpack('I', __resourceFile.read(4))[0]
		__compressedStream:io.BytesIO = io.BytesIO(__resourceFile.read(__infoSize))
		with gzip.GzipFile(fileobj=__compressedStream, mode='rb') as gz_file:
			decompressedData:bytes = gz_file.read()
		__resourceFileInfo:dict[str,dict[str,any]] = json.loads(decompressedData.decode('ASCII'))
		__isResourceFileInfoLoaded = True
	except Exception as ex:
		logger.exception("资源文件加载失败.")
		messagebox.showerror("Error",f"资源文件\"./musync_data/Resources.bin\"加载失败!\n{ex}")

	@staticmethod
	def GetDpi()->int:
		""" get system dpi"""
		startTime:int = time.perf_counter_ns()
		hDC = win32gui.GetDC(0)
		try:
			relWidth:int = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
			width:int = GetSystemMetrics(0)
			dpi:int = int(round(relWidth / width, 2) * 100)
		finally:
			win32gui.ReleaseDC(0, hDC)
		logger.debug(f"Get DPI:{dpi}")
		logger.debug(f"GetDPI Run Time: {(time.perf_counter_ns() - startTime)/1000000} ms")
		return dpi; # e.g. 100 -> 100%

	@staticmethod
	def ChangeConsoleStyle()->None:
		"""修改控制台样式"""
		startTime:int = time.perf_counter_ns()
		logger.info('Changing Console Style...')
		config:Config = Config()
		if not config.MainExecPath:
			Toolkit.GetSaveFile()
		if not config.MainExecPath:
			logger.error('Not Have Config.MainExecPath!')
			return
		execPath = config.MainExecPath.replace('/','_')+'musynx.exe'
		logger.debug(f"execPath: {execPath}")
		regkey:winreg.HKEYType = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Console',reserved=0, access=winreg.KEY_WRITE)
		winreg.CreateKey(regkey,execPath)
		regkey.Close()
		regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f'Console\\{execPath}',reserved=0, access=winreg.KEY_WRITE)
		winreg.SetValueEx(regkey,'CodePage',0,winreg.REG_DWORD,65001)
		winreg.SetValueEx(regkey,'WindowSize',0,winreg.REG_DWORD,262174)
		winreg.SetValueEx(regkey,'WindowAlpha',0,winreg.REG_DWORD,(config.ConsoleAlpha * 255 // 100))
		winreg.SetValueEx(regkey,'FaceName',0,winreg.REG_SZ,'霞鹜文楷等宽')
		winreg.SetValueEx(regkey,'FontSize',0,winreg.REG_DWORD,(config.ConsoleFontSize << 16))
		regkey.Close()
		logger.debug(f"ChangeConsoleStyle() Run Time: {(time.perf_counter_ns() - startTime)/1000000} ms")

	@staticmethod
	def GetHash(filePath:str|None=None)->str:
		"""获取文件哈希值
		
		"""
		startTime:int = time.perf_counter_ns()
		if (filePath is None): return ""
		with open(filePath,'rb') as fileBytes:
			hashResult:str = sha256(fileBytes.read()).hexdigest().upper()
		logger.debug(f"GetHash() Run Time: {(time.perf_counter_ns() - startTime)/1000000} ms")
		return hashResult

	@classmethod
	def ResourceReleases(cls, offset:int, lenth:int, releasePath:str=None)->bytes:
		"""
		资源释放函数
		传入:
			offset      (int): 资源偏移
			lenth       (int): 资源长度
			releasePath (str): 资源释放地址
		传出:
			bytes: 解压的资源
		"""
		startTime:int = time.perf_counter_ns()
		cls.__resourceFile.seek(offset)
		__compressedStream:io.BytesIO = io.BytesIO(cls.__resourceFile.read(lenth))
		with gzip.GzipFile(fileobj=__compressedStream, mode='rb') as gz_file:
			decompressedData:bytes = gz_file.read()
		if releasePath is not None:
			with open(releasePath,"wb") as file:
				file.write(decompressedData)
		logger.debug(f"ResourceReleases() Run Time: {(time.perf_counter_ns() - startTime)/1000000} ms")
		return decompressedData

	@classmethod
	def CheckResources(cls, fonts:list[str])->None:
		"""运行前环境检查"""
		startTime:int = time.perf_counter_ns()
		# 检查旧版数据文件夹
		logger.debug("Check \"musync\\\" is exists...")
		if os.path.exists('./musync/'):
			os.rename('./musync/','./musync_data/')
		# 检查数据文件夹是否存在
		logger.debug("Check \"musync_data\\\" is not exists...")
		os.makedirs('./musync_data/', exist_ok=True)
		# 检查日志存档文件夹
		logger.debug("Check \"log\\\" is not exists...")
		os.makedirs("./logs/", exist_ok=True)
		# 检查资源文件
		if cls.__isResourceFileInfoLoaded:
			# 检查LICENSE是否存在
			logger.debug("Check if the \"./LICENSE\" is exists...")
			if (not os.path.isfile("./LICENSE") or (Toolkit.GetHash('./LICENSE') != cls.__resourceFileInfo["License"]["hash"])):
				info:dict[str,any] = cls.__resourceFileInfo["License"]
				Toolkit.ResourceReleases(info["offset"], info["lenth"], "./LICENSE")
			# 检查图标文件是否存在
			logger.debug("Check if the \"musync_data\\MUSYNC.ico\" is exists...")
			if (not os.path.isfile('./musync_data/MUSYNC.ico') or (Toolkit.GetHash('./musync_data/MUSYNC.ico') != cls.__resourceFileInfo["Icon"]["hash"])):
				info:dict[str,any] = cls.__resourceFileInfo["Icon"]
				Toolkit.ResourceReleases(info["offset"], info["lenth"], './musync_data/MUSYNC.ico')
			# 检查SongName.json是否存在
			logger.debug("Check if the \"musync_data\\SongName.json\" is exists...")
			if (not os.path.isfile('./musync_data/SongName.json') or (cls.__resourceFileInfo["SongName"]["Version"] > SongName.Version())):
				info:dict[str,any] = cls.__resourceFileInfo["SongName"]
				Toolkit.ResourceReleases(info["offset"], info["lenth"], './musync_data/SongName.json')
			# 检查mscorlib.dll是否存在
			logger.debug("Check if the \"mscorlib.dll\" is exists...")
			if (not os.path.isfile("./mscorlib.dll") or (Toolkit.GetHash('./mscorlib.dll') != cls.__resourceFileInfo["CoreLib"]["hash"])):
				info:dict[str,any] = cls.__resourceFileInfo["CoreLib"]
				Toolkit.ResourceReleases(info["offset"], info["lenth"], "./mscorlib.dll")
			# 检查字体文件是否存在
			logger.debug("Check if the \"musync_data\\LXGW.ttf\" is exists...")
			if not os.path.isfile('./musync_data/LXGW.ttf') or (Toolkit.GetHash('./musync_data/LXGW.ttf') != cls.__resourceFileInfo["Font"]["hash"]):
				info:dict[str,any] = cls.__resourceFileInfo["Font"]
				Toolkit.ResourceReleases(info["offset"], info["lenth"], './musync_data/LXGW.ttf')
			# 检查字体是否安装
			logger.debug("Check if the \"霞鹜文楷等宽\" font is installed...")
			if '霞鹜文楷等宽' not in fonts:
				os.startfile(os.path.join(os.getcwd(), 'musync_data', 'LXGW.ttf'))
		# 检查皮肤文件夹是否存在
		logger.debug("Check if the \"skin\\\" is exists...")
		if not os.path.exists("./skin/"):
			os.makedirs('./skin/')
		# 检查数据库文件版本
		logger.debug("Check Database version...")
		Toolkit.DatabaseUpdate(Toolkit.CheckDatabaseVersion())
		# 检查GameLib
		logger.debug("Check DLLInjection...")
		if Config.DLLInjection:
			Toolkit.GameLibCheck()
		logger.debug(f"CheckResources() Run Time: {(time.perf_counter_ns() - startTime)/1000000} ms")

	@classmethod
	def GetSaveFile(cls)->str:
		"""搜索预设存档目录"""
		startTime:int = time.perf_counter_ns()
		logger.debug("正在搜索存档文件中……")
		saveFilePath:str = None
		for ids in "DEFCGHIJKLMNOPQRSTUVWXYZAB":
			if os.path.isfile(f'{ids}:\\Program Files\\steam\\steamapps\\common\\MUSYNX\\musynx.exe'):
				saveFilePath:str = f"{ids}:\\Program Files\\steam\\steamapps\\common\\MUSYNX\\"
				break
			elif os.path.isfile(f'{ids}:\\SteamLibrary\\steamapps\\common\\MUSYNX\\musynx.exe'):
				saveFilePath:str = f"{ids}:\\SteamLibrary\\steamapps\\common\\MUSYNX\\"
				break
			elif os.path.isfile(f'{ids}:\\steam\\steamapps\\common\\MUSYNX\\musynx.exe'):
				saveFilePath:str = f"{ids}:\\steam\\steamapps\\common\\MUSYNX\\"
				break
		else:
			logger.error("搜索不到存档文件.")
			logger.info("GetSaveFile() Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000))
			return ""
		logger.debug(f"SaveFilePath: {saveFilePath}")
		Config.MainExecPath = saveFilePath
		Config.SaveConfig()
		return saveFilePath

	@classmethod
	def GameLibCheck(cls)->int:
		"""
		游戏脚本检查
		传出:
			0: 无法修补
			1: 已修补
			2: 未修补,但已经完成修补
		"""
		def DLLInjection():
			"""备份并修补"""
			if os.path.isfile(f'{dllPath}.old'): os.remove(f'{dllPath}.old')
			os.rename(dllPath, f'{dllPath}.old')
			info:dict[str,any] = cls.__resourceFileInfo["GameLib"]
			Toolkit.ResourceReleases(info["offset"], info["lenth"], dllPath)

		startTime:int = time.perf_counter_ns()
		dllPath = Config.MainExecPath+'MUSYNX_Data/Managed/Assembly-CSharp.dll'
		if not os.path.isfile(dllPath):
			logger.error(f"Assembly-CSharp.dll not found at \"{dllPath}\", skip DLLInjection.")
			logger.debug(f"GameLibCheck() Run Time: {(time.perf_counter_ns() - startTime)/1000000} ms")
			return 0
		nowHash = Toolkit.GetHash(dllPath)
		sourceHash = cls.__resourceFileInfo["GameLib"]["SourceHash"]
		fixHash = cls.__resourceFileInfo["GameLib"]["hash"]
		# 'D41D8CD98F00B204E9800998ECF8427E' is 0 Byte file
		logger.debug(f"     Now Assembly-CSharp.dll: {nowHash}")
		# 当前文件哈希 等于 修改文件哈希
		# 其他情况, 无法覆盖文件
		rtcode:int = 0
		if (nowHash == fixHash):
			rtcode = 1
		# 当前文件哈希为空文件 或者 为原始文件哈希
		elif (sourceHash == "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855") or ((sourceHash == nowHash) and (sourceHash != fixHash)):
			DLLInjection()
			rtcode = 1
		logger.debug(f"GameLibCheck() Run Time: {(time.perf_counter_ns() - startTime)/1000000} ms")
		return rtcode

	@classmethod
	def CheckDatabaseVersion(cls)->int:
		"数据库版本检查"
		startTime:int = time.perf_counter_ns()
		rtcode:int = -1
		if os.path.isfile("./musync_data/HitDelayHistory_v2.db"):
			db:sql.Connection = sql.connect('./musync_data/HitDelayHistory_v2.db')
			cursor:sql.Cursor = db.cursor()
			# 使用 PRAGMA table_info 获取表的列信息
			cursor.execute("PRAGMA table_info(HitDelayHistory);")
			# 获取列的数量
			columnCount:int = len(cursor.fetchall())
			if (columnCount==6):
				logger.debug("存在文件 HitDelayHistory_v2.db 且 列数为6, 判定数据库版本为 v2")
				logger.info("Database Version: 2")
				db.close()
				rtcode = 2
			else:
				logger.debug("存在文件 HitDelayHistory_v2.db 且 列数不为6, 判定数据库版本为 v1")
				logger.info("Database Version: 1")
				db.close()
				rtcode = 1
		elif os.path.isfile("./musync_data/HitDelayHistory.db"):
			db:sql.Connection = sql.connect('./musync_data/HitDelayHistory.db')
			cursor:sql.Cursor = db.cursor()
			cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
			tableCount:int = cursor.fetchone()[0]
			if (tableCount==1):
				logger.debug("存在文件 HitDelayHistory.db 且 仅有一张数据表, 判定数据库版本为 v1")
				logger.info("Database Version: 1")
				db.close()
				rtcode = 1
			else:
				cursor.execute("SELECT Value FROM Infos WHERE Key='Version';")
				version:int = int(cursor.fetchone()[0])
				logger.debug(f"存在文件\"HitDelayHistory.db\"且\"Infos.Version={version}\", 判定数据库版本为 v{version}")
				logger.info(f"Database Version: {version}")
				db.close()
				rtcode = version
		else:
			logger.warning("无数据库文件存在.")
			rtcode = 0
		if (rtcode == -1):
			logger.fatal(">>> CheckDatabaseVersion()函数出现严重异常! 函数未能完成执行! <<<")
		logger.debug(f"CheckDatabaseVersion() Run Time: {(time.perf_counter_ns() - startTime)/1000000} ms")
		return rtcode

	@classmethod
	def DatabaseUpdate(cls, nowVersion:int)->None:
		"数据库版本更新"
		startTime:int = time.perf_counter_ns()
		LastVersion:int = 3
		# 链接数据库
		if (nowVersion==2):
			os.rename("./musync_data/HitDelayHistory_v2.db", "./musync_data/HitDelayHistory.db")
		db:sql.Connection = sql.connect('./musync_data/HitDelayHistory.db')
		cursor:sql.Cursor = db.cursor()
		if (nowVersion == 0):
			logger.info(f"创建v{LastVersion}版本数据库中...")
			cursor.execute("""CREATE table IF NOT EXISTS HitDelayHistory (
				SongMapName text Not Null,
				RecordTime text Not Null,
				AvgDelay float,
				AllKeys int,
				AvgAcc float,
				HitMap text,
				PRIMARY KEY ("SongMapName", "RecordTime"));""")
			cursor.execute("CREATE Table IF NOT EXISTS Infos (Key Text PRIMARY KEY, Value Text Default None);")
			cursor.execute("INSERT Into Infos Values(?, ?)", ("Version","%d"%LastVersion))
			db.commit()
			db.close()
			return
		if (nowVersion == 1):
			logger.info("记录数据迁移中... v1->v2")
			cursor.execute("ALTER TABLE HitDelayHistory RENAME TO HitDelayHistoryV1;")
			cursor.execute("""CREATE table IF NOT EXISTS HitDelayHistory (
				SongMapName text Not Null,
				RecordTime text Not Null,
				AvgDelay float,
				AllKeys int,
				AvgAcc float,
				HitMap text,
				PRIMARY KEY ("SongMapName", "RecordTime"));""")
			for ids in cursor.execute("SELECT * From HitDelayHistoryV1").fetchall():
				nameAndTime:str = ids[0].split("-202")
				name:str = nameAndTime[0]
				recordTime:str = "202%s"%nameAndTime[1]
				avgDelay:float = ids[1]
				allKeys:int = ids[2]
				avgAcc:float = ids[3]
				hitMap:str = ids[4]
				logger.debug("正在迁移%s  %s"%(name,recordTime))
				cursor.execute("INSERT Into HitDelayHistory values(?,?,?,?,?,?)", (name,recordTime,avgDelay,allKeys,avgAcc,hitMap))
			# cursor.execute("ALTER TABLE HitDelayHistory RENAME TO HitDelayHistoryV1;")
			db.commit()
			nowVersion=2
		if (nowVersion == 2):
			logger.info("记录数据迁移中... v2->v3")
			cursor.execute("CREATE Table IF NOT EXISTS Infos (Key Text PRIMARY KEY, Value Text Default None);")
			cursor.execute("INSERT Into Infos Values(?, ?)", ("Version","3"))
			db.commit()
			nowVersion = 3
		if (nowVersion == 3):
			db.commit()
			db.close()
			logger.info("记录数据无需迁移.")
		logger.debug(f"DatabaseUpdate() Run Time: {(time.perf_counter_ns() - startTime)/1000000} ms")

if __name__ == '__main__':
	print(Toolkit.GetDpi())