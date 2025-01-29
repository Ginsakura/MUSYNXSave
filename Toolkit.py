
import logging
import os
import shutil
import sqlite3 as sql
import sys
import winreg
from win32 import win32gui, win32print
from win32.lib import win32con
from win32.win32api import GetSystemMetrics
from Resources import Config, Logger, SongName

logger:logging.Logger = Logger().GetLogger("Toolkit");
SongNameJsonUpdate:int = 20250126;

class Toolkit(object):
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

	def GetResourcePath(relativePath:str)->str:
		"""获取资源文件在临时目录中的绝对路径"""
		try:
			# 如果是打包后的单文件模式，使用 _MEIPASS
			base_path:str = sys._MEIPASS;
		except AttributeError:
			# 如果是正常运行模式，使用当前文件夹
			base_path:str = os.path.abspath(".");
		return os.path.join(base_path, relativePath);

	def EnsureResourceInRuntimeDirectory(relativePath:str)->None:
		"""确保资源文件存在于运行目录中"""
		sourcePath:str = Toolkit.GetResourcePath(relativePath);  # 获取临时目录中的资源路径
		destinationPath:str = os.path.join(os.getcwd(), relativePath);  # 获取运行目录中的目标路径

		# 检查资源文件是否已经存在于运行目录
		if not os.path.exists(destinationPath):
			logger.info(f"资源文件 {relativePath} 不存在于运行目录，正在复制...");
			# 确保目标目录存在
			os.makedirs(os.path.dirname(destinationPath), exist_ok=True);
			# 复制文件
			shutil.copy2(sourcePath, destinationPath);
			logger.info(f"资源文件已复制到 {destinationPath}");
		else:
			logger.info(f"资源文件 {relativePath} 已存在于运行目录，无需复制");

	def CheckResources(fonts)->None:
		"运行前环境检查"
		# 检查旧版数据文件夹
		if os.path.exists('./musync/'):
			os.rename('./musync/','./musync_data/');
		# 检查数据文件夹是否存在
		if not os.path.exists('./musync_data/'):
			os.makedirs('./musync_data/');
		# 检查日志存档文件夹
		if not os.path.isdir("./logs/"):
			os.makedirs("./logs/");
		# 检查图标文件是否存在
		if not os.path.isfile('./musync_data/MUSYNC.ico'):
			Toolkit.EnsureResourceInRuntimeDirectory("musync_data/MUSYNC.ico");
		# 检查SongName.json是否存在
		if (not os.path.isfile('./musync_data/SongName.json') or (SongNameJsonUpdate > SongName.Version())):
			Toolkit.EnsureResourceInRuntimeDirectory('musync_data/SongName.json');
		# 检查字体文件是否存在
		if not os.path.isfile('./musync_data/LXGW.ttf'):
			Toolkit.EnsureResourceInRuntimeDirectory("musync_data/LXGW.ttf");
		# 检查字体是否安装
		if not '霞鹜文楷等宽' in fonts:
			os.system(f'{os.getcwd()}/musync_data/LXGW.ttf');
		# 检查皮肤文件夹是否存在
		if not os.path.exists("./skin/"):
			os.makedirs('./skin/');
		# 检查数据库文件版本
		Toolkit.DatabaseUpdate(Toolkit.CheckDatabaseVersion());

	def CheckDatabaseVersion()->int:
		"数据库版本检查"
		def ResourceRelease()->None:
			db.close();
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
				ResourceRelease();
				return 2;
			else:
				logger.debug("存在文件 HitDelayHistory_v2.db 且 列数不为6, 判定数据库版本为 v1");
				logger.info("Database Version: 1");
				ResourceRelease();
				return 1;
		elif os.path.isfile("./musync_data/HitDelayHistory.db"):
			db:sql.Connection = sql.connect('./musync_data/HitDelayHistory.db')
			cursor:sql.Cursor = db.cursor();
			cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';");
			tableCount:int = cursor.fetchone()[0];
			if (tableCount==1):
				logger.debug("存在文件 HitDelayHistory.db 且 仅有一张数据表, 判定数据库版本为 v1");
				logger.info("Database Version: 1");
				ResourceRelease();
				return 1;
			else:
				cursor.execute("SELECT Value FROM Infos WHERE Key='Version';");
				version:int = int(cursor.fetchone()[0]);
				logger.debug(f"存在文件\"HitDelayHistory.db\"且\"Infos.Version={version}\", 判定数据库版本为 v{version}");
				logger.info(f"Database Version: {version}");
				ResourceRelease();
				return version;

	def DatabaseUpdate(nowVersion:int)->None:
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