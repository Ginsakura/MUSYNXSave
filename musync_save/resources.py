# -*- coding: utf-8 -*-
import gzip
import json
import logging
import os
import shutil
import threading
from typing import Any, ClassVar

class Config(object):
    """从bootcfg.json读取配置信息,单例"""
    @staticmethod
    def CompressLogFile()->None:
        logsDir:str		= ".\\logs\\"
        # Ensure logs directory exists
        os.makedirs(logsDir, exist_ok=True)
        logName:str		= "log.txt"
        # Check if log file exists
        if not os.path.isfile(f".\\{logName}"):
            return
        # 获取已有的压缩文件数量
        nextIndex:int = len(os.listdir(logsDir))
        logsName:str	= f"log.{nextIndex}.gz"
        # 移动压缩文件到 logs 目录
        shutil.move(f".\\{logName}", logsDir+logName)
        # 压缩 log.txt 文件
        with open(logsDir+logName, 'rb') as f_in:
            with open(logsDir+logsName, 'wb') as f_out_raw:
                with gzip.GzipFile(filename='log.txt', mode='wb', fileobj=f_out_raw) as f_out:
                    shutil.copyfileobj(f_in, f_out)
        # 清理 log.txt 文件
        os.remove(logsDir+logName)

    _logLevelMapping:ClassVar[dict[str,int]]={
        "NOTSET": logging.NOTSET,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "FATAL": logging.CRITICAL,
        "CRITICAL": logging.CRITICAL,
        }
    _instance						= None
    _lock:threading.Lock			= threading.Lock()
    _logger:logging.Logger			= None
    _filePath:str					= os.getcwd()+"\\musync_data\\bootcfg.json"
    _config:ClassVar[dict[str,Any]]	= dict()

    Version:str						= _config.get("Version"					, "3.0.0")
    UpdateChannel:str				= _config.get("UpdateChannel"				, "Release")
    LoggerFilterString:str			= _config.get("LoggerFilterString"			, "DEBUG")
    LoggerFilter:int				= _logLevelMapping.get(LoggerFilterString	, logging.INFO)
    CheckUpdate:bool				= _config.get("CheckUpdate"				, True)
    DLLInjection:bool				= _config.get("DLLInjection"				, False)
    SystemDPI:int					= _config.get("SystemDPI"					, 100)
    DonutChartinHitDelay:bool		= _config.get("DonutChartinHitDelay"		, True)
    DonutChartinAllHitAnalyze:bool	= _config.get("DonutChartinAllHitAnalyze"	, True)
    NarrowDelayInterval:bool		= _config.get("NarrowDelayInterval"		, True)
    ConsoleAlpha:int				= _config.get("ConsoleAlpha"				, 75)
    ConsoleFont:str					= _config.get("ConsoleFont"				, "霞鹜文楷等宽")
    ConsoleFontSize:int				= _config.get("ConsoleFontSize"			, 36)
    MainExecPath:str				= _config.get("MainExecPath"				, "")
    ChangeConsoleStyle:bool			= _config.get("ChangeConsoleStyle"			, True)
    FramelessWindow:bool			= _config.get("FramelessWindow"			, False)
    TransparentColor:str			= _config.get("TransparentColor"			, "#FFFFFF")

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                if os.path.isfile(".\\log.txt"):
                    cls.CompressLogFile()
                cls._logger_init()
                cls._instance = super(Config, cls).__new__(cls)
                _file:logging.FileHandler = logging.FileHandler(".\\log.txt")
                _file.setLevel(logging.DEBUG)
                _file.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                _console:logging.StreamHandler = logging.StreamHandler()
                _console.setLevel(logging.DEBUG)
                _console.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                cls._logger.addHandler(_file)
                cls._logger.addHandler(_console)
                cls._logger.info("creating an instance in Resources.Config")
                cls.LoadConfig()
        return cls._instance

    @classmethod
    def _logger_init(cls)->None:
        cls._logger = logging.getLogger("Resources.Config")

        if not os.path.isfile(cls._filePath):
            cls._logger.error(f"file: \"{cls._filePath}\" not exists.")
        else:
            with open(cls._filePath,'r',encoding='utf8') as configFile:
                try:
                    cls._config = json.load(configFile)
                except Exception:
                    cls._logger.exception(f"file: \"{cls._filePath}\" load failure.")
                else:
                    cls._logger.info(f"file: \"{cls._filePath}\" loaded.")

    @classmethod
    def FilePath(cls)->str: return cls._filePath
    # @FilePath.setter
    # def FilePath(self, value:str): self._filePath = value; self.LoadFile()

    @classmethod
    def LoadConfig(cls)->None:
        "读取配置文件,自动执行"
        if not os.path.isfile(cls._filePath):
            cls._logger.error(f"file: \"{cls._filePath}\" not exists.")
            return
        with open(cls._filePath,'r',encoding='utf8') as configFile:
            try:
                config:dict[str,Any] = json.load(configFile)
                # 动态将字典的键值对赋值给类的属性
                for key, value in config.items():
                    setattr(cls, key, value)
                # Update LoggerFilter after all keys are loaded
                cls.LoggerFilter = cls._logLevelMapping.get(cls.LoggerFilterString, logging.INFO)
            except Exception:
                cls._logger.exception(f"file: \"{cls._filePath}\" load failure.")
            else:
                cls._logger.info(f"file: \"{cls._filePath}\" loaded.")

    @classmethod
    def SaveConfig(cls) -> None:
        "保存配置文件,手动执行"
        # Fix Filter
        logLevelMapping:dict[int,str] = {
            0: "NOTSET",
            10: "DEBUG",
            20: "INFO",
            30: "WARNING",
            40: "ERROR",
            50: "FATAL",
            }
        loggerFilterStr:str = logLevelMapping[cls.LoggerFilter]
        # 获取所有需要保存的属性
        config_data = {
            "Version": cls.Version,
            "UpdateChannel": cls.UpdateChannel,
            "LoggerFilterString": loggerFilterStr,
            "CheckUpdate": cls.CheckUpdate,
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
        }
        # 确保文件夹存在
        os.makedirs(os.path.dirname(cls._filePath), exist_ok=True)
        # 保存为 JSON 文件
        try:
            with open(cls._filePath, 'w', encoding='utf8') as configFile:
                json.dump(config_data, configFile, ensure_ascii=False, indent=2)
            cls._logger.info(f"Configuration saved to \"{cls._filePath}\" successfully.")
        except Exception:
            cls._logger.exception(f"Failed to save configuration to \"{cls._filePath}\"")

