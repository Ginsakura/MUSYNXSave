# -*- coding: utf-8 -*-
import json
from pathlib import Path
from typing import Any, List

from .config_manager import get_logger
from .map_info import MapDataInfo

class SaveDataManager:
    def __init__(self):
        self._file_path = Path.cwd() / "musync_data" / "SaveDataInfo.json"
        self.logger = get_logger("Resources.SaveDataInfo")

        # 属性名严格保持 C# 内存中的命名
        self.version: int = 0
        self.crc: int = 0
        self.saveInfoList: List[MapDataInfo] = []
        self.purchaseIds: List[str] = []
        self.songIndex: int = 1
        self.isHard: int = 0
        self.buttonNumber: int = 4
        self.sortNum: int = 0
        self.missVibrate: bool = False
        self.soundHelper: int = 3
        self.displayAdjustment: int = 0
        self.judgeCompensate: int = 0
        self.advSceneSettringString: str = ""
        self.metronomeSquipment: str = ""
        self.playTimeUIA: int = 0
        self.playTimeUIB: int = 0
        self.playTimeUIC: int = 0
        self.playTimeUID: int = 0
        self.playTimeUIE: int = 0
        self.playTimeUIF: int = 0
        self.playTimeRankEX: int = 0
        self.playTimeKnockEX: int = 0
        self.playTimeKnockNote: int = 0
        self.playVsync: bool = True
        self.buttonSetting4K: List[int] = []
        self.buttonSetting6K: List[int] = []
        self.hiddenUnlockSongs: bool = False
        self.hideLeaderboardMini: bool = True
        self.playingSceneName: str = ""
        self.selectSongName: str = "luobi"
        self.sceneName: str = "SelectSongScene"
        self.busVolume: float = 0.0
        self.advSceneSettingString: str = "\n"
        self.dropSpeed: int = 8
        self.dropSpeedFloat: float = 0.0
        self.isOpenVSync: bool = True
        self.hadSaveFpsAndVSync: bool = False
        self.fps: int = 60
        self.AppVersion: int = 0
        self.isUseUserMemoryDropSpeed: bool = True

    def to_dict(self, debug=False) -> dict[str, Any]:
        """极致精简：直接导出内部字典，保持原汁原味的命名"""
        data = {}
        # 直接使用 __dict__，但过滤掉私有属性和 logger
        for key, value in self.__dict__.items():
            if key.startswith('_') or key == 'logger':
                continue

            if key == 'saveInfoList':
                data[key] = ["DEBUG"] if debug else [info.to_dict() for info in value]
            else:
                data[key] = value
        return data

    def dump_to_json(self) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.info("SaveDataInfo successfully saved.")
        except Exception:
            self.logger.exception("Failed to save SaveDataInfo.json")

save_data = SaveDataManager()
