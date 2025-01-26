import gzip
import json
import logging
import os
import shutil
import threading


class SongName(object):
	"存储SongName.json,单例";
	__instance = None;
	__lock:threading.Lock = threading.Lock();

	def __new__(cls):
		with cls.__lock:
			if not cls.__instance:
				cls.__instance = super(SongName, cls).__new__(cls)

		return cls.__instance

	def __init__(self) -> None:
		self.__data:dict[str,list|int]	= None;
		self.__filePath:str				= os.getcwd()+"/musync_data/SongName.json";
		self.__logger:logging.Logger	= Logger().GetLogger("Resources.SongName");
		self.__logger.info("creating an instance in Resources.SongName");
		self.LoadFile();

	@property
	def SongNameData(self)->str: return self.__data;

	@property
	def Update(self)->int: return self.__data["update"];

	@property
	def FilePath(self)->str: return self.__filePath;
	# @FilePath.setter
	# def FilePath(self, value:str): self.__filePath = value; self.LoadFile();

	def LoadFile(self)->None:
		"加载配置文件,自动执行";
		if not os.path.isfile(self.__filePath):
			self.__logger.error(f"file: \"{self.__filePath}\" not exists.");
			self.__data = None;
			return;
		with open(self.__filePath,'r',encoding='utf8') as songNameFile:
			try:
				self.__data:dict[str,list] = json.load(songNameFile);
			except Exception:
				self.__logger.exception(f"file: \"{self.__filePath}\" load failure.");
			else:
				self.__logger.info(f"file: \"{self.__filePath}\" loaded.");

