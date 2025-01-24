import json
import logging
import os
from re import T

class SongName(object):
	def __init__(self) -> None:
		self.__data:dict[str,list] = None;
		self.__filePath:str = "./musync_data/SongName.json";
		self.logger:logging.Logger = logging.getLogger("Resources.SongName");
		self.logger.info("creating an instance in Resources.SongName");
		self.LoadFile();

	@property
	def SongNameData(self)->str: return self.__data

	@property
	def FilePath(self)->str: return self.__filePath
	# @FilePath.setter
	# def FilePath(self, value:str): self.__filePath = value; self.LoadFile();

	def LoadFile(self)->None:
		if os.path.isfile(self.__filePath):
			self.logger.error(f"file: \"{self.__filePath}\" not exists.");
			return;
		with open(self.__filePath,'r',encoding='utf8') as songNameFile:
			try:
				songNameJson:dict[str,list] = json.load(songNameFile);
			except Exception:
				self.logger.exception(f"file: \"{self.__filePath}\" load failure.");
			else:
				self.logger.info(f"file: \"{self.__filePath}\" loaded.");

class Config(object):
	def __init__(self) -> None:
		self.__filePath:str = "./musync_data/bootcfg.json";
		self.logger:logging.Logger = logging.getLogger("Resources.Config");
		self.logger.info("creating an instance in Resources.Config");
		self.LoadConfig();
		self.Version:str = None;
		self.Acc_Sync:bool = False;
		self.CheckUpdate:bool = True;
		self.AnalyzeWhenStarting:bool = False;
		self.DLLInjection:bool = False;
		self.SystemDPI:int = 100;
		self.DonutChartinHitDelay:bool = True;
		self.DonutChartinAllHitAnalyze:bool = True;
		self.NarrowDelayInterval:bool = True;
		self.ConsoleAlpha:int = 75;
		self.ConsoleFont:str = "霞鹜文楷等宽";
		self.ConsoleFontSize:int = 36;
		self.MainExecPath:str = None;
		self.ChangeConsoleStyle:bool = True;
		self.FramelessWindow:bool = False;
		self.TransparentColor:str = "#FFFFFF";
		self.Default4Keys:bool = False;
		self.DefaultDiffcute:int = 0;

	# def __repr__(self):
	# 	pass

	@property
	def FilePath(self)->str: return self.__filePath;
	# @FilePath.setter
	# def FilePath(self, value:str): self.__filePath = value; self.LoadFile();

	def LoadConfig(self)->None:
		if os.path.isfile(self.__filePath):
			self.logger.error(f"file: \"{self.__filePath}\" not exists.");
			return;
		with open(self.__filePath,'r',encoding='utf8') as configFile:
			try:
				config:dict[str,any] = json.load(configFile);
				# 动态将字典的键值对赋值给类的属性
				for key, value in config.items():
					setattr(self, key, value)
			except Exception:
				self.logger.exception(f"file: \"{self.__filePath}\" load failure.");
			else:
				self.logger.info(f"file: \"{self.__filePath}\" loaded.");

	def SaveConfig(self) -> None:
		# 获取所有需要保存的属性
		config_data = {
			"Version": self.Version,
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
			self.logger.info(f"Configuration saved to \"{self.__filePath}\" successfully.")
		except Exception as e:
			self.logger.exception(f"Failed to save configuration to \"{self.__filePath}\": {e}")

