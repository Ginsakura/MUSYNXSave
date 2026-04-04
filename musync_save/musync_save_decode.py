# -*- coding: utf-8 -*-
import clr
import logging
import os
import sys
import time
from base64 import b64decode
from tkinter import messagebox
from typing import Any

from .config_manager import config, get_logger
from .songname_manager import song_name
from .save_data_manager import save_data
from .map_info import MapDataInfo
from .toolkit import Toolkit

logger:logging.Logger = get_logger(name="MUSYNCSavDecode")
try:
    # Load C# Lib
    # clr.AddReference("System.Runtime.Serialization.Formatters.Binary")
    clr.AddReference("mscorlib")
    from System import Reflection
    from System.IO import MemoryStream
    from System.Reflection import Assembly
    from System.Runtime.Serialization.Formatters.Binary import BinaryFormatter
except Exception:
    logger.exception("Import Error.")
    sys.exit(101)

class MusyncSaveDecoder(object):
    """docstring for MUSYNCSavProcess"""
    def __init__(self, savFile:str=''):
        super(MusyncSaveDecoder, self).__init__()
        self.__assembly_loaded:bool = False
        dllPath:str|None = None
        try:
            dllPath = './musync_data/Assembly-CSharp.dll'
            assembly = Assembly.LoadFrom(dllPath)
            self.__assembly = assembly
            self.__assembly_loaded = True
        except Exception:
            logger.exception(f"Failed to Load {dllPath or 'assembly (path construction failed)'}")
            raise
        self.savPath:str = savFile
        self.FavSong:list[str] = list()
        self.__logger:logging.Logger = get_logger(name="MUSYNCSavDecode.MUSYNCSavProcess")
        self.__logger.info("creating an instance in MUSYNCSavDecode")

    def Main(self):
        if os.path.isfile(self.savPath):
            self.LoadSaveFile()
            self.FixUserMemory()
            self.FavFix()
            save_data.dump_to_json()
        else:
            self.__logger.error(f"文件夹\"{self.savPath}\"内找不到存档文件.")
            messagebox.showerror("Error", "文件夹内找不到存档文件.")

    def LoadSaveFile(self)->None:
        '''加载存档文件并进行base64解码'''
        start_time: int = time.perf_counter_ns()
        self.__logger.debug("LoadSaveFile Start.")
        with open(self.savPath, 'r', encoding="utf-8") as file:
            base64_data = file.read()
        self.Deserialize(b64decode(base64_data))
        self.__logger.debug("LoadSaveFile End.")
        self.__logger.info(f"LoadSaveFile Run Time: {Toolkit.calc_end_time(start_time):.2f} ms")

    def Deserialize(self, data)->None:
        """反序列化存档数据"""
        start_time: int = time.perf_counter_ns()
        self.__logger.debug("SaveDeserialize Start.")
        stream:MemoryStream = MemoryStream(data)
        try:
            userMemory = (BinaryFormatter().Deserialize(stream))
        finally:
            stream.Dispose()
        userMemoryTypeInfo = userMemory.GetType()

        def GetNonPublicField(field,typeInfo=userMemoryTypeInfo,instance=userMemory)->Any:
            '''获取非公开的字段'''
            anyVar = typeInfo.GetField(field, Reflection.BindingFlags.NonPublic | Reflection.BindingFlags.Instance)
            return anyVar.GetValue(instance)

        def GetNonPublicMethod(field:str,typeInfo=userMemoryTypeInfo,instance=userMemory)->Any:
            '''获取非公开的Get方法'''
            # 获取 internal 属性的 PropertyInfo
            propertyInfo = typeInfo.GetProperty(field, Reflection.BindingFlags.Instance | Reflection.BindingFlags.NonPublic)
            # 获取属性值(调用 get 方法)
            method = propertyInfo.GetGetMethod(nonPublic=True)
            return method.Invoke(instance, None)

        def NetListToPyList(saveInfoList)->list[MapDataInfo]:
            '''将C# List<SongSaveInfo>转换为Python List[SongSaveInfoPy]'''
            saveInfos:list[MapDataInfo] = list()
            for songSaveInfo in saveInfoList:
                typeInfo2 = songSaveInfo.GetType()
                saveInfoPy:MapDataInfo = MapDataInfo(
                    GetNonPublicMethod("SongId", typeInfo=typeInfo2, instance=songSaveInfo),
                    GetNonPublicMethod("SpeedStall", typeInfo=typeInfo2, instance=songSaveInfo),
                    GetNonPublicMethod("SyncNumber", typeInfo=typeInfo2, instance=songSaveInfo),
                    GetNonPublicMethod("UploadScore", typeInfo=typeInfo2, instance=songSaveInfo),
                    GetNonPublicMethod("PlayCount", typeInfo=typeInfo2, instance=songSaveInfo),
                    GetNonPublicMethod("Isfav", typeInfo=typeInfo2, instance=songSaveInfo),
                    GetNonPublicMethod("CrcInt", typeInfo=typeInfo2, instance=songSaveInfo)
                    )
                saveInfos.append(saveInfoPy)
                # self.logger.debug(saveInfoPy)
            return saveInfos

        # # 修改 private 字段的值
        # secret_name_field.SetValue(instance, "Bob")
        # secret_age_field.SetValue(instance, 25)
        # 获取 private 字段的值
        fieldMappings: list[tuple[str, object]] = [
            ("version", int),
            ("crc", int),
            ("saveInfoList", lambda v: NetListToPyList(v)),
            ("purchaseIds", list),
            ("songIndex", int),
            ("isHard", int),
            ("buttonNumber", int),
            ("sortNum", int),
            ("missVibrate", bool),
            ("soundHelper", int),
            ("displayAdjustment", int),
            ("judgeCompensate", int),
            ("advSceneSettringString", str),
            ("metronomeSquipment", str),
            ("playTimeUIA", int),
            ("playTimeUIB", int),
            ("playTimeUIC", int),
            ("playTimeUID", int),
            ("playTimeUIE", int),
            ("playTimeUIF", int),
            ("playTimeRankEX", int),
            ("playTimeKnockEX", int),
            ("playTimeKnockNote", int),
            ("playVsync", bool),
            ("buttonSetting4K", list),
            ("buttonSetting6K", list),
            ("hiddenUnlockSongs", bool),
            ("hideLeaderboardMini", bool),
            ("playingSceneName", str),
            ("selectSongName", str),
            ("sceneName", str),
            ("busVolume", float),
            ("advSceneSettingString", str),
            ("dropSpeed", int),
            ("dropSpeedFloat", float),
            ("isOpenVSync", bool),
            ("hadSaveFpsAndVSync", bool),
            ("fps", int),
        ]
        for field, converter in fieldMappings:
            raw_value = GetNonPublicField(field)
            setattr(save_data, field, converter(raw_value))

        # 具有特殊来源的字段（直接从 userMemory 读取）
        save_data.AppVersion = int(userMemory.AppVersion)
        save_data.isUseUserMemoryDropSpeed = bool(userMemory.isUseUserMemoryDropSpeed)

        self.__logger.debug(save_data.to_dict(debug=True))
        self.__logger.debug("SaveDeserialize End.")
        self.__logger.info(f"SaveDeserialize Run Time: {Toolkit.calc_end_time(start_time):.2f} ms")

    def FixUserMemory(self) -> None:
        """补全缺失数据"""
        start_time: int = time.perf_counter_ns()
        self.__logger.debug("UserMemoryToJson Start.")

        # ==========================================
        # 内部纯函数定义
        # ==========================================

        def UpdateSongName(map_data: 'MapDataInfo') -> bool:
            """[核心修复] 获取并直接在原对象上更新谱面信息，防止游玩成绩丢失"""
            # 使用 song_name 单例的 data 属性，键名为字符串形式的 ID
            song_data: list | None = song_name.data.get(str(map_data.SongId))
            if song_data is None:
                return False

            # 安全获取 BuiltinSong 列表，防止不存在时抛出异常
            builtin_list: set[str] = set(song_name.data.get("BuiltinSong", []))
            is_builtin: bool = song_data[0] in builtin_list

            # 调用新版的类方法，直接在现有对象上附加名字和难度
            map_data.update_from_list(song_data, is_builtin)
            return True

        def NoCopyright(songId:int)->bool:
            """标记无版权曲目"""
            NCR = set(
                102801, 102802, 102811, 102812, #粉色柠檬
                104901, 104902, 104911, 104912, #TWINKLE STAR
                109601, 109602, 109611, 109612, #为你而来
                109701, 109702, 109711, 109712, #星之伊始
                109801, 109802, 109811, 109812, #观星者
                127501, 127502, 127511, 127512, #寓言预见遇见你的那刻
                129201, 129202, 129211, 129212, #404 Not Found
                129301, 129302, 129311, 129312, #ArroganT
                129401, 129402, 129411, 129412, #樂園 - Atlantis
                )
            return songId in NCR

        def OldAprilFoolsDay(songId:int) -> bool:
            """标记愚人节谱面"""
            OAFD = set(
                )
            return songId in OAFD

        # ==========================================
        # 遍历与状态清洗
        # ==========================================

        removeIndexList: list[int] = list()
        self.__logger.debug("|  SongID  | SpeedStall | SyncNumber |         UploadScore        | PlayCount |  State  |")

        # 遍历 save_data 管理器中的存档列表
        for saveIndex, mapData in enumerate(save_data.saveInfoList):

            # 【直接更新原对象】不再重写 mapData
            is_found = UpdateSongName(mapData)

            if not is_found or not mapData.SongName:
                mapData.State = "NoName"
                # 倒序插入待删除列表，这是极好的做法！
                removeIndexList.insert(0, saveIndex)
            elif mapData.Isfav:
                # 确保外部的 FavSong 列表存在
                if hasattr(self, 'FavSong'):
                    self.FavSong.append(mapData.SongName)
                mapData.State = "Favo"
            elif OldAprilFoolsDay(mapData.SongId):
                mapData.State = "Fool"
            elif NoCopyright(mapData.SongId):
                mapData.State = "NoCR"

            # 优化了冗余的字符串格式化，直接利用 f-string 的强大格式化能力
            self.__logger.debug(
                f'| {mapData.SongId:>8} | {mapData.SpeedStall:>10} | '
                f'{mapData.SyncNumber/100:>9.2f}% | {mapData.UploadScore*100:>25.21f}% | '
                f'{mapData.PlayCount:>9} | {mapData.State:>7} |'
            )
            # 因为 mapData 是引用传递，它在内存中的改变已经自动同步到列表里了！
            # save_data.saveInfoList[saveIndex] = mapData

        # ==========================================
        # 倒序删除无效记录
        # ==========================================
        for removeIndex in removeIndexList:
            save_data.saveInfoList.pop(removeIndex)

        self.__logger.debug("UserMemoryToJson End.")
        self.__logger.info(f"UserMemoryToJson Run Time: {Toolkit.calc_end_time(start_time):.2f} ms")

    def FavFix(self) -> None:
        """修复收藏仅应用于每首歌的4KEZ谱面的问题"""
        start_time: int = time.perf_counter_ns()
        self.__logger.debug("FavFix Start.")

        self.__logger.debug(f"Favorites List：{self.FavSong}")

        # 将列表转换为集合 (Set)。将 in 判定的时间复杂度从 O(N) 降为 O(1)，极大提升遍历速度
        fav_song_set = set(self.FavSong)

        # 抛弃 enumerate，直接遍历对象引用
        for mapData in save_data.saveInfoList:
            if mapData.SongName in fav_song_set:
                # 直接修改内存中的对象，无需回填 save_data.saveInfoList[index]
                mapData.State = "Favo"

                # 既然是修复游戏的收藏 Bug，必须同时把 Isfav 设为 True
                # 这样将来序列化写入 SaveDataInfo.json 时，游戏才能真正识别全难度的收藏状态！
                mapData.Isfav = True

        self.__logger.debug("FavFix End.")
        self.__logger.info(f"FavFix Run Time: {Toolkit.calc_end_time(start_time):.2f} ms")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('savPath', nargs='?', default=None, help='Path to savedata.sav')
    args = parser.parse_args()

    savPath = args.savPath or os.path.join(config.MainExecPath or '.', 'SavesDir', 'savedata.sav')

    Object = MusyncSaveDecoder(savPath)
    Object.Main()
