# -*- coding: utf-8 -*-
import gzip
import json
import logging
import shutil
from pathlib import Path

from .version import version, pre_version, is_pre_release

# ==========================================
# 日志系统初始化 (完全替代旧版 Logger 类)
# ==========================================
_LOG_FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_LOG_FILE_PATH = Path.cwd() / "log.txt"

def get_logger(name: str="MUSYNC.App") -> logging.Logger:
    """
    全局日志获取函数，替代旧版的 Logger.GetLogger
    """
    # 动态获取当前的日志过滤等级
    # 因为全局 config 还没定义时也可能调用此函数，所以需要一个默认值 fallback
    try:
        current_level = config._logger_filter
    except NameError:
        current_level = logging.INFO

    logger = logging.getLogger(name)
    for i in logger.handlers:
        i.setLevel(current_level)

    # 核心：避免为同一个名字的 logger 重复添加 Handler 导致日志输出多次
    if not logger.hasHandlers():
        # 1. 写入 log.txt
        file_handler = logging.FileHandler(_LOG_FILE_PATH, encoding='utf-8')
        file_handler.setLevel(current_level)
        file_handler.setFormatter(_LOG_FORMATTER)

        # 2. 输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(current_level)
        console_handler.setFormatter(_LOG_FORMATTER)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

class AppConfigManager:
    _log_level_mapping = {
        "NOTSET": logging.NOTSET, "DEBUG": logging.DEBUG, "INFO": logging.INFO,
        "WARN": logging.WARNING, "WARNING": logging.WARNING, "ERROR": logging.ERROR,
        "FATAL": logging.CRITICAL, "CRITICAL": logging.CRITICAL,
    }

    def __init__(self):
        self._base_path: Path = Path.cwd()
        self._file_path: Path = self._base_path / "musync_data" / "bootcfg.json"
        self._log_path: Path = self._base_path / "log.txt"
        self._logs_dir: Path = self._base_path / "logs"
        self._logger_filter: int = logging.INFO

        self.compress_log_file()

        # 配置属性
        self.Version: str = pre_version if is_pre_release else version
        self.UpdateChannel: str = "PreRelease" if is_pre_release else "Release"
        self.LoggerFilterString: str = "INFO"
        self.CheckUpdate: bool = True
        self.DllInjection: bool = False
        self.SystemDpi: int = 100
        self.DonutChartInHitDelay: bool = True
        self.DonutChartInAllHitAnalyze: bool = True
        self.NarrowDelayInterval: bool = True
        self.ConsoleAlpha: int = 75
        self.ConsoleFont: str = "霞鹜文楷等宽"
        self.ConsoleFontSize: int = 36
        self.MainExecPath: str = ""
        self.ChangeConsoleStyle: bool = True

        self.load_config()

    def load_config(self):
        """加载配置文件，动态赋值属性"""
        # 检查配置文件是否存在，若存在则加载配置，否则保持默认值
        if not self._file_path.is_file(): return
        try:
            # 打开配置文件并加载 JSON 数据，动态赋值给属性
            with open(self._file_path, 'r', encoding='utf8') as f:
                data = json.load(f)
                # 动态赋值，因为属性名现在与 JSON 键名严格一致
                for k, v in data.items():
                    if hasattr(self, k):
                        setattr(self, k, v)

            self._logger_filter = self._log_level_mapping.get(self.LoggerFilterString, logging.INFO)

            self._logger: logging.Logger = get_logger("AppConfigManager")
            self._logger.info("Configuration loaded.")

        except Exception:
            self._logger: logging.Logger = get_logger("AppConfigManager")
            self._logger.exception("Failed to load configuration.")

    def compress_log_file(self) -> None:
        """压缩当前日志文件并归档到 logs 目录，命名为 log.{index}.gz，index 从 0 开始递增"""
        # 检查日志文件是否存在，若存在则压缩并归档到 logs 目录
        self._logs_dir.mkdir(exist_ok=True)
        if not self._log_path.is_file():
            return

        # 生成日志索引(以目录中文件数)
        next_index: int = len(list(self._logs_dir.glob("log.*.gz")))
        # 生成目标路径
        target_gz_path: Path = self._logs_dir / f"log.{next_index}.gz"
        # 拼接目标日志路径
        target_log_path: Path = self._logs_dir / self._log_path.name

        # 移动日志文件到目标路径
        shutil.move(str(self._log_path), str(target_log_path))
        # 压缩日志文件
        with open(target_log_path, 'rb') as f_in, gzip.open(target_gz_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        # 删除原始日志文件
        target_log_path.unlink()

    def save_config(self) -> None:
        """保存当前配置到 JSON 文件，自动过滤掉内部属性和非基本类型属性（如 Path 和 Logger）"""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._file_path, 'w', encoding='utf8') as f:
                # 过滤掉内部属性
                export_data = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            self._logger.info("Configuration saved.")
        except Exception:
            self._logger.exception("Failed to save configuration.")

config = AppConfigManager()
