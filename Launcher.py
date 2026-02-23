# -*- coding: utf-8 -*-
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
    Toolkit.init_resources()

    if Version.isPreRelease:
        Config.Version = Version.preVersion.replace("pre", ".")
    else:
        Config.Version = Version.version.replace("rc", ".")

    # Launcher
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root:Tk = Tk()
    fontlist:list[str] = list(font.families())
    Toolkit.get_save_file()
    Toolkit.check_resources(fontlist)
    # del fonts
    if Config.ChangeConsoleStyle:
        Toolkit.change_console_style()
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
    # from datetime import datetime as dt
    exitCode:int = 0
    try:
        logger.info(" ====> Launcher() start <====")
        Launcher()
        logger.info(" ====> Launcher() end <====")
    except Exception:
        logger.exception("Launcher Exception.")
        exitCode = 1
    logger.info("====> Software Exiting <====")
    # os.system("pause")
    sys.exit(exitCode)
