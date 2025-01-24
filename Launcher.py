import ctypes
import json
import logging
import os
import sys
# import traceback
# import requests

# from tkinter import *
from tkinter import Tk,font

import Functions
import MainWindowOldStyle as OldStyle
# import MusyncSavDecodeGUI as NewStyle

from Resources import Config

version = '1.3.0rc1'
isPreRelease = True
preVersion = "1.3.0pre1"
isPreRelease = False

logger = logging.getLogger("Launcher")
logger.setLevel(level = logging.INFO)
file = logging.FileHandler("./log.txt")
file.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)


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
