# -*- coding: utf-8 -*-
from dataclasses import dataclass, asdict
from typing import Any

# ==========================================
# 1. 纯血数据模型 (Data Models)
# ==========================================

@dataclass
class MapInfo:
    """基础谱面信息，直接映射 C# 内存结构中的部分字段"""
    SongName: str = ""
    SongKeys: str = ""
    SongDifficulty: str = "Unknown"
    SongDifficultyNumber: str = "00"
    SongIsBuiltin: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class MapDataInfo(MapInfo):
    """包含了谱面数据的完整信息，直接映射 C# 内存结构"""
    SongId: int = 0
    SpeedStall: int = 0
    SyncNumber: int = 0
    UploadScore: float = 0.0
    PlayCount: int = 0
    Isfav: bool = False
    CrcInt: int = 0
    State: str = "    "

    def update_from_list(self, info: list, is_builtin: bool = False) -> None:
        """从列表中更新谱面信息，确保数据完整性和类型安全"""
        if not info or len(info) < 4: return
        self.SongName = str(info[0])
        self.SongKeys = "4Key" if info[1] == 4 else "6Key"
        difficulties = ["Easy", "Hard", "Inferno"]
        self.SongDifficulty = difficulties[info[2]] if 0 <= info[2] < len(difficulties) else "Unknown"
        self.SongDifficultyNumber = f"{info[3]:02d}"
        self.SongIsBuiltin = is_builtin

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.update({
            "SongId": f"{self.SongId:08X}",
            "SpeedStall": f"{self.SpeedStall:08X}",
            "SyncNumber": f"{self.SyncNumber / 100.0}%",
            "UploadScore": f"{self.UploadScore * 100.0}%"
        })
        return data
