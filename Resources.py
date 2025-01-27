import gzip
import json
import logging
import os
import shutil
import threading


class SongName(object):
	"存储SongName.json,单例";
	__instance = None;
	__lock:threading.Lock		= threading.Lock();
	__data:dict[str,list|int]	= None;
	__filePath:str				= os.getcwd()+"\\musync_data\\SongName.json";
	__logger:logging.Logger		= None;

	def __new__(cls):
		with cls.__lock:
			if not cls.__instance:
				cls.__instance = super(SongName, cls).__new__(cls);
				cls.__logger = Logger().GetLogger("Resources.SongName");
				cls.__logger.info("creating an instance in Resources.SongName");
				cls.LoadFile();
		return cls.__instance

	@classmethod
	def SongNameData(cls)->str: return cls.__data;

	@classmethod
	def Update(cls)->int|None: return None if (cls.__data is None) else cls.__data["update"];

	@classmethod
	def FilePath(cls)->str: return cls.__filePath;
	# @FilePath.setter
	# def FilePath(self, value:str): self.__filePath = value; self.LoadFile();

	@classmethod
	def LoadFile(cls)->None:
		"加载配置文件,自动执行";
		if not os.path.isfile(cls.__filePath):
			cls.__logger.error(f"file: \"{cls.__filePath}\" not exists.");
			cls.__data = None;
			return;
		with open(cls.__filePath,'r',encoding='utf8') as songNameFile:
			try:
				cls.__data:dict[str,list] = json.load(songNameFile);
			except Exception:
				cls.__logger.exception(f"file: \"{cls.__filePath}\" load failure.");
			else:
				cls.__logger.info(f"file: \"{cls.__filePath}\" loaded.");

