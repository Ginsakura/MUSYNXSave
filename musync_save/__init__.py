# -*- coding: utf-8 -*-
"""
MUSYNXSave 工具包
提供同步音律喵赛克 Steam 本地存档分析、延迟分析等功能
"""


# 导出主要入口类和函数
# 无依赖关系的核心功能模块
from .version import version, pre_version, is_pre_release
from .config_manager import config, Logger
from .map_info import MapDataInfo
from .save_data_manager import save_data

# 仅依赖 `get_logger` 的模块
from .songname_manager import song_name
from .acc_sync_diff_analyze import analyze_3d

# 依赖 `config`, `get_logger` 的模块
from .all_hit_analyze import AllHitAnalyze

# 依赖 `config`, `get_logger`, `song_name` 的模块
from .toolkit import Toolkit

# 依赖 `MapDataInfo` 和 `save_data` 的模块
from .difficulty_score_analyze import diff_score_analyze

# 依赖 `config`, `get_logger`, `song_name`, `analyze_3d`, `AllHitAnalyze` 的模块
from .hit_delay import HitDelay

# 依赖绝大多数包的模块，放在最后导入以避免循环依赖
from .musync_save_decode import MusyncSaveDecoder
from .main_window import MusyncMainWindow

__version__ = pre_version.replace("pre",".") if (is_pre_release) else version

# 定义公开接口（建议使用）
__all__ = [
    # .version
    "version",
    "pre_version",
    "is_pre_release",
    # .config_manager
    "config",
    "Logger",
    # .map_info
    "MapDataInfo",
    # .save_data_manager
    "save_data",
    # .songname_manager
    "song_name",
    # .acc_sync_diff_analyze
    "analyze_3d",
    # .all_hit_analyze
    "AllHitAnalyze",
    # .toolkit
    "Toolkit",
    # .difficulty_score_analyze
    "diff_score_analyze",
    # .hit_delay
    "HitDelay",
    # .musync_save_decode
    "MusyncSaveDecoder",
    # .main_window
    "MusyncMainWindow",
]

# 如果希望导入包时自动初始化配置，可以取消下面注释
Toolkit.init_resources()
