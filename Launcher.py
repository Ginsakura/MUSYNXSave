import sys
import ctypes
import logging
import os
from tkinter import Tk, font
from Resources import Logger
from Version import *
logger:logging.Logger = Logger.GetLogger(name="Launcher");
try:
	# from tkinter import *
	from MainWindow import MusyncSavDecodeGUI
	#from .MainWindow_New import MusyncSavDecodeGUI
	from Resources import Config, SaveDataInfo, SongName
	from Toolkit import Toolkit
except:
	logger.exception("Import Error.");
	sys.exit(101)

def Launcher()->None:
	# Init
	Config();
	SongName();
	SaveDataInfo();
	Config.Version = preVersion.replace("pre",".") if (isPreRelease) else version.replace("rc",".");

	# Launcher
	root:Tk = Tk();
	ctypes.windll.shcore.SetProcessDpiAwareness(1);
	fontlist:list[str] = list(font.families());
	Toolkit.CheckResources(fontlist);
	# del fonts
	if Config.ChangeConsoleStyle:
		Toolkit.ChangeConsoleStyle();
	root.tk.call('tk', 'scaling', 1.25);
	root.resizable(False, True); #允许改变窗口高度，不允许改变窗口宽度
	# 强制仅旧版UI
	MusyncSavDecodeGUI(root=root);
	# if cfg['EnableFramelessWindow']:
	# 	root.overrideredirect(1)
	# 	window = NewStyle.MusyncSavDecodeGUI(root=root)
	# else:
	# 	window = OldStyle.MusyncSavDecodeGUI(root=root,version=version,preVersion=preVersion,isPreRelease=isPreRelease)
	root.update();
	root.mainloop();

if __name__ == '__main__':
	try:
		Launcher();
	except Exception:
		logger.exception("Launcher Exception.");
	os.system("pause");