class Config(object):
	"从bootcfg.json读取配置信息,单例";
	def CompressLogFile()->None:
		logsDir:str		= ".\\logs\\";
		logsName:str	= "log.gz";
		logName:str		= "log.txt";
		# 移动压缩文件到 logs 目录
		shutil.move(f".\\{logName}", logsDir+logName);
		# 获取已有的压缩文件数量
		nextIndex:int = len([f for f in os.listdir(logsDir)]);
		# 压缩 log.txt 文件
		with open(logsDir+logName, 'rb') as f_in:
			with gzip.open(f"{logsDir}{logsName}.{nextIndex}", 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out);
		# 清理 log.txt 文件
		os.remove(logsDir+logName);
	__instance						= None;
	__lock:threading.Lock			= threading.Lock();
	if (os.path.isfile(".\\log.txt")): CompressLogFile();
	__logger:logging.Logger			= logging.getLogger("Resources.Config");
	__filePath:str					= os.getcwd()+"\\musync_data\\bootcfg.json";
	Version:str						= None;
	LoggerFilter:str				= "Info";
	Acc_Sync:bool					= False;
	CheckUpdate:bool				= True;
	DLLInjection:bool				= False;
	SystemDPI:int					= 100;
	DonutChartinHitDelay:bool		= True;
	DonutChartinAllHitAnalyze:bool	= True;
	NarrowDelayInterval:bool		= True;
	ConsoleAlpha:int				= 75;
	ConsoleFont:str					= "霞鹜文楷等宽";
	ConsoleFontSize:int				= 36;
	MainExecPath:str				= None;
	ChangeConsoleStyle:bool			= True;
	FramelessWindow:bool			= False;
	TransparentColor:str			= "#FFFFFF";
	Default4Keys:bool				= False;
	DefaultDiffcute:int				= 0;

	def __new__(cls):
		with cls.__lock:
			if not cls.__instance:
				cls.__instance = super(Config, cls).__new__(cls)
				__file:logging.FileHandler = logging.FileHandler(".\\log.txt");
				__file.setLevel(logging.DEBUG);
				__file.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'));
				__console:logging.StreamHandler = logging.StreamHandler();
				__console.setLevel(logging.DEBUG);
				__console.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'));
				cls.__logger.addHandler(__file);
				cls.__logger.addHandler(__console);
				cls.__logger.info("creating an instance in Resources.Config");
				cls.LoadConfig();
		return cls.__instance

	# def __repr__(self):
	# 	pass

	@classmethod
	def FilePath(cls)->str: return cls.__filePath;
	# @FilePath.setter
	# def FilePath(self, value:str): self.__filePath = value; self.LoadFile();

	@classmethod
	def LoadConfig(cls)->None:
		"读取配置文件,自动执行";
		if not os.path.isfile(cls.__filePath):
			cls.__logger.error(f"file: \"{cls.__filePath}\" not exists.");
			return;
		with open(cls.__filePath,'r',encoding='utf8') as configFile:
			try:
				config:dict[str,any] = json.load(configFile);
				# 动态将字典的键值对赋值给类的属性
				for key, value in config.items():
					setattr(cls, key, value)
			except Exception:
				cls.__logger.exception(f"file: \"{cls.__filePath}\" load failure.");
			else:
				cls.__logger.info(f"file: \"{cls.__filePath}\" loaded.");

	@classmethod
	def SaveConfig(cls) -> None:
		"保存配置文件,手动执行";
		# 获取所有需要保存的属性
		config_data = {
			"Version": cls.Version,
			"LoggerFilter" : cls.LoggerFilter,
			"Acc_Sync": cls.Acc_Sync,
			"CheckUpdate": cls.CheckUpdate,
			"AnalyzeWhenStarting": cls.AnalyzeWhenStarting,
			"DLLInjection": cls.DLLInjection,
			"SystemDPI": cls.SystemDPI,
			"DonutChartinHitDelay": cls.DonutChartinHitDelay,
			"DonutChartinAllHitAnalyze": cls.DonutChartinAllHitAnalyze,
			"NarrowDelayInterval": cls.NarrowDelayInterval,
			"ConsoleAlpha": cls.ConsoleAlpha,
			"ConsoleFont": cls.ConsoleFont,
			"ConsoleFontSize": cls.ConsoleFontSize,
			"MainExecPath": cls.MainExecPath,
			"ChangeConsoleStyle": cls.ChangeConsoleStyle,
			"FramelessWindow": cls.FramelessWindow,
			"TransparentColor": cls.TransparentColor,
			"Default4Keys": cls.Default4Keys,
			"DefaultDiffcute": cls.DefaultDiffcute
		};
		# 确保文件夹存在
		os.makedirs(os.path.dirname(cls.__filePath), exist_ok=True);
		# 保存为 JSON 文件
		try:
			with open(cls.__filePath, 'w', encoding='utf8') as configFile:
				json.dump(config_data, configFile, ensure_ascii=False, indent=4);
			cls.__logger.info(f"Configuration saved to \"{cls.__filePath}\" successfully.");
		except Exception as e:
			cls.__logger.exception(f"Failed to save configuration to \"{cls.__filePath}\": {e}");

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
		super().__init__(); # 父类构造函数
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

