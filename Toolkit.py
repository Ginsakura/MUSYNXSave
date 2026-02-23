# -*- coding: utf-8 -*-
import gzip
import io
import json
import logging
import os
import re
import sqlite3
import struct
import threading
import time
import winreg

from hashlib import sha256
from tkinter import messagebox
from typing import Any, Optional
from win32 import win32gui, win32print
from win32.lib import win32con
from win32.win32api import GetSystemMetrics

from Resources import Config, Logger, SongName

_logger: logging.Logger = Logger().GetLogger("Toolkit")

class Toolkit:
    _logger: logging.Logger = Logger().GetLogger("Toolkit")
    _resource_file_info: dict[str, dict[str, Any]] = {}
    _is_resource_loaded: bool = False
    _resource_file: Optional[io.BufferedReader] = None
    _file_lock: threading.Lock = threading.Lock()

    @staticmethod
    def calc_end_time(start_time: int) -> float:
        return (time.perf_counter_ns() - start_time) / 1_000_000;

    @classmethod
    def init_resources(cls) -> None:
        """初始化加载打包的资源文件 (应在程序启动时显式调用)"""
        if cls._is_resource_loaded:
            return

        cls._logger.debug("加载资源文件: \"./musync_data/Resources.bin\".")
        try:
            cls._resource_file = open("./musync_data/Resources.bin", "rb")
            cls._resource_file.seek(0)

            info_size: int = struct.unpack('I', cls._resource_file.read(4))[0]
            compressed_stream = io.BytesIO(cls._resource_file.read(info_size))

            with gzip.GzipFile(fileobj=compressed_stream, mode='rb') as gz_file:
                decompressed_data: bytes = gz_file.read()

            cls._resource_file_info = json.loads(decompressed_data.decode('ascii'))
            cls._is_resource_loaded = True
        except Exception as ex:
            cls._logger.exception("资源文件加载失败.")
            messagebox.showerror("Error", f"资源文件\"./musync_data/Resources.bin\"加载失败!\n{ex}")

    @staticmethod
    def get_dpi() -> int:
        """获取系统 DPI 缩放比例 (e.g. 100 -> 100%)"""
        start_time: int = time.perf_counter_ns()
        h_dc = win32gui.GetDC(0)
        try:
            rel_width: int = win32print.GetDeviceCaps(h_dc, win32con.DESKTOPHORZRES)
            width: int = GetSystemMetrics(0)
            dpi: int = int(round(rel_width / width, 2) * 100)
        finally:
            win32gui.ReleaseDC(0, h_dc)
        _logger.debug(f"Get DPI: {dpi}")
        _logger.debug(f"get_dpi() Run Time: {Toolkit.calc_end_time(start_time):.2f} ms")
        return dpi

    @staticmethod
    def change_console_style() -> None:
        """修改终端控制台样式 (通过写注册表)"""
        start_time: int = time.perf_counter_ns()
        _logger.info('Changing Console Style...')

        config = Config()
        if not config.MainExecPath:
            Toolkit.get_save_file()

        if not config.MainExecPath:
            _logger.error('Not Have Config.MainExecPath!')
            return

        exec_path: str = config.MainExecPath.replace('/', '_') + 'musynx.exe'
        _logger.debug(f"execPath: {exec_path}")

        try:
            # 创建 Registry Key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Console', reserved=0, access=winreg.KEY_WRITE) as reg_key:
                winreg.CreateKey(reg_key, exec_path)

            # 设置样式值
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, f'Console\\{exec_path}', reserved=0, access=winreg.KEY_WRITE) as reg_key:
                winreg.SetValueEx(reg_key, 'CodePage', 0, winreg.REG_DWORD, 65001)
                winreg.SetValueEx(reg_key, 'WindowSize', 0, winreg.REG_DWORD, 262174)
                winreg.SetValueEx(reg_key, 'WindowAlpha', 0, winreg.REG_DWORD, (config.ConsoleAlpha * 255 // 100))
                winreg.SetValueEx(reg_key, 'FaceName', 0, winreg.REG_SZ, '霞鹜文楷等宽')
                winreg.SetValueEx(reg_key, 'FontSize', 0, winreg.REG_DWORD, (config.ConsoleFontSize << 16))
        except OSError as e:
            _logger.error(f"Failed to change console style: {e}")

        _logger.debug(f"change_console_style() Run Time: {Toolkit.calculate_end_time(start_time):.2f} ms")

    @staticmethod
    def get_hash(file_path: Optional[str] = None) -> str:
        """分块读取并获取文件 SHA256 哈希值 (大写)"""
        start_time: int = time.perf_counter_ns()
        if not file_path or not os.path.isfile(file_path):
            return ""

        sha256_hash = sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)

        hash_result: str = sha256_hash.hexdigest().upper()
        _logger.debug(f"get_hash() Run Time: {Toolkit.calculate_end_time(start_time):.2f} ms")
        return hash_result

    @classmethod
    def release_resource(cls, offset: int, length: int, release_path: Optional[str] = None) -> bytes:
        """从 VFS 释放单个资源，具备线程安全防护"""
        if not cls._is_resource_loaded or cls._resource_file is None:
            cls.init_resources()

        start_time: int = time.perf_counter_ns()

        with cls._file_lock:
            cls._resource_file.seek(offset)
            compressed_data: bytes = cls._resource_file.read(length)

        with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as gz_file:
            decompressed_data: bytes = gz_file.read()

        if release_path:
            with open(release_path, "wb") as f:
                f.write(decompressed_data)

        cls._logger.debug(f"release_resource() Run Time: {Toolkit.calculate_end_time(start_time):.2f} ms")
        return decompressed_data

    @classmethod
    def check_resources(cls, fonts: list[str]) -> None:
        """运行前环境与资源校验"""
        start_time: int = time.perf_counter_ns()
        cls.init_resources()

        cls._logger.debug("Check directory structure...")
        if os.path.exists('./musync/'):
            os.rename('./musync/', './musync_data/')
        os.makedirs('./musync_data/', exist_ok=True)
        os.makedirs("./logs/", exist_ok=True)
        os.makedirs('./skin/', exist_ok=True)

        if cls._is_resource_loaded:
            # 统一资源检查逻辑
            resources_to_check = [
                ("./LICENSE", "license"),
                ("./musync_data/MUSYNC.ico", "icon"),
                ("./musync_data/SongName.json", "song_name"),
                ("./mscorlib.dll", "core_lib"),
                ("./musync_data/LXGW.ttf", "font")
            ]

            for file_path, tag in resources_to_check:
                cls._logger.debug(f"Check if the \"{file_path}\" exists and is valid...")
                info = cls._resource_file_info[tag]

                # song_name 特殊逻辑 (按 Version 更新)
                if tag == "song_name":
                    if not os.path.isfile(file_path) or info["version"] > SongName.Version():
                        cls.release_resource(info["offset"], info["length"], file_path)
                # 常规哈希比对逻辑
                else:
                    if not os.path.isfile(file_path) or cls.get_hash(file_path) != info["hash"]:
                        cls.release_resource(info["offset"], info["length"], file_path)

            if '霞鹜文楷等宽' not in fonts:
                cls._logger.debug("Check if the \"霞鹜文楷等宽\" font is installed...")
                os.startfile(os.path.abspath(os.path.join('musync_data', 'LXGW.ttf')))

        cls._logger.debug("Check Database version...")
        cls.update_database(cls.check_database_version())

        cls._logger.debug("Check DLLInjection...")
        if Config.DLLInjection:
            cls.game_lib_check()

        cls._logger.debug(f"check_resources() Run Time: {Toolkit.calculate_end_time(start_time):.2f} ms")

    @classmethod
    def get_save_file(cls) -> str:
        """搜索预设存档目录"""
        start_time: int = time.perf_counter_ns()
        cls._logger.debug("正在搜索存档文件中……")

        drives = "CDEFGHIJKLMNOPQRSTUVWXYZAB"
        steam_paths = [
            "Program Files\\steam\\steamapps\\common\\MUSYNX\\",
            "SteamLibrary\\steamapps\\common\\MUSYNX\\",
            "steam\\steamapps\\common\\MUSYNX\\"
        ]

        for drive in drives:
            for path in steam_paths:
                full_path = f"{drive}:\\{path}"
                if os.path.isfile(f"{full_path}musynx.exe"):
                    cls._logger.debug(f"SaveFilePath: {full_path}")
                    Config.MainExecPath = full_path
                    Config.SaveConfig()
                    return full_path

        cls._logger.error("搜索不到存档文件.")
        cls._logger.info(f"get_save_file() Run Time: {Toolkit.calculate_end_time(start_time):.2f} ms")
        return ""

    @classmethod
    def game_lib_check(cls) -> int:
        """
        游戏脚本 DLL 检查与修补
        Returns:
            0: 无法修补或未匹配到修补条件
            1: 已修补 (包括已经是最新或修补成功)
        """
        start_time: int = time.perf_counter_ns()
        return_code: int = 0  # 初始化统一返回值
        dll_path: str = Config.MainExecPath + 'MUSYNX_Data/Managed/Assembly-CSharp.dll'
        EMPTY_HASH: str = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"

        # 使用嵌套逻辑确保流程最终能流向函数末尾
        if not os.path.isfile(dll_path):
            cls._logger.error(f"Assembly-CSharp.dll not found at \"{dll_path}\", skip DLLInjection.")
            return_code = 0
        else:
            now_hash: str = cls.get_hash(dll_path)
            # 假设资源信息已加载
            lib_info: dict = cls._resource_file_info.get("game_lib", {})
            source_hash: str = lib_info.get("source_hash", "")
            fix_hash: str = lib_info.get("hash", "")

            cls._logger.debug(f"    Now Assembly-CSharp.dll: {now_hash}")

            # 1. 检查是否已经是修补好的版本
            if now_hash == fix_hash:
                return_code = 1
            else:
                # 2. 检查是否符合修补条件
                # 逻辑：如果 source_hash 是空的，或者当前文件就是原版文件且不等于目标文件
                if (source_hash == EMPTY_HASH or
                    (source_hash == now_hash and source_hash != fix_hash)):
                    try:
                        old_dll: str = f'{dll_path}.old'
                        if os.path.isfile(old_dll):
                            os.remove(old_dll)
                        os.rename(dll_path, old_dll)

                        # 释放资源
                        cls.release_resource(lib_info["offset"],
                                             lib_info["length"],
                                             dll_path
                                             )
                        return_code = 1
                    except Exception as e:
                        cls._logger.error(f"修补过程中发生异常: {e}")
                        return_code = 0
                else:
                    return_code = 0

        # --- 统一出口 ---
        # 无论上述哪个分支执行，都会来到这里
        run_time_ms: float = Toolkit.calculate_end_time(start_time)
        cls._logger.debug(f"game_lib_check() Run Time: {run_time_ms:.2f} ms, "
                          f"Return Code: {return_code}")
        return return_code

    @staticmethod
    def create_new_database(db: sqlite3.Connection) -> None:
        """初始化新数据库结构"""
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS HitDelayHistory (
                SongMapName TEXT NOT NULL DEFAULT '',
                RecordTime TEXT NOT NULL DEFAULT '',
                Diff INTEGER NOT NULL DEFAULT 0,
                Keys TEXT NOT NULL DEFAULT '',
                Combo TEXT NOT NULL DEFAULT '0/0',
                AvgDelay FLOAT,
                AllKeys INTEGER,
                AvgAcc FLOAT,
                HitMap TEXT,
                PRIMARY KEY ("SongMapName", "RecordTime")
            );""")
        cursor.execute("CREATE TABLE IF NOT EXISTS Infos ("
                       "Key TEXT PRIMARY KEY,"
                       "Value TEXT DEFAULT NULL);")

    @classmethod
    def check_database_version(cls) -> int:
        """数据库版本检查"""
        start_time: int = time.perf_counter_ns()
        rt_code: int = -1

        try:
            if os.path.isfile("./musync_data/HitDelayHistory_v2.db"):
                with sqlite3.connect('./musync_data/HitDelayHistory_v2.db') as db:
                    cursor = db.cursor()
                    cursor.execute("PRAGMA table_info(HitDelayHistory);")
                    column_count = len(cursor.fetchall())
                    rt_code = 2 if column_count == 6 else 1
                    cls._logger.info(f"Database Version: {rt_code}")

            elif os.path.isfile("./musync_data/HitDelayHistory.db"):
                with sqlite3.connect('./musync_data/HitDelayHistory.db') as db:
                    cursor = db.cursor()
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
                    table_count = cursor.fetchone()[0]

                    if table_count == 1:
                        rt_code = 1
                    else:
                        cursor.execute("SELECT Value FROM Infos WHERE Key='Version';")
                        rt_code = int(cursor.fetchone()[0])
                    cls._logger.info(f"Database Version: {rt_code}")
            else:
                cls._logger.warning("无数据库文件存在.")
                rt_code = 0

        except Exception as e:
            cls._logger.fatal(f"CheckDatabaseVersion() 异常: {e}")

        cls._logger.debug(f"check_database_version() Run Time: {Toolkit.calculate_end_time(start_time):.2f} ms")
        return rt_code

    @classmethod
    def update_database(cls, now_version: int) -> bool:
        """安全的数据库结构更新 (瀑布式流转)"""
        start_time: int = time.perf_counter_ns()
        target_version: int = 4

        if now_version == -1:
            return False

        if now_version == 2:
            os.rename("./musync_data/HitDelayHistory_v2.db",
                      "./musync_data/HitDelayHistory.db")

        # 核心修复：使用 with db 确保所有操作为一个完整的事务，失败自动回滚
        with sqlite3.connect('./musync_data/HitDelayHistory.db') as db:
            cursor:sqlite3.Cursor = db.cursor()

            try:
                # V0 -> V4: 直接创建最新表
                if now_version == 0:
                    cls._logger.info(f"创建 v{target_version} 版本数据库中...")
                    cls.create_new_database(db)
                    cursor.execute("INSERT OR REPLACE INTO Infos VALUES(?, ?)",
                                   ("Version", str(target_version)))
                    now_version = target_version

                # V1 -> V2
                if now_version == 1:
                    cls._logger.info("记录数据迁移中... v1 -> v2")
                    cursor.execute("ALTER TABLE HitDelayHistory RENAME TO HitDelayHistoryV1;")
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS HitDelayHistory (
                            SongMapName TEXT NOT NULL,
                            RecordTime TEXT NOT NULL,
                            AvgDelay FLOAT,
                            AllKeys INTEGER,
                            AvgAcc FLOAT,
                            HitMap TEXT,
                            PRIMARY KEY ("SongMapName", "RecordTime")
                        );""")
                    for ids in cursor.execute("SELECT * FROM HitDelayHistoryV1").fetchall():
                        name_and_time = ids[0].split("-202")
                        name, record_time = name_and_time[0], f"202{name_and_time[1]}"
                        cursor.execute(
                            "INSERT INTO HitDelayHistory VALUES(?,?,?,?,?,?)",
                            (name, record_time, ids[1], ids[2], ids[3], ids[4])
                        )
                    cursor.execute("DROP TABLE HitDelayHistoryV1;")
                    now_version = 2

                # V2 -> V3
                if now_version == 2:
                    cls._logger.info("记录数据迁移中... v2 -> v3")
                    cursor.execute("CREATE TABLE IF NOT EXISTS Infos ("
                                   "Key TEXT PRIMARY KEY,"
                                   "Value TEXT DEFAULT NULL);"
                                   )
                    cursor.execute("INSERT OR REPLACE INTO Infos VALUES(?, ?)",
                                   ("Version", "3"))
                    now_version = 3

                # V3 -> V4
                if now_version == 3:
                    cls._logger.info("记录数据迁移中... v3 -> v4")
                    cursor.execute("ALTER TABLE HitDelayHistory ADD COLUMN "
                                   "Diff INTEGER NOT NULL DEFAULT 0")
                    cursor.execute("ALTER TABLE HitDelayHistory ADD COLUMN "
                                   "Mode TEXT NOT NULL DEFAULT ''")
                    cursor.execute("ALTER TABLE HitDelayHistory ADD COLUMN "
                                   "Combo TEXT NOT NULL DEFAULT '0/0'")

                    # 预编译双重正则
                    # 1. 严格末尾匹配 (最安全，覆盖 95% 以上的标准情况)
                    pattern_end: re.Pattern = re.compile(
                        r'\s*(4|6)[Kk]?(ez|e|hd|h|in|i)\s*$',
                        re.IGNORECASE
                        )

                    # 2. 中间宽泛匹配 (Fallback 方案，匹配被前后夹击的难度标识)
                    # 注意：两边加上 \s+ 或边界，
                    # 防止像 "xxxx4ever" 这种单词中间被误识别为 4e (4K EZ)
                    pattern_mid: re.Pattern = re.compile(
                        r'\s+(4|6)[Kk]?(ez|e|hd|h|in|i)\s+',
                        re.IGNORECAS
                        )

                    cursor.execute("SELECT ROWID, SongMapName FROM HitDelayHistory")
                    rows: list[Any] = cursor.fetchall()
                    update_data = []

                    for row_id, old_name in rows:
                        if not old_name:
                            continue

                        # === 优先尝试：末尾严格匹配 ===
                        matchs = pattern_end.search(old_name)
                        if matchs:
                            key_num: str = matchs.group(1)
                            diff_raw: str = matchs.group(2).upper()
                            diff_std: str = 'IN'
                            if diff_raw.startswith('E'):
                                diff_std = 'EZ'
                            elif diff_raw.startswith('H'):
                                diff_std = 'HD'
                            std_keys: str = f"{key_num}K{diff_std}"

                            cleaned_name: str = old_name[:matchs.start()].strip()
                            update_data.append((cleaned_name, std_keys, row_id))
                            continue  # 匹配成功，直接进入下一条记录

                        # === Fallback 策略：尝试中间匹配 ===
                        match_mid = pattern_mid.search(old_name)
                        if match_mid:
                            key_num: str = match_mid.group(1)
                            diff_raw: str = match_mid.group(2).upper()
                            diff_std: str = 'IN'
                            if diff_raw.startswith('E'):
                                diff_std = 'EZ'
                            elif diff_raw.startswith('H'):
                                diff_std = 'HD'
                            std_keys: str = f"{key_num}K{diff_std}"

                            # 抽离中间的难度字符串，拼接左右两侧的内容
                            # 例如 "葬歌 4KHD 2D" -> "葬歌" + " " + "2D"
                            left_part = old_name[:match_mid.start()]
                            right_part = old_name[match_mid.end():]
                            cleaned_name = f"{left_part} {right_part}".strip()

                            # 合并可能产生的多余空格 (例如 "葬歌  2D" -> "葬歌 2D")
                            cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

                            update_data.append((cleaned_name, std_keys, row_id))
                            continue  # 匹配成功，进入下一条

                        # === 极端情况：两套正则都没匹配上 ===
                        cls._logger.warning(f"无法识别难度的异常谱面名称: [{old_name}]，跳过迁移。")

                    if update_data:
                        cursor.executemany("UPDATE HitDelayHistory SET SongMapName = ?, Mode = ? WHERE ROWID = ?", update_data)
                        cls._logger.debug(f"成功清理并更新了 {len(update_data)} 条记录。")

                    cursor.execute("UPDATE Infos SET Value = ? WHERE Key = ?", (str(target_version), "Version"))
                    now_version = target_version

            except sqlite3.Error as e:
                cls._logger.error(f"数据库更新失败并已回滚，原因: {e}")
                return False

        cls._logger.info("数据库状态检查通过.")
        cls._logger.debug(f"update_database() Run Time: {Toolkit.calculate_end_time(start_time):.2f} ms")
        return True
