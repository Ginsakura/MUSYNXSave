import ctypes
import json
import os
import sys
# import traceback
# import requests

# from tkinter import *
from tkinter import Tk,font

import Functions
import MainWindowOldStyle as OldStyle
# import MusyncSavDecodeGUI as NewStyle

version = '1.2.8rc1'
isPreRelease = True
preVersion = "1.2.8pre3"
isPreRelease = False

def launcher():
	root = Tk()
	ctypes.windll.shcore.SetProcessDpiAwareness(1)
	fonts = list(font.families())
	Functions.CheckFileBeforeStarting(fonts)
	# del fonts
	Functions.CheckConfig()
	with open('./musync_data/ExtraFunction.cfg','r',encoding='utf8') as cfg:
		cfg = json.load(cfg)
	if cfg['ChangeConsoleStyle']:
		Functions.ChangeConsoleStyle()
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
