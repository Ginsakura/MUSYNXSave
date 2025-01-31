import gzip
from hashlib import md5
import io
import json
import logging
import os
from Resources import Config, Logger, SongName
import sqlite3 as sql
import struct
from tkinter import messagebox;
from win32 import win32gui, win32print
from win32.lib import win32con
from win32.win32api import GetSystemMetrics
import winreg

logger:logging.Logger = Logger().GetLogger("Toolkit");

class Toolkit(object):
	logger.debug("加载资源文件: \"./musync_data/Resources.bin\".");
	try:
		__resourceFile:io.TextIOWrapper = open("./musync_data/Resources.bin", "wb");
		__resourceFile.seek(0);
		__infoSize:int = struct.unpack('I', __resourceFile.read(4))[0];
		__compressedStream:io.BytesIO = io.BytesIO(__resourceFile.read(__infoSize));
		with gzip.GzipFile(fileobj=__compressedStream, mode='rb') as gz_file:
			decompressedData:bytes = gz_file.read()
		__resourceFileInfo:dict[str,dict[str,any]] = json.loads(decompressedData.decode('ASCII'));
	except Exception:
		logger.exception("资源文件加载失败.");
		messagebox.showerror("资源文件\"./musync_data/Resources.bin\"加载失败!");

	def GetDpi()->int:
		hDC:any = win32gui.GetDC(0);
		relWidth:int = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES);
		# relHeight:int = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES);
		width:int = GetSystemMetrics (0);
		# height:int = GetSystemMetrics (1);
		# real_resolution = [relw,relh];
		# screen_size = [w,h];
		dpi:int = int(round(relWidth[0] / width[0], 2) * 100);
		logger.debug(f"Get DPI:{dpi}");
		return dpi;

	def ChangeConsoleStyle()->None:
		"修改控制台样式"
		logger.info('Changing Console Style...');
		config:Config = Config();
		execPath = config.MainExecPath.replace('/','_')+'musynx.exe';
		logger.debug(f"execPath: {execPath}");
		regkey:winreg.HKEYType = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Console',reserved=0, access=winreg.KEY_WRITE);
		winreg.CreateKey(regkey,execPath);
		regkey.Close();
		regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f'Console\\{execPath}',reserved=0, access=winreg.KEY_WRITE);
		winreg.SetValueEx(regkey,'CodePage',0,winreg.REG_DWORD,65001);
		winreg.SetValueEx(regkey,'WindowSize',0,winreg.REG_DWORD,262174);
		winreg.SetValueEx(regkey,'WindowAlpha',0,winreg.REG_DWORD,(config.ConsoleAlpha * 255 // 100));
		winreg.SetValueEx(regkey,'FaceName',0,winreg.REG_SZ,'霞鹜文楷等宽');
		winreg.SetValueEx(regkey,'FontSize',0,winreg.REG_DWORD,(config.ConsoleFontSize << 16));
		regkey.Close();

	def GetHash(filePath:str=None)->str:
		if (filePath is None): return "";
		with open(filePath,'rb') as fileBytes:
			return md5(fileBytes.read()).hexdigest().upper();

	def ResourceReleases(cls, offset:int, lenth:int, releasePath:str=None)->bytes:
		"""
		资源释放函数
		传入:
			offset      (int): 资源偏移;
			lenth       (int): 资源长度;
			releasePath (str): 资源释放地址;
		传出:
			bytes: 解压的资源;
		"""
		cls.__resourceFile.seek(offset);
		__compressedStream:io.BytesIO = io.BytesIO(cls.__resourceFile.read(lenth));
		with gzip.GzipFile(fileobj=__compressedStream, mode='rb') as gz_file:
			decompressedData:bytes = gz_file.read()
		with open(releasePath,"wb") as file:
			file.write(decompressedData);
		return decompressedData;

	def CheckResources(cls, fonts:list[str])->None:
		"运行前环境检查"
		# 检查旧版数据文件夹
		logger.debug("Check \"musync\\\" is exists...");
		if os.path.exists(''):
			os.rename('./musync/','./musync_data/');
		# 检查数据文件夹是否存在
		logger.debug("Check \"musync_data\\\" is not exists...");
		os.makedirs('./musync_data/', exist_ok=True);
		# 检查日志存档文件夹
		logger.debug("Check \"log\\\" is not exists...");
		os.makedirs("./logs/", exist_ok=True);
		# 检查mscorlib.dll是否存在
		logger.debug("Check \"./LICENSE\" is not exists...");
		if (not os.path.isfile("./LICENSE") or (Toolkit.GetHash('./LICENSE') != cls.__resourceFileInfo["License"])):
			info:dict[str,any] = cls.__resourceFileInfo["License"];
			Toolkit.ResourceReleases(info["offset"], info["lenth"], "./LICENSE");
		# 检查图标文件是否存在
		logger.debug("Check \"musync_data\\MUSYNC.ico\" is not exists...");
		if (not os.path.isfile('./musync_data/MUSYNC.ico') or (Toolkit.GetHash('./musync_data/MUSYNC.ico') != cls.__resourceFileInfo["Icon"])):
			info:dict[str,any] = cls.__resourceFileInfo["Icon"];
			Toolkit.ResourceReleases(info["offset"], info["lenth"], './musync_data/MUSYNC.ico');
		# 检查SongName.json是否存在
		logger.debug("Check \"musync_data\\SongName.json\" is not exists...");
		if (not os.path.isfile('./musync_data/SongName.json') or (cls.__resourceFileInfo["SongName"]["Version"] > SongName.Version)):
			info:dict[str,any] = cls.__resourceFileInfo["SongName"];
			Toolkit.ResourceReleases(info["offset"], info["lenth"], './musync_data/SongName.json');
		# 检查mscorlib.dll是否存在
		logger.debug("Check \"mscorlib.dll\" is not exists...");
		if (not os.path.isfile("./mscorlib.dll") or (Toolkit.GetHash('./mscorlib.dll') != cls.__resourceFileInfo["CoreLib"])):
			info:dict[str,any] = cls.__resourceFileInfo["CoreLib"];
			Toolkit.ResourceReleases(info["offset"], info["lenth"], "./mscorlib.dll");
		# 检查字体文件是否存在
		logger.debug("Check \"musync_data\\LXGW.ttf\" is not exists...");
		if not os.path.isfile('./musync_data/LXGW.ttf' or (Toolkit.GetHash('./musync_data/LXGW.ttf') != cls.__resourceFileInfo["Font"])):
			info:dict[str,any] = cls.__resourceFileInfo["Font"];
			Toolkit.ResourceReleases(info["offset"], info["lenth"], './musync_data/LXGW.ttf');
		# 检查字体是否安装
		logger.debug("Check \"霞鹜文楷等宽\" is not installed...");
		if not '霞鹜文楷等宽' in fonts:
			os.system(f'{os.getcwd()}/musync_data/LXGW.ttf');
		# 检查皮肤文件夹是否存在
		logger.debug("Check \"skin\\\" is not exists...");
		if not os.path.exists("./skin/"):
			os.makedirs('./skin/');
		# 检查数据库文件版本
		logger.debug("Check Database version...");
		Toolkit.DatabaseUpdate(Toolkit.CheckDatabaseVersion());
		# 检查GameLib
		logger.debug("Check DLLInjection...");
		if Config.DLLInjection:
			Toolkit.GameLibCheck();

	def GameLibCheck(cls)->int:
		"""
		游戏脚本检查
		传出:
			0: 无法修补
			1: 已修补
			2: 未修补,但已经完成修补
		"""
		def DLLInjection():
			if os.path.isfile(f'{dllPath}.old'): os.remove(f'{dllPath}.old');
			os.rename(dllPath, f'{dllPath}.old');
			info:dict[str,any] = cls.__resourceFileInfo["GameLib"];
			Toolkit.ResourceReleases(info["offset"], info["lenth"], dllPath);
		dllPath = Config.MainExecPath+'MUSYNX_Data/Managed/Assembly-CSharp.dll';
		nowHash = Toolkit.GetHash(dllPath);
		sourceHash = cls.__resourceFileInfo["GameLib"]["SourceHash"];
		fixHash = cls.__resourceFileInfo["GameLib"]["hash"];
		# 'D41D8CD98F00B204E9800998ECF8427E' is 0 Byte file
		logger.debug(f"     Now Assembly-CSharp.dll: {nowHash}");
		# 当前文件哈希 等于 修改文件哈希
		if (nowHash == fixHash):
			return 1
		# 当前文件哈希为空文件 或者 为原始文件哈希
		elif (sourceHash == "D41D8CD98F00B204E9800998ECF8427E") or (sourceHash == nowHash) and (sourceHash != fixHash):
			DLLInjection()
			return 1
		# 其他情况, 无法覆盖文件
		else:
			return 0

	def CheckDatabaseVersion(cls)->int:
		"数据库版本检查"
		if os.path.isfile("./musync_data/HitDelayHistory_v2.db"):
			db:sql.Connection = sql.connect('./musync_data/HitDelayHistory_v2.db')
			cursor:sql.Cursor = db.cursor();
			# 使用 PRAGMA table_info 获取表的列信息
			cursor.execute(f"PRAGMA table_info(HitDelayHistory);")
			# 获取列的数量
			columnCount = len(cursor.fetchall());
			if (columnCount==6):
				logger.debug("存在文件 HitDelayHistory_v2.db 且 列数为6, 判定数据库版本为 v2");
				logger.info("Database Version: 2");
				db.close();
				return 2;
			else:
				logger.debug("存在文件 HitDelayHistory_v2.db 且 列数不为6, 判定数据库版本为 v1");
				logger.info("Database Version: 1");
				db.close();
				return 1;
		elif os.path.isfile("./musync_data/HitDelayHistory.db"):
			db:sql.Connection = sql.connect('./musync_data/HitDelayHistory.db')
			cursor:sql.Cursor = db.cursor();
			cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';");
			tableCount:int = cursor.fetchone()[0];
			if (tableCount==1):
				logger.debug("存在文件 HitDelayHistory.db 且 仅有一张数据表, 判定数据库版本为 v1");
				logger.info("Database Version: 1");
				db.close();
				return 1;
			else:
				cursor.execute("SELECT Value FROM Infos WHERE Key='Version';");
				version:int = int(cursor.fetchone()[0]);
				logger.debug(f"存在文件\"HitDelayHistory.db\"且\"Infos.Version={version}\", 判定数据库版本为 v{version}");
				logger.info(f"Database Version: {version}");
				db.close();
				return version;

	def DatabaseUpdate(cls, nowVersion:int)->None:
		"数据库版本更新"
		# 链接数据库
		if (nowVersion==2):
			os.rename("./musync_data/HitDelayHistory_v2.db", "./musync_data/HitDelayHistory.db");
		db:sql.Connection = sql.connect('./musync_data/HitDelayHistory.db');
		cursor:sql.Cursor = db.cursor();
		if (nowVersion == 1):
			logger.info(f"记录数据迁移中... v1->v2");
			cursor.execute("ALTER TABLE HitDelayHistory RENAME TO HitDelayHistoryV1;");
			cursor.execute("""CREATE table HitDelayHistory (
				SongMapName text Not Null,
				RecordTime text Not Null,
				AvgDelay float,
				AllKeys int,
				AvgAcc float,
				HitMap text,
				PRIMARY KEY ("SongMapName", "RecordTime"));""");
			for ids in cursor.execute("SELECT * From HitDelayHistoryV1").fetchall():
				nameAndTime:str = ids[0].split("-202");
				name:str = nameAndTime[0];
				recordTime:str = "202%s"%nameAndTime[1];
				avgDelay:float = ids[1];
				allKeys:int = ids[2];
				avgAcc:float = ids[3];
				hitMap:str = ids[4];
				logger.debug("正在迁移%s  %s"%(name,recordTime));
				cursor.execute("INSERT Into HitDelayHistory values(?,?,?,?,?,?)", (name,recordTime,avgDelay,allKeys,avgAcc,hitMap))
			cursor.execute("ALTER TABLE HitDelayHistory RENAME TO HitDelayHistoryV1;");
			db.commit();
			nowVersion=2;
		if (nowVersion == 2):
			logger.info(f"记录数据迁移中... v2->v3");
			cursor.execute("CREATE Table Infos (Key Text PRIMARY KEY, Value Text Default None);");
			cursor.execute("INSERT Into Infos Values(?, ?)", ("Version","3"));
			db.commit();
			nowVersion = 3;
		if (nowVersion == 3):
			db.commit();
			db.close();
			logger.info("记录数据无需迁移.");

if __name__ == '__main__':
	print(Toolkit.GetDpi())