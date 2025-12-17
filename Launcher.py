from Resources import Config
Config()

import sys
import ctypes
import logging
from tkinter import Tk, font
# from tkinter import *

import Version
from MainWindow import MusyncSavDecodeGUI
#from .MainWindow_New import MusyncSavDecodeGUI
from Resources import Logger, SaveDataInfo, SongName
from Toolkit import Toolkit

logger:logging.Logger = Logger.GetLogger(name="Launcher")

def Launcher()->None:
	# Init
	SongName()
	SaveDataInfo()
	Config.Version = Version.preVersion.replace("pre",".") if (Version.isPreRelease) else Version.version.replace("rc",".")

	# Launcher
	root:Tk = Tk()
	ctypes.windll.shcore.SetProcessDpiAwareness(1)
	fontlist:list[str] = list(font.families())
	Toolkit.GetSaveFile()
	Toolkit.CheckResources(fontlist)
	# del fonts
	if Config.ChangeConsoleStyle:
		Toolkit.ChangeConsoleStyle()
	root.tk.call('tk', 'scaling', 1.25)
	root.resizable(False, True) #允许改变窗口高度，不允许改变窗口宽度
	# 仅旧版UI可用
	MusyncSavDecodeGUI(root=root)
	# if cfg['EnableFramelessWindow']:
	# 	root.overrideredirect(1)
	# 	window = NewStyle.MusyncSavDecodeGUI(root=root)
	# else:
	# 	window = OldStyle.MusyncSavDecodeGUI(root=root,version=version,preVersion=preVersion,isPreRelease=isPreRelease)
	root.update()
	root.mainloop()

if __name__ == '__main__':
	from datetime import datetime as dt
	try:
		logger.info(" ====> Launcher() start <====")
		Launcher()
		logger.info(" ====> Launcher() end <====")
	except Exception:
		logger.exception("Launcher Exception.")
	logger.info("====> Software Exiting <====")
	# os.system("pause")
	sys.exit(0)