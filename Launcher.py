# -*- coding: utf-8 -*-
import os
# === 启动时自动将工作目录切换到当前 main.py 所在的文件夹 ===
# 必须放在所有自定义模块（如 controller）导入之前！
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

import ctypes
import logging
import sys

from tkinter import Tk, font

from musync_save import config, Logger
from musync_save import Toolkit, MusyncMainWindow

logger:logging.Logger = Logger.get_logger(name="Launcher")

def launcher()->None:
    """程序入口，负责环境检查、资源准备和主窗口启动"""
    # Launcher
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root:Tk = Tk()
    fontlist:list[str] = list(font.families())
    Toolkit.get_save_file()
    Toolkit.check_resources(fontlist)
    # del fonts
    if config.ChangeConsoleStyle:
        Toolkit.change_console_style()
    root.tk.call('tk', 'scaling', 1.25)
    root.resizable(False, True) #允许改变窗口高度，不允许改变窗口宽度
    MusyncMainWindow(root=root)
    root.update()
    root.mainloop()

if __name__ == '__main__':
    exitCode:int = 0
    try:
        logger.info(" ====> Launcher() start <====")
        launcher()
        logger.info(" ====> Launcher() end <====")
    except Exception:
        logger.exception("Launcher Exception.")
        exitCode = 1
    logger.info("====> Software Exiting <====")
    # os.system("pause")
    sys.exit(exitCode)
