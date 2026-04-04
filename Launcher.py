# -*- coding: utf-8 -*-
import ctypes
import logging
import re
import sys

from pathlib import Path
from tkinter import Tk, font

from musync_save import config, Logger
from musync_save import Toolkit, MusyncMainWindow, HitDelay

logger:logging.Logger = Logger.get_logger(name="Launcher")

def Launcher()->None:
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
    # if cfg['EnableFramelessWindow']:
    # 	root.overrideredirect(1)
    # 	window = NewStyle.MusyncSavDecodeGUI(root=root)
    # else:
    # 	window = OldStyle.MusyncSavDecodeGUI(root=root,version=version,preVersion=preVersion,isPreRelease=isPreRelease)
    root.update()
    root.mainloop()


# def auto_increment_prerelease() -> None:
#     """检测到 debug_prerelease 文件时，自动递增 version.py 中的 pre 版本号"""
#     trigger_file: Path = Path.cwd() / "debug_prerelease"
#     version_file: Path = Path.cwd() / "version.py"

#     # 1. 检查触发文件和目标源文件是否存在
#     if not trigger_file.exists() or not version_file.exists():
#         return

#     try:
#         # 2. 读取 version.py 的完整文本
#         content = version_file.read_text(encoding="utf-8")

#         # 3. 核心正则表达式：精准捕获 pre 后的数字
#         # 匹配模式解析:
#         # Group 1: 匹配 `pre_version:str = '3.0.0pre` 或 `"3.0.0pre`
#         # Group 2: 匹配数字部分，例如 `15`
#         # Group 3: 匹配结尾的引号 `'` 或 `"`
#         pattern = r'(pre_version\s*:\s*str\s*=\s*["\'].*?pre)(\d+)(["\'])'

#         def increment_logic(match) -> str:
#             prefix = match.group(1)           # 前缀部分
#             current_num = int(match.group(2)) # 将提取到的字符串数字转为整数
#             suffix = match.group(3)           # 后缀引号

#             new_num = current_num + 1
#             print(f"[Auto-Build] 版本号已递增: pre{current_num} -> pre{new_num}")

#             return f"{prefix}{new_num}{suffix}"

#         # 4. 执行正则替换
#         new_content, sub_count = re.subn(pattern, increment_logic, content)

#         # 5. 如果成功匹配并替换，写回文件
#         if sub_count > 0:
#             version_file.write_text(new_content, encoding="utf-8")

#             # 删除触发文件
#             # trigger_file.unlink()
#             # print("🗑️ [Auto-Build] 触发文件 'debug_prerelease' 已被消费并删除。")

#     except Exception as e:
#         print(f"❌ [Auto-Build] 自动递增版本号失败: {e}")

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
    # auto_increment_prerelease();
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