class Logger(object):
    """用于记录和生成日志"""
    _formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    @classmethod
    def GetLogger(cls, name:str)->logging.Logger:
        """获取Logger"""
        loggerFilter:int = Config.LoggerFilter
        logger:logging.Logger = logging.getLogger(name)
        logger.setLevel(level = loggerFilter)
        if not logger.hasHandlers():
            file_handler = logging.FileHandler(".\\log.txt")
            file_handler.setLevel(loggerFilter)
            file_handler.setFormatter(cls._formatter)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(loggerFilter)
            console_handler.setFormatter(cls._formatter)
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        return logger

class SongName(object):
    "存储SongName.json,单例"
    _instance = None
    _lock: threading.Lock		= threading.Lock()
    _data: dict[str, list[Any]]	= {}
    _filePath: str				= os.getcwd()+"\\musync_data\\SongName.json"
    _logger: logging.Logger		= None

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(SongName, cls).__new__(cls)
                cls._logger = Logger.GetLogger("Resources.SongName")
                cls._logger.info("creating an instance in Resources.SongName")
                cls.LoadFile()
        return cls._instance

    @classmethod
    def SongNameData(cls) -> dict[str,list[str|int|bool]]:
        return cls._data

    @classmethod
    def Version(cls)->int:
        return 0 if (cls._data is None) else cls._data["version"]

    @classmethod
    def FilePath(cls)->str:
        return cls._filePath
    # @FilePath.setter
    # def FilePath(self, value:str): self._filePath = value; self.LoadFile()

    @classmethod
    def LoadFile(cls)->None:
        "加载配置文件,自动执行"
        if not os.path.isfile(cls._filePath):
            cls._logger.error(f"file: \"{cls._filePath}\" not exists.")
            cls._data = {}
            return
        with open(cls._filePath,'r',encoding='utf8') as songNameFile:
            try:
                cls._data = json.load(songNameFile)
            except Exception:
                cls._logger.exception(f"file: \"{cls._filePath}\" load failure.")
            else:
                cls._logger.info(f"file: \"{cls._filePath}\" loaded.")