class SaveDataInfo(object):
	"存储存档数据,单例"
	__instance						= None;
	__lock:threading.Lock			= threading.Lock();
	__logger:logging.Logger			= None;
	version:int						= None;
	AppVersion:int					= None;
	saveInfoList:list[MapDataInfo]	= list();
	purchaseIds:list[str]			= list();
	crc:int							= None;
	saveDate:int					= None;
	songIndex:int					= 1;
	isHard:int						= None;
	buttonNumber:int				= 4;
	sortNum:int						= None;
	missVibrate:bool				= None;
	soundHelper:int					= 3;
	displayAdjustment:int			= None;
	judgeCompensate:int				= None;
	advSceneSettringString:str		= None;
	metronomeSquipment:str			= None;
	playTimeUIA:int					= None;
	playTimeUIB:int					= None;
	playTimeUIC:int					= None;
	playTimeUID:int					= None;
	playTimeUIE:int					= None;
	playTimeUIF:int					= None;
	playTimeRankEX:int				= None;
	playTimeKnockEX:int				= None;
	playTimeKnockNote:int			= None;
	playVsync:bool					= True;
	buttonSetting4K:list[int]		= list();
	buttonSetting6K:list[int]		= list();
	hiddenUnlockSongs:bool			= None;
	hideLeaderboardMini:bool		= True;
	playingSceneName:str			= None;
	selectSongName:str				= "luobi";
	sceneName:str					= "SelectSongScene";
	busVolume:float					= None;
	advSceneSettingString:str		= "\n";
	dropSpeed:int					= 8;
	isUseUserMemoryDropSpeed:bool	= True;
	dropSpeedFloat:float			= None;
	isOpenVSync:bool				= True;
	hadSaveFpsAndVSync:bool			= None;
	fps:int							= 60;

	def __new__(cls):
		with cls.__lock:
			if not cls.__instance:
				cls.__instance = super(SaveDataInfo, cls).__new__(cls);
				cls.__logger = Logger().GetLogger(name="Resources.SaveDataInfo");
				cls.__logger.info("creating an instance in Resources.SaveDataInfo");
		return cls.__instance

	@classmethod
	def __str__(cls)->str:
		return f"SongSaveInfoPy(\n"\
			f"\tversion:{cls.version}\n"\
			f"\tAppVersion:{cls.AppVersion}\n"\
			f"\tsaveInfoList: List[SongSaveInfoPy]\n"\
			f"\tpurchaseIds:{cls.purchaseIds}\n"\
			f"\tcrc:{cls.crc}\n"\
			f"\tsaveDate:{cls.saveDate}\n"\
			f"\tsongIndex:{cls.songIndex}\n"\
			f"\tisHard:{cls.isHard}\n"\
			f"\tbuttonNumber:{cls.buttonNumber}\n"\
			f"\tsortNum:{cls.sortNum}\n"\
			f"\tmissVibrate:{cls.missVibrate}\n"\
			f"\tsoundHelper:{cls.soundHelper}\n"\
			f"\tdisplayAdjustment:{cls.displayAdjustment}\n"\
			f"\tjudgeCompensate:{cls.judgeCompensate}\n"\
			f"\tadvSceneSettringString:\"{cls.advSceneSettringString}\"\n"\
			f"\tmetronomeSquipment:\"{cls.metronomeSquipment}\"\n"\
			f"\tplayTimeUIA:{cls.playTimeUIA}\n"\
			f"\tplayTimeUIB:{cls.playTimeUIB}\n"\
			f"\tplayTimeUIC:{cls.playTimeUIC}\n"\
			f"\tplayTimeUID:{cls.playTimeUID}\n"\
			f"\tplayTimeUIE:{cls.playTimeUIE}\n"\
			f"\tplayTimeUIF:{cls.playTimeUIF}\n"\
			f"\tplayTimeRankEX:{cls.playTimeRankEX}\n"\
			f"\tplayTimeKnockEX:{cls.playTimeKnockEX}\n"\
			f"\tplayTimeKnockNote:{cls.playTimeKnockNote}\n"\
			f"\tplayVsync:{cls.playVsync}\n"\
			f"\tbuttonSetting4K:{cls.buttonSetting4K}\n"\
			f"\tbuttonSetting6K:{cls.buttonSetting6K}\n"\
			f"\thiddenUnlockSongs:{cls.hiddenUnlockSongs}\n"\
			f"\thideLeaderboardMini:{cls.hideLeaderboardMini}\n"\
			f"\tplayingSceneName:\"{cls.playingSceneName}\"\n"\
			f"\tselectSongName:\"{cls.selectSongName}\"\n"\
			f"\tsceneName:\"{cls.sceneName}\"\n"\
			f"\tbusVolume:{cls.busVolume}\n"\
			f"\tadvSceneSettingString:\"{cls.advSceneSettingString}\"\n"\
			f"\tdropSpeed:{cls.dropSpeed}\n"\
			f"\tisUseUserMemoryDropSpeed:{cls.isUseUserMemoryDropSpeed}\n"\
			f"\tdropSpeedFloat:{cls.dropSpeedFloat}\n"\
			f"\tisOpenVSync:{cls.isOpenVSync}\n"\
			f"\thadSaveFpsAndVSync:{cls.hadSaveFpsAndVSync}\n"\
			f"\tfps:{cls.fps})";

	@classmethod
	def ToDict(cls)->dict[str,any]:
		"格式化为dict类型";
		tempDict = dict(
			Version					 = cls.version,
			AppVersion				 = cls.AppVersion,
			PurchaseIds				 = cls.purchaseIds,
			Crc						 = cls.crc,
			SongIndex				 = cls.songIndex,
			IsHard					 = cls.isHard,
			ButtonNumber			 = cls.buttonNumber,
			SortNum					 = cls.sortNum,
			MissVibrate				 = cls.missVibrate,
			SoundHelper				 = cls.soundHelper,
			DisplayAdjustment		 = cls.displayAdjustment,
			JudgeCompensate			 = cls.judgeCompensate,
			AdvSceneSettringString	 = cls.advSceneSettringString,
			MetronomeSquipment		 = cls.metronomeSquipment,
			PlayTimeUIA				 = cls.playTimeUIA,
			PlayTimeUIB				 = cls.playTimeUIB,
			PlayTimeUIC				 = cls.playTimeUIC,
			PlayTimeUID				 = cls.playTimeUID,
			PlayTimeUIE				 = cls.playTimeUIE,
			PlayTimeUIF				 = cls.playTimeUIF,
			PlayTimeRankEX			 = cls.playTimeRankEX,
			PlayTimeKnockEX			 = cls.playTimeKnockEX,
			PlayTimeKnockNote		 = cls.playTimeKnockNote,
			PlayVsync				 = cls.playVsync,
			ButtonSetting4K			 = cls.buttonSetting4K,
			ButtonSetting6K			 = cls.buttonSetting6K,
			HiddenUnlockSongs		 = cls.hiddenUnlockSongs,
			HideLeaderboardMini		 = cls.hideLeaderboardMini,
			PlayingSceneName		 = cls.playingSceneName,
			SelectSongName			 = cls.selectSongName,
			SceneName				 = cls.sceneName,
			BusVolume				 = cls.busVolume,
			AdvSceneSettingString	 = cls.advSceneSettingString,
			DropSpeed				 = cls.dropSpeed,
			IsUseUserMemoryDropSpeed = cls.isUseUserMemoryDropSpeed,
			DropSpeedFloat			 = cls.dropSpeedFloat,
			IsOpenVSync				 = cls.isOpenVSync,
			HadSaveFpsAndVSync		 = cls.hadSaveFpsAndVSync,
			Fps = cls.fps,
			);
		tempDict["SaveInfoList"] = list();
		for saveInfo in cls.saveInfoList:
			tempDict["SaveInfoList"].append(saveInfo.ToDict());
		return tempDict;

	@classmethod
	def DumpToJson(cls)->None:
		"实例的数据保存为 JSON 文件";
		dataDict = cls.ToDict();
		filePath:str = ".\\musync_data\\SaveDataInfo.json";
		try:
			with open(filePath, "w", encoding="utf-8") as json_file:
				json.dump(dataDict, json_file, indent=4, ensure_ascii=False)
			cls.__logger.info(f"Data successfully saved to {filePath}")
		except Exception:
			cls.__logger.exception(f"Failed to save data to {filePath}")

class Logger(object):
	"用于记录和生成logging.Logger"
	__formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s');
	__file = logging.FileHandler(".\\log.txt");
	__console = logging.StreamHandler();
	__loggerFilter = logging.INFO;

	@classmethod
	def GetLogger(cls, name:str, logFilter:str = Config().LoggerFilter)->logging.Logger:
		"获取Logger"
		match logFilter.lower():
			case "debug": cls.loggerFilter		= logging.DEBUG;
			case "warning": cls.loggerFilter	= logging.WARNING;
			case "error": cls.loggerFilter		= logging.ERROR;
			case "fatal": cls.loggerFilter		= logging.FATAL;
			case _: cls.loggerFilter			= logging.INFO;
		cls.__file.setLevel(cls.__loggerFilter);
		cls.__file.setFormatter(cls.__formatter);
		cls.__console.setLevel(cls.__loggerFilter);
		cls.__console.setFormatter(cls.__formatter);

		logger:logging.Logger = logging.getLogger(name);
		logger.setLevel(level = cls.loggerFilter)
		if not logger.hasHandlers():
			logger.addHandler(cls.__file);
			logger.addHandler(cls.__console);
		return logger;
