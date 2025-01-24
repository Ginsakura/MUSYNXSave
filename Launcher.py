import ctypes
import json
import logging
import os
import sys
# from tkinter import *
from tkinter import Tk,font
from . import Toolkit
from . import MainWindowOldStyle as OldStyle
#from . import MusyncSavDecodeGUI as NewStyle
from .Resources import Config

version = '1.3.0rc1'
isPreRelease = True
preVersion = "1.3.0pre1"
isPreRelease = False

config:Config = Config();
loggerFilter = logging.INFO;
match config.LoggerFilter.lower():
	case "debug": loggerFilter = logging.DEBUG;
	case "warning": loggerFilter = logging.WARNING;
	case "error": loggerFilter = logging.ERROR;
	case "fatal": loggerFilter = logging.FATAL;
	case _: loggerFilter = logging.INFO;

logger = logging.getLogger("Launcher")
logger.setLevel(level = loggerFilter)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file = logging.FileHandler("./log.txt")
file.setLevel(loggerFilter)
file.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(loggerFilter)
console.setFormatter(formatter)

logger.addHandler(file)
logger.addHandler(console)


def launcher():
	root:Tk = Tk()
	ctypes.windll.shcore.SetProcessDpiAwareness(1)
	fonts:list[str] = list(font.families())
	Toolkit.CheckFileBeforeStarting(fonts)
	# del fonts
	if config.ChangeConsoleStyle:
		Toolkit.ChangeConsoleStyle()
	root.tk.call('tk', 'scaling', 1.25)
	root.resizable(False, True) #允许改变窗口高度，不允许改变窗口宽度
	# 强制仅旧版UI
	window = OldStyle.MusyncSavDecodeGUI(root=root,version=version,preVersion=preVersion,isPreRelease=isPreRelease)
	# if cfg['EnableFramelessWindow']:
	# 	root.overrideredirect(1)
	# 	window = NewStyle.MusyncSavDecodeGUI(root=root)
	# else:
	# 	window = OldStyle.MusyncSavDecodeGUI(root=root,version=version,preVersion=preVersion,isPreRelease=isPreRelease)
	root.update()
	root.mainloop()


if __name__ == '__main__':
	if sys.argv[-1] == "debug":
		launcher()
	else:
		try:
			launcher()
		except Exception as e:
			print(repr(e))
	os.system("pause")
