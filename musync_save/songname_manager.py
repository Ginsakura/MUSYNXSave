# -*- coding: utf-8 -*-
import json
from pathlib import Path
from typing import Any

from .config_manager import get_logger

class SongNameManager:
    """管理 MUSYNXSave 中的 SongName.json 文件，提供版本控制和数据访问功能。"""

    def __init__(self):
        # 文件路径
        self._file_path = Path.cwd() / "musync_data" / "SongName.json"
        # 数据结构
        self.data: dict[str, list] = {}
        # 日志记录器
        self.logger = get_logger("SongNameManager")
        # 尝试加载文件，如果不存在则初始化为空字典
        self.load_file()

    @property
    def version(self) -> int:
        """安全访问版本号，如果数据未加载或格式不正确返回0"""
        return self.data.get("version", 0) if self.data else 0

    @property
    def file_path(self) -> str:
        """返回 SongName.json 的绝对路径字符串"""
        return str(self._file_path)

    def load_file(self) -> None:
        """加载 SongName.json 文件，如果文件不存在则初始化为空字典"""
        if not self._file_path.is_file():
            self.data = {}
            return
        with open(self._file_path, 'r', encoding='utf8') as f:
            try:
                self.data = json.load(f)
            except Exception:
                self.logger.exception(
                    f"Failed to load SongName.json from {self.file_path}")

song_name = SongNameManager()
