# -*- coding: utf-8 -*-
"""
MUSYNXSave 工具包
提供同步音律喵赛克 Steam 本地存档分析、延迟分析等功能
"""

from .resources import Config
Config()

# 导出主要入口类和函数
# 1. 无依赖关系的核心功能模块
from .version import version, pre_version, is_pre_release
from .resources import Logger, SongName, SaveDataInfo, MapInfo, MapDataInfo

# 2. 依赖 1 的工具模块
from .acc_sync_diff_analyze import analyze_3d
from .all_hit_analyze import AllHitAnalyze
from .difficulty_score_analyze import diff_score_analyze
from .toolkit import Toolkit

# 3. 依赖 1 和 2 的主功能模块
from .hit_delay import HitDelay
from .musync_save_decode import MusyncSaveDecoder

# 4. 主窗口和程序入口
from .main_mindow import MusyncMainWindow

__version__ = pre_version.replace("pre",".") if (is_pre_release) else version

# 定义公开接口（建议使用）
__all__ = [
    "AllHitAnalyze",
    "analyze_3d",
    "Config",
    "diff_score_analyze",
    "HitDelay",
    "Logger",
    "MapDataInfo",
    "MapInfo",
    "MusyncMainWindow",
    "MusyncSaveDecoder",
    "SaveDataInfo",
    "SongName",
    "Toolkit",
]

# 初始化单例（可选，但 Launcher 中已做，此处不再重复）
# 如果希望导入包时自动初始化配置，可以取消下面注释
Config().Version = __version__
SongName()
SaveDataInfo()
Toolkit.init_resources()