class Config(object):
	"从bootcfg.json读取配置信息,单例";
	def CompressLogFile()->None:
		logsDir:str		= "./logs/";
		logsName:str	= "log.gz";
		logName:str		= "log.txt";
		# 移动压缩文件到 logs 目录
		shutil.move(f"./{logName}", logsDir+logName);
		# 获取已有的压缩文件数量
		nextIndex:int = len([f for f in os.listdir(logsDir)]);
		# 压缩 log.txt 文件
		with open(logsDir+logName, 'rb') as f_in:
			with gzip.open(f"{logsDir}{logsName}.{nextIndex}", 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out);
		# 清理 log.txt 文件
		os.remove(logsDir+logName);
	__instance = None;
	__lock:threading.Lock = threading.Lock();
	if (os.path.isfile("./log.txt")):CompressLogFile();
	__logger:logging.Logger = logging.getLogger("Resources.Config");
	__file:logging.FileHandler = logging.FileHandler("./log.txt");
	__file.setLevel(logging.DEBUG);
	__file.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'));
	__console:logging.StreamHandler = logging.StreamHandler();
	__console.setLevel(logging.DEBUG);
	__console.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'));
	__logger.addHandler(__file);
	__logger.addHandler(__console);

	def __new__(cls):
		with cls.__lock:
			if not cls.__instance:
				cls.__instance = super(Config, cls).__new__(cls)
		return cls.__instance

	def __init__(self) -> None:
		self.__filePath:str					= os.getcwd()+"/musync_data/bootcfg.json";
		self.__logger.info("creating an instance in Resources.Config");
		self.Version:str					= None;
		self.LoggerFilter:str				= "Info";
		self.Acc_Sync:bool					= False;
		self.CheckUpdate:bool				= True;
		self.AnalyzeWhenStarting:bool		= False;
		self.DLLInjection:bool				= False;
		self.SystemDPI:int					= 100;
		self.DonutChartinHitDelay:bool		= True;
		self.DonutChartinAllHitAnalyze:bool	= True;
		self.NarrowDelayInterval:bool		= True;
		self.ConsoleAlpha:int				= 75;
		self.ConsoleFont:str				= "霞鹜文楷等宽";
		self.ConsoleFontSize:int			= 36;
		self.MainExecPath:str				= None;
		self.ChangeConsoleStyle:bool		= True;
		self.FramelessWindow:bool			= False;
		self.TransparentColor:str			= "#FFFFFF";
		self.Default4Keys:bool				= False;
		self.DefaultDiffcute:int			= 0;
		self.LoadConfig();

	# def __repr__(self):
	# 	pass

	@property
	def FilePath(self)->str: return self.__filePath;
	# @FilePath.setter
	# def FilePath(self, value:str): self.__filePath = value; self.LoadFile();

	def LoadConfig(self)->None:
		"读取配置文件,自动执行";
		if not os.path.isfile(self.__filePath):
			self.__logger.error(f"file: \"{self.__filePath}\" not exists.");
			return;
		with open(self.__filePath,'r',encoding='utf8') as configFile:
			try:
				config:dict[str,any] = json.load(configFile);
				# 动态将字典的键值对赋值给类的属性
				for key, value in config.items():
					setattr(self, key, value)
			except Exception:
				self.__logger.exception(f"file: \"{self.__filePath}\" load failure.");
			else:
				self.__logger.info(f"file: \"{self.__filePath}\" loaded.");

	def SaveConfig(self) -> None:
		"保存配置文件,手动执行";
		# 获取所有需要保存的属性
		config_data = {
			"Version": self.Version,
			"LoggerFilter" : self.LoggerFilter,
			"Acc_Sync": self.Acc_Sync,
			"CheckUpdate": self.CheckUpdate,
			"AnalyzeWhenStarting": self.AnalyzeWhenStarting,
			"DLLInjection": self.DLLInjection,
			"SystemDPI": self.SystemDPI,
			"DonutChartinHitDelay": self.DonutChartinHitDelay,
			"DonutChartinAllHitAnalyze": self.DonutChartinAllHitAnalyze,
			"NarrowDelayInterval": self.NarrowDelayInterval,
			"ConsoleAlpha": self.ConsoleAlpha,
			"ConsoleFont": self.ConsoleFont,
			"ConsoleFontSize": self.ConsoleFontSize,
			"MainExecPath": self.MainExecPath,
			"ChangeConsoleStyle": self.ChangeConsoleStyle,
			"FramelessWindow": self.FramelessWindow,
			"TransparentColor": self.TransparentColor,
			"Default4Keys": self.Default4Keys,
			"DefaultDiffcute": self.DefaultDiffcute
		}
		# 确保文件夹存在
		os.makedirs(os.path.dirname(self.__filePath), exist_ok=True)
		# 保存为 JSON 文件
		try:
			with open(self.__filePath, 'w', encoding='utf8') as configFile:
				json.dump(config_data, configFile, ensure_ascii=False, indent=4)
			self.__logger.info(f"Configuration saved to \"{self.__filePath}\" successfully.")
		except Exception as e:
			self.__logger.exception(f"Failed to save configuration to \"{self.__filePath}\": {e}")