class MapInfo(object):
    "存储谱面信息"
    def __init__(self, info:list|None = None, isBuiltin:bool=False) -> None:
        if info is None:
            self.SongName:str				= ""
            self.SongKeys:str				= ""
            self.SongDifficulty:str		    = ""
            self.SongDifficultyNumber:str	= ""
        else:
            self.SongName:str				= str(info[0])
            self.SongKeys:str				= ("4Key" if info[1]==4 else "6Key")
            difficulties:list[str]			= ["Easy", "Hard", "Inferno"]
            self.SongDifficulty:str = difficulties[info[2]] if 0 <= info[2] < len(difficulties) else "Unknown"
            self.SongDifficultyNumber:str	= f"{info[3]:02d}"
        self.SongIsBuiltin:bool				= isBuiltin

    def ToDict(self)->dict[str, str|bool]:
        "格式化为dict类型"
        return dict(
            Name			 = self.SongName,
            Keys			 = self.SongKeys,
            Difficulty		 = self.SongDifficulty,
            DifficultyNumber = self.SongDifficultyNumber,
            SongIsBuiltin	 = self.SongIsBuiltin
            )

class MapDataInfo(MapInfo):
    "存储谱面数据和信息"
    def __init__(self,SongId:int=0, SpeedStall:int=0, SyncNumber:int=0,
            UploadScore:float=0.0, PlayCount:int=0, Isfav:bool=False,
            CrcInt:int=0) -> None:
        self.SongId:int = SongId
        super().__init__() # 父类构造函数
        # self.SongInfo:MapInfo = None
        self.SpeedStall:int		= SpeedStall
        self.SyncNumber:int		= SyncNumber
        self.UploadScore:float	= UploadScore
        self.PlayCount:int		= PlayCount
        self.Isfav:bool			= Isfav
        self.CrcInt:int			= CrcInt
        self.State:str			= "    "

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
            f"State:{self.State})"

    def SetSongInfo(self, *args, **kwargs) -> None:
        if len(args) == 1 and isinstance(args[0], list):
            # 通过 List 设置 SongInfo 字段
            info = args[0]
            if (info is None):
                return
            self.SongName:str				= str(info[0])
            self.SongKeys:str				= "4Key" if info[1] == 4 else "6Key"
            difficulties:list[str]			= ["Easy", "Hard", "Inferno"]
            self.SongDifficulty:str			= difficulties[info[2]] if 0 <= info[2] < len(difficulties) else "Unknown"
            self.SongDifficultyNumber:str	= f"{info[3]:02d}"
            self.SongIsBuiltin:bool			= kwargs.get('isBuiltin', False)
        elif len(args) == 1 and isinstance(args[0], MapInfo):
            # 通过 MapInfo 设置 SongInfo 字段
            mapInfo = args[0]
            if (mapInfo is None):
                return
            self.SongName:str				= mapInfo.SongName
            self.SongKeys:str				= mapInfo.SongKeys
            self.SongDifficulty:str			= mapInfo.SongDifficulty
            self.SongDifficultyNumber:str	= mapInfo.SongDifficultyNumber
            self.SongIsBuiltin:bool			= mapInfo.SongIsBuiltin
        elif len(args) == 1 and args[0] is None:
            # 如果传入的 MapInfo 为 None，处理这种情况
            # Config._logger.warning("MapInfo is None.")
            return
        elif len(args) == 4 and all(isinstance(arg, str) for arg in args):
            # 通过逐个条目设置 SongInfo 字段
            self.SongName, self.SongKeys, self.SongDifficulty, self.SongDifficultyNumber = args
            self.SongIsBuiltin = kwargs.get('isBuiltin', False)
        else:
            raise TypeError("Invalid arguments for SetSongInfo")

    def SetSongFrom(self,isBuiltin=False)->None:
        "设置曲目是否为内置曲目"
        self.SongIsBuiltin = isBuiltin

    def ToDict(self)->dict[str,Any]:
        "格式化为dict类型"
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
            )

