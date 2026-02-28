# -*- coding: utf-8 -*-
"""
数据清洗与格式化工具脚本 (Data Cleansing Utility)
用于维护和修复 musync_data/songname.json 的结构与键值对。
"""
import json
import os
from typing import Any, Dict

# ==================== 常量定义 ====================
SONG_NAME_JSON: str = './musync_data/songname.json'
SAV_ANALYZE_TXT: str = './musync_data/SavAnalyze.analyze'

# ==================== 辅助函数 ====================
def _load_json(filepath: str) -> Dict[str, Any]:
    """安全读取 JSON 文件，若不存在则返回空字典"""
    if not os.path.isfile(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_json(filepath: str, data: Dict[str, Any]) -> None:
    """安全保存 JSON 文件，保证中文不转码"""
    with open(filepath, 'w', encoding='utf-8') as f:
        # indent=4 增加可读性，可根据需要改为 indent=""
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== 核心功能 ====================
def format_missing_ids() -> None:
    """补全缺失的曲目 ID，将 15~1343 之间缺失的 ID 填充为 None"""
    data: Dict[str, Any] = _load_json(SONG_NAME_JSON)

    for ids in range(15, 1344):
        str_id = str(ids)
        if str_id not in data:
            data[str_id] = None

    _save_json(SONG_NAME_JSON, data)

def sort_json_keys() -> None:
    """对 JSON 文件的键 (Key) 进行字典序升序排序"""
    data: Dict[str, Any] = _load_json(SONG_NAME_JSON)

    # Python 3.7+ 的字典是有序的，直接根据 key 排序并重建字典
    sorted_data = dict(sorted(data.items(), key=lambda item: item[0]))
    print(f"排序完成，共 {len(sorted_data)} 条记录。")

    _save_json(SONG_NAME_JSON, sorted_data)

def switch_endianness() -> None:
    """将键名从 小端序 (Little-Endian) 转换为 大端序 (Big-Endian)"""
    data: Dict[str, Any] = _load_json(SONG_NAME_JSON)
    new_data: Dict[str, Any] = {}

    for old_key, value in data.items():
        # 仅对长度为 8 的十六进制字符串进行端序翻转转换
        if len(old_key) == 8:
            new_key = old_key[6:8] + old_key[4:6] + old_key[2:4] + old_key[0:2]
            new_data[new_key] = value
        else:
            new_data[old_key] = value

    _save_json(SONG_NAME_JSON, new_data)

if __name__ == '__main__':
    # 你可以在这里按需调用格式化函数
    # format_missing_ids()
    # format_legacy_data_structure()
    # sort_json_keys()
    print("工具脚本已就绪。")
