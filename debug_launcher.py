# -*- coding: utf-8 -*-
import os
# === 启动时自动将工作目录切换到当前 main.py 所在的文件夹 ===
# 必须放在所有自定义模块（如 controller）导入之前！
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

import ctypes
import logging
import sys

from pathlib import Path
from tkinter import Tk, font

def auto_increment_prerelease() -> None:
    """检测到 debug_prerelease 文件时，自动递增 version.py 中的 pre 版本号"""
    trigger_file: Path = Path.cwd() / "debug_prerelease"
    version_file: Path = Path.cwd() / "musync_save" / "version.py"

    # 检查触发文件和目标源文件是否存在
    if not trigger_file.exists():
        return

    try:
        # 读取 debug_prerelease 的完整文本
        with trigger_file.open(encoding="utf-8") as tf:
            content: list[str] = tf.read().split("\n")
        # version
        version: str = content[0]
        # pre_version
        pre_version: str = content[1]
        # is_pre_release
        is_pre_release: bool = True if content[2] == "1" else False

        version_script: str = "# -*- coding: utf-8 -*-\n" \
            f"version:str = '{version}'						# Release版本号\n" \
            f"pre_version:str = '{version}pre{pre_version}'				# PreRelease版本号\n" \
            f"is_pre_release:bool = {is_pre_release}"

        # 将新的版本信息写回 version.py
        with version_file.open("w", encoding="utf-8") as vf:
            vf.write(version_script)

        # 自增 pre 版本号
        pre_version: int = int(pre_version) + 1
        # 更新 debug_prerelease 文件
        with trigger_file.open("w", encoding="utf-8") as tf:
            tf.write(
                f"{version}\n{pre_version}\n{'1' if is_pre_release else '0'}")

    except Exception as e:
        print(f"❌ [Auto-Build] 自动递增版本号失败: {e}")
auto_increment_prerelease();

from musync_save import config, Logger
from musync_save import Toolkit, MusyncMainWindow, HitDelay

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
        launcher()
        logger.info(" ====> Launcher() end <====")
    except Exception:
        logger.exception("Launcher Exception.")
        exitCode = 1
    logger.info("====> Software Exiting <====")
    # os.system("pause")
    sys.exit(exitCode)