class SaveDataInfo(object):
	"存储存档数据,单例"
	__instance = None;
	__lock:threading.Lock = threading.Lock();

	def __new__(cls):
		with cls.__lock:
			if not cls.__instance:
				cls.__instance = super(SaveDataInfo, cls).__new__(cls)
		return cls.__instance

	def __init__(self):
		super(SaveDataInfo, self).__init__()
		self.__logger:logging.Logger		= Logger().GetLogger(name="Resources.SaveDataInfo");
		self.__logger.info("creating an instance in Resources.SaveDataInfo");
		self.version:int					= None;
		self.AppVersion:int					= None;
		self.saveInfoList:list[MapDataInfo]	= list();
		self.purchaseIds:list[str]			= list();
		self.crc:int						= None;
		# self.instance						= None;
		self.saveDate:int					= None;
		self.songIndex:int					= 1;
		self.isHard:int						= None;
		self.buttonNumber:int				= 4;
		self.sortNum:int					= None;
		self.missVibrate:bool				= None;
		self.soundHelper:int				= 3;
		self.displayAdjustment:int			= None;
		self.judgeCompensate:int			= None;
		self.advSceneSettringString:str		= None;
		self.metronomeSquipment:str			= None;
		self.playTimeUIA:int				= None;
		self.playTimeUIB:int				= None;
		self.playTimeUIC:int				= None;
		self.playTimeUID:int				= None;
		self.playTimeUIE:int				= None;
		self.playTimeUIF:int				= None;
		self.playTimeRankEX:int				= None;
		self.playTimeKnockEX:int			= None;
		self.playTimeKnockNote:int			= None;
		self.playVsync:bool					= True;
		self.buttonSetting4K:list[int]		= list();
		self.buttonSetting6K:list[int]		= list();
		self.hiddenUnlockSongs:bool			= None;
		self.hideLeaderboardMini:bool		= True;
		self.playingSceneName:str			= None;
		self.selectSongName:str				= "luobi";
		self.sceneName:str					= "SelectSongScene";
		self.busVolume:float				= None;
		self.advSceneSettingString:str		= "\n";
		self.dropSpeed:int					= 8;
		self.isUseUserMemoryDropSpeed:bool	= True;
		self.dropSpeedFloat:float			= None;
		self.isOpenVSync:bool				= True;
		self.hadSaveFpsAndVSync:bool		= None;
		self.fps:int						= 60;

	def __str__(self)->str:
		return f"SongSaveInfoPy(\n"\
			f"\tversion:{self.version}\n"\
			f"\tAppVersion:{self.AppVersion}\n"\
			f"\tsaveInfoList: List[SongSaveInfoPy]\n"\
			f"\tpurchaseIds:{self.purchaseIds}\n"\
			f"\tcrc:{self.crc}\n"\
			f"\tsaveDate:{self.saveDate}\n"\
			f"\tsongIndex:{self.songIndex}\n"\
			f"\tisHard:{self.isHard}\n"\
			f"\tbuttonNumber:{self.buttonNumber}\n"\
			f"\tsortNum:{self.sortNum}\n"\
			f"\tmissVibrate:{self.missVibrate}\n"\
			f"\tsoundHelper:{self.soundHelper}\n"\
			f"\tdisplayAdjustment:{self.displayAdjustment}\n"\
			f"\tjudgeCompensate:{self.judgeCompensate}\n"\
			f"\tadvSceneSettringString:\"{self.advSceneSettringString}\"\n"\
			f"\tmetronomeSquipment:\"{self.metronomeSquipment}\"\n"\
			f"\tplayTimeUIA:{self.playTimeUIA}\n"\
			f"\tplayTimeUIB:{self.playTimeUIB}\n"\
			f"\tplayTimeUIC:{self.playTimeUIC}\n"\
			f"\tplayTimeUID:{self.playTimeUID}\n"\
			f"\tplayTimeUIE:{self.playTimeUIE}\n"\
			f"\tplayTimeUIF:{self.playTimeUIF}\n"\
			f"\tplayTimeRankEX:{self.playTimeRankEX}\n"\
			f"\tplayTimeKnockEX:{self.playTimeKnockEX}\n"\
			f"\tplayTimeKnockNote:{self.playTimeKnockNote}\n"\
			f"\tplayVsync:{self.playVsync}\n"\
			f"\tbuttonSetting4K:{self.buttonSetting4K}\n"\
			f"\tbuttonSetting6K:{self.buttonSetting6K}\n"\
			f"\thiddenUnlockSongs:{self.hiddenUnlockSongs}\n"\
			f"\thideLeaderboardMini:{self.hideLeaderboardMini}\n"\
			f"\tplayingSceneName:\"{self.playingSceneName}\"\n"\
			f"\tselectSongName:\"{self.selectSongName}\"\n"\
			f"\tsceneName:\"{self.sceneName}\"\n"\
			f"\tbusVolume:{self.busVolume}\n"\
			f"\tadvSceneSettingString:\"{self.advSceneSettingString}\"\n"\
			f"\tdropSpeed:{self.dropSpeed}\n"\
			f"\tisUseUserMemoryDropSpeed:{self.isUseUserMemoryDropSpeed}\n"\
			f"\tdropSpeedFloat:{self.dropSpeedFloat}\n"\
			f"\tisOpenVSync:{self.isOpenVSync}\n"\
			f"\thadSaveFpsAndVSync:{self.hadSaveFpsAndVSync}\n"\
			f"\tfps:{self.fps})";

	def ToDict(self)->dict[str,any]:
		"格式化为dict类型";
		return dict(
			Version					 = self.version,
			AppVersion				 = self.AppVersion,
			SaveInfoList			 = [saveInfo.ToDict() for saveInfo in self.saveInfoList],
			PurchaseIds				 = self.purchaseIds,
			Crc						 = self.crc,
			SongIndex				 = self.songIndex,
			IsHard					 = self.isHard,
			ButtonNumber			 = self.buttonNumber,
			SortNum					 = self.sortNum,
			MissVibrate				 = self.missVibrate,
			SoundHelper				 = self.soundHelper,
			DisplayAdjustment		 = self.displayAdjustment,
			JudgeCompensate			 = self.judgeCompensate,
			AdvSceneSettringString	 = self.advSceneSettringString,
			MetronomeSquipment		 = self.metronomeSquipment,
			PlayTimeUIA				 = self.playTimeUIA,
			PlayTimeUIB				 = self.playTimeUIB,
			PlayTimeUIC				 = self.playTimeUIC,
			PlayTimeUID				 = self.playTimeUID,
			PlayTimeUIE				 = self.playTimeUIE,
			PlayTimeUIF				 = self.playTimeUIF,
			PlayTimeRankEX			 = self.playTimeRankEX,
			PlayTimeKnockEX			 = self.playTimeKnockEX,
			PlayTimeKnockNote		 = self.playTimeKnockNote,
			PlayVsync				 = self.playVsync,
			ButtonSetting4K			 = self.buttonSetting4K,
			ButtonSetting6K			 = self.buttonSetting6K,
			HiddenUnlockSongs		 = self.hiddenUnlockSongs,
			HideLeaderboardMini		 = self.hideLeaderboardMini,
			PlayingSceneName		 = self.playingSceneName,
			SelectSongName			 = self.selectSongName,
			SceneName				 = self.sceneName,
			BusVolume				 = self.busVolume,
			AdvSceneSettingString	 = self.advSceneSettingString,
			DropSpeed				 = self.dropSpeed,
			IsUseUserMemoryDropSpeed = self.isUseUserMemoryDropSpeed,
			DropSpeedFloat			 = self.dropSpeedFloat,
			IsOpenVSync				 = self.isOpenVSync,
			HadSaveFpsAndVSync		 = self.hadSaveFpsAndVSync,
			Fps = self.fps,
			);

	def DumpToJson(self)->None:
		"实例的数据保存为 JSON 文件";
		dataDict = self.ToDict();
		filePath:str = "./musync_data/SaveDataInfo.json";
		try:
			with open(filePath, "w", encoding="utf-8") as json_file:
				json.dump(dataDict, json_file, indent=4, ensure_ascii=False)
			self.__logger.info(f"Data successfully saved to {filePath}")
		except Exception:
			self.__logger.exception(f"Failed to save data to {filePath}")