class SaveDataInfo(object):
    "存储存档数据,单例"
    _instance									= None
    _lock:threading.Lock						= threading.Lock()
    _logger:logging.Logger						= None
    version:int									= None
    AppVersion:int								= None
    saveInfoList:ClassVar[list[MapDataInfo]]	= []
    purchaseIds:ClassVar[list[str]]				= []
    crc:int										= None
    saveDate:int								= None
    songIndex:int								= 1
    isHard:int									= None
    buttonNumber:int							= 4
    sortNum:int									= None
    missVibrate:bool							= None
    soundHelper:int								= 3
    displayAdjustment:int						= None
    judgeCompensate:int							= None
    advSceneSettringString:str					= None
    metronomeSquipment:str						= None
    playTimeUIA:int								= None
    playTimeUIB:int								= None
    playTimeUIC:int								= None
    playTimeUID:int								= None
    playTimeUIE:int								= None
    playTimeUIF:int								= None
    playTimeRankEX:int							= None
    playTimeKnockEX:int							= None
    playTimeKnockNote:int						= None
    playVsync:bool								= True
    buttonSetting4K:ClassVar[list[int]]			= list()
    buttonSetting6K:ClassVar[list[int]]			= list()
    hiddenUnlockSongs:bool						= None
    hideLeaderboardMini:bool					= True
    playingSceneName:str						= None
    selectSongName:str							= "luobi"
    sceneName:str								= "SelectSongScene"
    busVolume:float								= None
    advSceneSettingString:str					= "\n"
    dropSpeed:int								= 8
    isUseUserMemoryDropSpeed:bool				= True
    dropSpeedFloat:float						= None
    isOpenVSync:bool							= True
    hadSaveFpsAndVSync:bool						= None
    fps:int										= 60

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(SaveDataInfo, cls).__new__(cls)
                cls._logger = Logger.GetLogger(name="Resources.SaveDataInfo")
                cls._logger.info("creating an instance in Resources.SaveDataInfo")
        return cls._instance

    @classmethod
    def ToString(cls)->str:
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
            f"\tfps:{cls.fps})"

    @classmethod
    def ToDict(cls,debug=False)->dict[str,Any]:
        "格式化为dict类型"
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
            )
        tempDict["SaveInfoList"] = list()
        if (debug):
            tempDict["SaveInfoList"].append("DEBUG")
        else:
            for saveInfo in cls.saveInfoList:
                tempDict["SaveInfoList"].append(saveInfo.ToDict())
        return tempDict

    @classmethod
    def DumpToJson(cls)->None:
        "实例的数据保存为 JSON 文件"
        dataDict = cls.ToDict()
        filePath:str = ".\\musync_data\\SaveDataInfo.json"
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        try:
            with open(filePath, "w", encoding="utf-8") as json_file:
                json.dump(dataDict, json_file, ensure_ascii=False, indent=2)
            cls._logger.info(f"Data successfully saved to {filePath}")
        except Exception:
            cls._logger.exception(f"Failed to save data to {filePath}")
