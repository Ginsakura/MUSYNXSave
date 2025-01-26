import ctypes
import logging
import os
# from tkinter import *
from tkinter import Tk,font
from MainWindow import MusyncSavDecodeGUI
#from .MainWindow_New import MusyncSavDecodeGUI
from Resources import Config, Logger
from Toolkit import Toolkit

version = '1.3.0rc1'
isPreRelease = True
preVersion = "1.3.0pre1"
isPreRelease = False

logger:logging.Logger = Logger().GetLogger(name="Launcher");

def Launcher():
	root:Tk = Tk();
	ctypes.windll.shcore.SetProcessDpiAwareness(1);
	fonts:list[str] = list(font.families());
	Toolkit.CheckResources(fonts);
	# del fonts
	if Config().ChangeConsoleStyle:
		Toolkit.ChangeConsoleStyle();
	root.tk.call('tk', 'scaling', 1.25);
	root.resizable(False, True); #允许改变窗口高度，不允许改变窗口宽度
	# 强制仅旧版UI
	window = MusyncSavDecodeGUI(root=root,version=version,preVersion=preVersion,isPreRelease=isPreRelease);
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
	# os.system("pause");