class MapInfo(object):
	"存储谱面信息"
	def __init__(self, info:list = None, isBuiltin=False) -> None:
		if info is None:
			self.SongName:str			  = None;
			self.SongKeys:str			  = None;
			self.SongDifficulty:str		  = None;
			self.SongDifficultyNumber:str = None;
		else:
			self.SongName:str			  = str(info[0]);
			self.SongKeys:str			  = ("4Key" if info[1]==4 else "6Key");
			self.SongDifficulty:str		  = str(["Easy","Hard","Inferno"][info[2]]);
			self.SongDifficultyNumber:str = f"{info[3]:02d}";
		self.SongIsBuiltin:bool		  = isBuiltin;

	def ToDict(self)->dict[str,str]:
		"格式化为dict类型";
		return dict(
			Name			 = self.SongName,
			Keys			 = self.SongKeys,
			Difficulty		 = self.SongDifficulty,
			DifficultyNumber = self.SongDifficultyNumber,
			SongIsBuiltin	 = self.SongIsBuiltin
			);

class MapDataInfo(MapInfo):
	"存储谱面数据和信息";
	def __init__(self,SongId:int=0, SpeedStall:int=0, SyncNumber:int=0,
			UploadScore:float=0.0, PlayCount:int=0, Isfav:bool=False,
			CrcInt:int=0) -> None:
		self.SongId:int = SongId;
		# self.SongInfo:MapInfo = None;
		self.SpeedStall:int		= SpeedStall;
		self.SyncNumber:int		= SyncNumber;
		self.UploadScore:float	= UploadScore;
		self.PlayCount:int		= PlayCount;
		self.Isfav:bool			= Isfav;
		self.CrcInt:int			= CrcInt;
		self.State:str			= "    ";

	def __str__(self):
		return f"SongSaveInfoPy("\
			f"SongId:{self.SongId:08X}, "\
			f"Name:{self.SongName}, "\
			f"Keys:{self.SongKeys}, "\
			f"Difficulty:{self.SongDifficulty}, "\
			f"DifficultyNumber:{self.SongDifficultyNumber}, "\
			f"SpeedStall:{self.SpeedStall:08X}, "\
			f"SyncNumber:{self.SyncNumber}, "\
			f"UploadScore:{self.UploadScore}, "\
			f"PlayCount:{self.PlayCount}, "\
			f"Isfav:{self.Isfav}, "\
			f"CrcInt:{self.CrcInt}, "\
			f"State:{self.State})";

	def SetSongInfo(self, *args, **kwargs):
		"设置SongInfo字段";
		if len(args) == 1 and isinstance(args[0], list):
			info = args[0];
			self.SongName			  = str(info[0]);
			self.SongKeys			  = "4Key" if info[1] == 4 else "6Key";
			self.SongDifficulty		  = str(["Easy", "Hard", "Inferno"][info[2]]);
			self.SongDifficultyNumber = f"{info[3]:02d}";
		elif len(kwargs) == 4:
			self.SongName			  = kwargs.get("name");
			self.SongKeys			  = kwargs.get("keys");
			self.SongDifficulty		  = kwargs.get("difficulty");
			self.SongDifficultyNumber = kwargs.get("difficultyNumber");
		else:
			raise ValueError("Invalid arguments");

	def SetSongFrom(self,isBuiltin=False)->None:
		"设置曲目是否为内置曲目"
		self.SongIsBuiltin = isBuiltin;

	def ToDict(self)->dict[str,any]:
		"格式化为dict类型";
		return dict(
			SongId			 = f"{self.SongId:08X}",
			SongName		 = self.SongName,
			SongKeys		 = self.SongKeys,
			SongDifficulty	 = self.SongDifficulty,
			SongDifficultyNumber = self.SongDifficultyNumber,
			SongIsBuiltin	 = self.SongIsBuiltin,
			SpeedStall		 = f"{self.SpeedStall:08X}",
			SyncNumber		 = f"{self.SyncNumber / 100.0}%",
			UploadScore		 = f"{self.UploadScore * 100.0}%",
			CrcInt			 = self.CrcInt,
			State			 = self.State
			);

class Logger(object):
	"用于记录和生成logging.Logger"
	def __init__(self, logFilter:str = Config().LoggerFilter) -> None:
		self.loggerFilter = logging.INFO;
		match logFilter.lower():
			case "debug": self.loggerFilter		= logging.DEBUG;
			case "warning": self.loggerFilter	= logging.WARNING;
			case "error": self.loggerFilter		= logging.ERROR;
			case "fatal": self.loggerFilter		= logging.FATAL;
			case _: self.loggerFilter			= logging.INFO;

		self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s');
		self.file = logging.FileHandler("./log.txt");
		self.file.setLevel(self.loggerFilter);
		self.file.setFormatter(self.formatter);
		self.console = logging.StreamHandler();
		self.console.setLevel(self.loggerFilter);
		self.console.setFormatter(self.formatter);

	def GetLogger(self,name:str)->logging.Logger:
		"获取Logger"
		logger:logging.Logger = logging.getLogger(name);
		logger.setLevel(level = self.loggerFilter)
		logger.addHandler(self.file);
		logger.addHandler(self.console);
		return logger;
