# -*- coding: utf-8 -*-
import sys
import ctypes
import logging
from tkinter import Tk, font

from musync_save import __version__
from musync_save import MusyncMainWindow, HitDelay
from musync_save import Toolkit, Config, Logger

logger:logging.Logger = Logger.GetLogger(name="Launcher")

def Launcher()->None:
    """程序入口，负责环境检查、资源准备和主窗口启动"""
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
    MusyncMainWindow(root=root)
    # if cfg['EnableFramelessWindow']:
    # 	root.overrideredirect(1)
    # 	window = NewStyle.MusyncSavDecodeGUI(root=root)
    # else:
    # 	window = OldStyle.MusyncSavDecodeGUI(root=root,version=version,preVersion=preVersion,isPreRelease=isPreRelease)
    root.update()
    root.mainloop()

def DEBUG() -> None:
    """调试入口，负责测试和调试"""
    logger.info(" ====> DEBUG() start <====")
    root:Tk = Tk()
    fontlist:list[str] = list(font.families())
    Toolkit.get_save_file()
    Toolkit.check_resources(fontlist)
    root.tk.call('tk', 'scaling', 1.25)

    # Debug Target
    HitDelay(root)

    root.update()
    root.mainloop()

    logger.info(" ====> DEBUG() end <====")

if __name__ == '__main__':
    exitCode:int = 0
    # DEBUG(); sys.exit(exitCode)
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
