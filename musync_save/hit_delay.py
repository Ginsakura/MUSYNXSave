# -*- coding: utf-8 -*-
import logging
import os
import pyperclip
import struct
import sqlite3
import time
import tkinter as tk
import uiautomation as uiauto
from datetime import datetime as dt

from matplotlib import pyplot as plt
from tkinter import ttk, messagebox
from typing import Any, Literal, Optional

# 外部数据分析模块导入
from .config_manager import config, Logger
from .songname_manager import song_name
from .acc_sync_diff_analyze import analyze_3d
from .all_hit_analyze import AllHitAnalyze

uiauto.SetGlobalSearchTimeout(1)

class HitDelay:
    """游玩延迟与历史记录可视化分析主界面"""
    _const_keys_mode: dict[int, str] = {4:"4K", 6:"6K"}
    _const_diff_mode: list[str] = ["EZ", "HD", "IN", "ERR"]

    def __init__(self, subroot: tk.Tk | tk.Toplevel) -> None:
        self._logger: logging.Logger = Logger.get_logger("HitDelay.HitDelayText")

        db_path: str = './musync_data/HitDelayHistory.db'
        if not os.path.isfile(db_path):
            self._logger.fatal("Database Not Exists!")
            messagebox.showerror("Error", '发生错误: HitDelayHistory.db 数据库文件不存在!')
            return

        self._db: sqlite3.Connection = sqlite3.connect(db_path)
        self._db.row_factory = sqlite3.Row
        self._cursor: sqlite3.Cursor = self._db.cursor()

        self._subroot: tk.Tk | tk.Toplevel = subroot
        self._font: tuple[str, int] = ('霞鹜文楷等宽', 16)

        try:
            self._subroot.iconbitmap('./musync_data/Musync.ico')
        except Exception:
            self._logger.warning("Musync.ico 未找到，使用默认图标")

        self._subroot.geometry('1200x600+300+300')
        self._subroot.title("高精度延迟分析")
        self._subroot['background'] = '#efefef'

        self._style: ttk.Style = ttk.Style()
        self._style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',13))
        self._style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',15))
        self._style.configure("TButton", font=self._font, relief="raised")
        self._style.configure("update.TButton", font=self._font, relief="raised",background='#A6E22B')
        self._style.configure("delete.TButton", font=self._font, relief="raised", foreground='#FF4040', background='#FF2020')
        # 全局修改所有 ttk.Combobox 下拉列表 (Listbox) 的字体
        self._subroot.option_add('*TCombobox*Listbox.font', self._font)

        # TODO: 绑定全局按键
        self._subroot.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._subroot.bind('<F5>', self._action_refresh_data)
        self._subroot.bind('<Escape>', self._on_closing)
        self._subroot.bind("<Control-r>", self._reset_ui_state)

        # 全局状态容器
        self._data_song_name: str = ""
        self._data_record_time: str = ""
        self._data_diff: int = 0
        self._data_mode: str = ""
        self._data_combo: str = ""
        self._data_avg_delay: float = 0.0
        self._data_all_keys: int = 0
        self._data_avg_acc: float = 0.0
        self._data_bytes: bytes = b''
        self._data_list: list[int] = []
        self._select_rowid: int = -1
        self._game_console_handle: Optional[uiauto.DocumentControl] = None;

        # MVC 架构流转：初始化视图 -> 加载数据 -> 渲染数据
        self._init_ui()
        self._action_refresh_data()

    # ==========================================
    # [Level 0] 视图初始化与布局层 (View / UI)
    # ==========================================
    def _init_ui(self) -> None:
        """初始化动态流式 UI 布局 (嵌套 Grid 架构)"""
        # 1. 主容器 (左右分割)
        main_frame: tk.Frame = tk.Frame(self._subroot, bg='#efefef')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        main_frame.columnconfigure(0, weight=1)  # 左侧数据区：弹性拉伸
        main_frame.columnconfigure(1, weight=0)  # 右侧控制区：锁定宽度
        main_frame.rowconfigure(0, weight=1)

        # ---------------- 左侧：数据表格区域 ----------------
        data_frame: tk.Frame = tk.Frame(main_frame, relief="groove", borderwidth=2)
        data_frame.grid(row=0, column=0, sticky="nsew", padx=0) # padx=(0, 0)

        data_frame.columnconfigure(0, weight=1)  # Treeview 弹性拉伸
        data_frame.columnconfigure(1, weight=0)  # Scrollbar 固定宽度
        data_frame.rowconfigure(0, weight=1)

        # 适配 V4 数据库结构
        columns: tuple[str, ...] = ("rowid", "song_name", "record_time", "mode",
                                    "diff", "combo", "notes", "avg_delay", "avg_acc")
        self._treeview: ttk.Treeview = ttk.Treeview(data_frame, show="headings",
                                                    columns=columns, selectmode='browse')

        headings: list[tuple[str, str, int, Literal['w', 'center', 'e']]] = [
            ("rowid", "ID", 40, tk.E),
            ("song_name", "曲名", 180, tk.W),
            ("record_time", "记录时间", 140, tk.W),
            ("mode", "模式", 50, tk.CENTER),
            ("diff", "难度", 45, tk.CENTER),
            ("combo", "Combo", 80, tk.E),
            ("notes", "Notes", 60, tk.E),
            ("avg_delay", "平均延迟", 120, tk.E),
            ("avg_acc", "平均准度", 120, tk.E)
        ]

        for col_id, title, width, anchor in headings:
            self._treeview.heading(col_id, anchor=tk.CENTER, text=title)
            self._treeview.column(col_id, anchor=anchor, width=width)
            # 如果是曲名或时间，允许拉伸；其他列固定宽度
            is_stretch = col_id in ["song_name", "record_time"]
            self._treeview.column(col_id, anchor=anchor, width=width, stretch=is_stretch)

        # 绑定大小改变事件
        # self._treeview.bind("<Configure>", self._on_treeview_resize)
        self._treeview.bind("<<TreeviewSelect>>", self._on_tree_select)
        self._treeview.bind("<Double-1>", self._on_tree_double_click)

        # 滚动条绑定
        self._bar: tk.Scrollbar = tk.Scrollbar(data_frame, command=self._treeview.yview)
        self._treeview.configure(yscrollcommand=self._bar.set)

        self._treeview.grid(row=0, column=0, sticky="nsew")
        self._bar.grid(row=0, column=1, sticky="ns")

        # ---------------- 右侧：控制面板区域 ----------------
        ctrl_frame: tk.Frame = tk.Frame(main_frame, bg='#efefef', width=300,
                                        relief="groove", borderwidth=2)
        ctrl_frame.grid(row=0, column=1, sticky="ns", padx=0, pady=0)
        # 强制锁定宽度
        ctrl_frame.grid_propagate(False)
        # ctrl_frame.pack_propagate(False)
        ctrl_frame.columnconfigure(0, weight=1)

        control_grid: tk.Frame = tk.Frame(ctrl_frame, bg='#efefef')
        control_grid.grid(row=0, column=0, sticky="nsew", padx=2, pady=(30, 0))
        # 将 0列 和 1列 划入同一个 uniform 组 "col"
        control_grid.columnconfigure(0, weight=1, uniform="col")
        control_grid.columnconfigure(1, weight=1, uniform="col")
        # 将 0行 和 1行 划入同一个 uniform 组 "row"
        control_grid.rowconfigure(0, weight=1, uniform="row")
        control_grid.rowconfigure(1, weight=1, uniform="row")

        control_row: int = 0
        # 各种操作按钮映射到 Controller 层
        self._get_data_button: ttk.Button = ttk.Button(
            control_grid,
            text="获取结果",
            style="TButton",
            command=self._action_get_console_data)
        self._update_data_button: ttk.Button = ttk.Button(
            control_grid,
            text="刷新",
            style="TButton",
            command=self._action_refresh_data)
        self._get_data_button.grid(row=control_row, column=0, sticky="nsew", padx=2, pady=2)
        self._update_data_button.grid(row=control_row, column=1, sticky="nsew", padx=2, pady=2)
        control_row += 1

        self._all_hit_button: ttk.Button = ttk.Button(
            control_grid,
            text="All Hit",
            style="TButton",
            command=self._action_show_all_hit)
        self._avg_sync_button: ttk.Button = ttk.Button(
            control_grid,
            text="Acc-Sync-Diff\n   3D 图表",
            style="TButton",
            command=analyze_3d)
        self._all_hit_button.grid(row=control_row, column=0, sticky="nsew", padx=2, pady=2)
        self._avg_sync_button.grid(row=control_row, column=1, sticky="nsew", padx=2, pady=2)

        info_modify_frame: tk.Frame = tk.Frame(ctrl_frame, relief="groove", borderwidth=2)
        info_modify_frame.grid(row=1, column=0, sticky='n', padx=2, pady=(30, 0))
        info_modify_frame.columnconfigure(0, weight=2, uniform="info_grid")
        info_modify_frame.columnconfigure(1, weight=3, uniform="info_grid")

        info_modify_row: int = 0

        # 行0: '谱面游玩标识'
        history_name_label: tk.Label = tk.Label(
            info_modify_frame,
            text='谱面游玩标识',
            font=self._font,
            relief="groove")
        history_name_label.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew', padx=0, pady=0)
        info_modify_row += 1

        # 行1: 铺面游玩标识名称显示
        self._his_name_entry = tk.Entry(info_modify_frame, font=self._font, relief="sunken")
        self._his_name_entry.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew')
        info_modify_row += 1

        # 行2: '记录时间'
        history_record_time_label: tk.Label = tk.Label(
            info_modify_frame,
            text='记录时间',
            font=self._font,
            relief="groove")
        history_record_time_label.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew')
        info_modify_row += 1

        # 行3: 铺面游玩时间显示
        self._his_record_time_value: tk.Label = tk.Label(
            info_modify_frame,
            text="",
            font=self._font,
            relief="groove")
        self._his_record_time_value.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew')
        info_modify_row += 1

        # 行4: 游玩模式显示
        history_mode_label: tk.Label = tk.Label(
            info_modify_frame,
            text='模式: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_mode_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._his_mode_value: ttk.Combobox = ttk.Combobox(
            info_modify_frame,
            values=['', '4KEZ', '4KHD', '4KIN', "6KEZ", "6KHD", "6KIN"],
            font=self._font,
            state="readonly")
        self._his_mode_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行5: 游玩难度显示
        history_difficulty_label: tk.Label = tk.Label(
            info_modify_frame,
            text='难度: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_difficulty_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._his_difficulty_value: ttk.Combobox = ttk.Combobox(
            info_modify_frame,
            values=[f"{i}" for i in range(1, 16)],
            font=self._font)
        self._his_difficulty_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行6: Combo显示
        history_combo_label: tk.Label = tk.Label(
            info_modify_frame,
            text='Combo: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_combo_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._his_combo_value: tk.Label = tk.Label(
            info_modify_frame,
            text="0/0    ",
            font=self._font,
            relief="groove",
            anchor='e')
        self._his_combo_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行7: Notes数量显示
        history_notes_label: tk.Label = tk.Label(
            info_modify_frame,
            text='按键数量: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_notes_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._his_notes_value: tk.Label = tk.Label(
            info_modify_frame,
            text="0    ",
            font=self._font,
            relief="groove",
            anchor='e')
        self._his_notes_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行8: Avg Delay显示
        history_delay_label: tk.Label = tk.Label(
            info_modify_frame,
            text='平均延迟: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_delay_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._his_delay_value: tk.Label = tk.Label(
            info_modify_frame,
            text="000.000000ms  ",
            font=self._font,
            relief="groove",
            anchor='e')
        self._his_delay_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行9: Avg Acc显示
        history_acc_label: tk.Label = tk.Label(
            info_modify_frame,
            text='AvgAcc: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_acc_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._his_acc_value: tk.Label = tk.Label(
            info_modify_frame,
            text='000.000000ms  ',
            font=self._font,
            relief="groove",
            anchor='e')
        self._his_acc_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行10: 操作按钮
        self._his_update_button: ttk.Button = ttk.Button(
            info_modify_frame,
            text='更新记录',
            style="update.TButton",
            command=self._action_change_mark)
        self._his_update_button.grid(row=info_modify_row, column=0, sticky='ew')

        self._his_delete_button: ttk.Button = ttk.Button(
            info_modify_frame,
            text='删除记录',
            style="delete.TButton",
            command=self._action_delete_record)
        self._his_delete_button.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        for i in range(info_modify_row):
            info_modify_frame.rowconfigure(i, weight=1, uniform="info_grid")


    # ==========================================
    # [Level 2] 数据访问与解析层 (Model / DAL)
    # ==========================================
    def _fetch_history_records(self) -> list[tuple[Any, ...]]:
        """[纯函数] 仅负责从 V4 数据库获取全部历史记录"""
        try:
            self._cursor.execute("SELECT ROWID, SongMapName, RecordTime, Mode, Diff, Combo, AllKeys, AvgDelay, AvgAcc FROM HitDelayHistory")
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            self._logger.error(f"查询历史记录失败: {e}")
            return []

    def _parse_hitmap(self, rowid: int) -> bytes:
        """[纯函数] 负责从 V4 数据库读取 BLOB 并反序列化为小端整数列表"""
        try:
            self._cursor.execute("SELECT HitMap FROM HitDelayHistory WHERE ROWID=?", (rowid,))
            result = self._cursor.fetchone()
            if not result or not result[0]:
                return b''

            return result[0]
        except sqlite3.Error as e:
            self._logger.error(f"查询 HitMap 数据失败: {e}")
        return b''

    def _fetch_record_by_rowid(self, rowid: int) -> Optional[sqlite3.Row]:
        """[纯函数] 扩展自 _parse_hitmap: 根据 ROWID 获取一整行完整数据（包含 HitMap）"""
        try:
            # 使用 SELECT * 或者显式列出所有列
            self._cursor.execute("""
                SELECT ROWID, SongMapName, RecordTime, Mode, Diff, Combo, AllKeys, AvgDelay, AvgAcc, HitMap
                FROM HitDelayHistory
                WHERE ROWID=?
            """, (rowid,))

            # fetchone() 会返回单一的 sqlite3.Row 对象，如果没有找到则返回 None
            return self._cursor.fetchone()
        except sqlite3.Error as e:
            self._logger.error(f"查询单条完整记录失败 (ROWID: {rowid}): {e}")
            return None

    def _db_delete_record(self, rowid: int) -> bool:
        """[纯函数] 删除指定 ROWID 的记录"""
        try:
            self._cursor.execute("DELETE FROM HitDelayHistory WHERE ROWID=?", (rowid,))
            self._db.commit()
            return self._cursor.rowcount > 0  # 返回是否真的删除了数据
        except sqlite3.Error as e:
            self._logger.error(f"删除记录失败 (ROWID: {rowid}): {e}")
            return False

    def _get_console_handle(self) -> None:
        try:
            # 尝试查找常规状态下的控制台
            win = uiauto.WindowControl(searchDepth=1, Name='MUSYNX Delay', searchInterval=1)
            self._game_console_handle = win.DocumentControl(searchDepth=1, Name='Text Area', searchInterval=1)
            return
        except Exception:
            self._logger.warning("常规控制台窗口未找到，尝试查找处于“选择”状态的窗口...")
        try:
            # 尝试查找处于被点击选中状态的控制台 (Windows CMD 特性)
            win = uiauto.WindowControl(searchDepth=1, Name='选择 MUSYNX Delay', searchInterval=1)
            self._game_console_handle = win.DocumentControl(searchDepth=1, Name='Text Area', searchInterval=1)
        except Exception:
            self._logger.exception("处于“选择”状态的控制台窗口也未找到。")
            return

    # ==========================================
    # [Level 2] 局部视图渲染层 (View Render)
    # ==========================================
    def _reset_ui_state(self, event: tk.Event = None) -> None:
        """重置右侧控制面板的状态"""
        # self._get_data_button.config(state=tk.DISABLED)
        self._his_delete_button.config(state=tk.DISABLED)
        self._his_update_button.config(state=tk.DISABLED)
        self._his_name_entry.delete(0, tk.END)
        self._select_rowid = -1

    def _render_treeview(self, data_rows: list[tuple[Any, ...]]) -> None:
        """清空并重新渲染 Treeview 数据"""
        for item in self._treeview.get_children():
            self._treeview.delete(item)

        for row in data_rows:
            row_id, name, rec_time, mode, diff, combo, notes, avg_delay, avg_acc = row
            delay_str: str = f"{avg_delay:.6f}ms" if avg_delay is not None else "N/A"
            acc_str: str = f"{avg_acc:.6f}ms" if avg_acc is not None else "N/A"

            self._treeview.insert("", tk.END, values=(row_id, name, rec_time, mode, diff, combo, notes, delay_str, acc_str))

        if self._treeview.get_children():
            self._treeview.yview_moveto(1.0) # 自动滚动到底部

    def _do_matplotlib_draw(self) -> None:
        """Matplotlib 数据绘图"""
        if not self._data_list:
            return

        # 绘制当前数据的 All Hit 分析结果
        rate, data_length = AllHitAnalyze(self._data_bytes).show()

        plt.rcParams['font.family'] = ['LXGW WenKai Mono', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False

        fig = plt.figure(f'AvgDelay: {self._data_avg_delay:.4f}ms    Notes: {self._data_all_keys}    '\
            f'Combo: {self._data_combo}    AvgAcc: {self._data_avg_acc:.4f}ms',figsize=(9, 4))
        fig.clear()
        fig.subplots_adjust(**{"left":0.045,"bottom":0.055,"right":1,"top":1})
        ax = fig.add_subplot()

        self._logger.info(f'data info:\n'\
            f'\tAvgDelay: {self._data_avg_delay}\n'\
            f'\tAllKeys: {self._data_all_keys}\n'\
            f'\tAvgAcc: {self._data_avg_acc}\n'\
            f'\tCombo: {self._data_combo}')
        font: dict = {'family': 'LXGW WenKai Mono',
                      'weight': 'normal',
                      'size': 12}
        ax.text(-10,5,"Slower→", ha='left',color='#c22472',rotation=90, fontdict=font)
        ax.text(-10,-5,"←Faster", ha='left',va='top',color='#288328',rotation=90, fontdict=font)

        max_y_axis: int = max(int(max(self._data_list)), 45)
        min_y_axis: int = min(int(min(self._data_list)), -45)
        ax.set_ylim(min_y_axis - 5, max_y_axis + 5)

        # ==========================================
        # 正值部分：从外向内判断 (max_y_axis >= 阈值)
        # ==========================================
        if max_y_axis >= 250:
            ax.axhline(y=250, c='orange', ls='--', lw=1, alpha=0.8, label=f"> 250 ms    -- MISS {rate[4]:>4}")
        if max_y_axis >= 150:
            ax.axhline(y=150, c='green', ls='--', lw=1, alpha=0.8, label=f"> 150 ms    --RIGHT {rate[3]:>4}")
        if max_y_axis >= 90:
            ax.axhline(y=90, c='blue', ls='--', lw=1, alpha=0.8, label=f">  90 ms    --GREAT {rate[2]:>4}")
        if max_y_axis >= 45:
            ax.axhline(y=45, c='cyan', ls='--', lw=1, alpha=0.8, label=f">  45 ms    --EXACT {rate[1]:>4}")
        ax.axhline(y=0, c='red', ls='-', lw=1, alpha=1.0, label=f"    0 ms    -- CyEX {rate[0]:>4}")

        # ==========================================
        # 负值部分：从外向内判断 (min_y_axis <= 阈值)
        # 注意：不再重复添加 label，防止图例重复
        # ==========================================
        if min_y_axis <= -150:
            ax.axhline(y=-150, c='green', ls='--', lw=1, alpha=0.8)
        if min_y_axis <= -90:
            ax.axhline(y=-90, c='blue', ls='--', lw=1, alpha=0.8)
        if min_y_axis <= -45:
            ax.axhline(y=-45, c='cyan', ls='--', lw=1, alpha=0.8)

        # avg delay 水平线
        ax.axhline(y=self._data_avg_delay, c='red', ls='--', lw=1,
                   alpha=1, label=f"Avg Delay: {self._data_avg_delay:.2f} ms")

        ax.legend()

        ax.plot(self._data_list, marker='o', markersize=3,
                linestyle='-', color='#8a68d0', alpha=0.7, label='Hit Delay')

        for x, y in zip(range(len(self._data_list)), self._data_list, strict=True):
            if y<0:
                ax.text(x,y-3,'%dms'%y,ha='center',va='top',fontsize=7.5,alpha=0.7)
            else:
                ax.text(x,y+3,'%dms'%y,ha='center',va='bottom',fontsize=7.5,alpha=0.7)

        ax.set_xlabel("延迟量 Delay (ms)")
        ax.set_ylabel("击打频数 (Hits)")

        # 强制格式化右下角坐标系为纯整数显示 (消除科学计数法)
        ax.format_coord = lambda x, y: f"Delay: {int(y)}ms, 频数: {int(x)}"

        plt.show()

    # ==========================================
    # [Level 1] 统筹调度与事件响应层 (Controllers)
    # ==========================================
    def _action_refresh_data(self) -> None:
        """统筹事件：拉取数据 -> 重置界面状态 -> 渲染表格"""
        data = self._fetch_history_records()
        self._reset_ui_state()
        self._render_treeview(data)

    def _action_delete_record(self) -> None:
        """UI 事件：删除选中记录"""
        if self._select_rowid == -1: return
        if not messagebox.askyesno("确认删除", "确定要删除这条游玩记录吗？\n删除后不可恢复！"): return

        try:
            self._db_delete_record(self._select_rowid)
            self._logger.info(f"已删除记录 ROWID: {self._select_rowid}")
            self._action_refresh_data()
        except sqlite3.Error as e:
            self._logger.error(f"删除记录失败: {e}")
            messagebox.showerror("数据库错误", f"删除失败:\n{e}")

    def _action_change_mark(self) -> None:
        """UI 事件：修改选中记录的标记名称"""
        if self._select_rowid == -1: return
        new_mark: str = self._his_name_entry.get().strip()
        new_mode: str = self._his_mode_value.get().strip()
        new_diff: str = self._his_difficulty_value.get().strip()

        if not new_mark:
            messagebox.showwarning("警告", "请输入有效的标记名称！")
            return

        try:
            self._cursor.execute("""
                UPDATE HitDelayHistory
                SET SongMapName=?, Mode=?, Diff=?
                WHERE ROWID=?
                """, (new_mark, new_mode, new_diff, self._select_rowid))
            self._db.commit()
            self._logger.info(f"已将 ROWID {self._select_rowid} 的标记修改为: {new_mark}, {new_mode}, {new_diff}")
            self._action_refresh_data()
        except sqlite3.Error as e:
            self._logger.error(f"修改标记失败: {e}")
            messagebox.showerror("数据库错误", f"修改失败:\n{e}")

    def _action_draw_single_line(self) -> None:
        """UI 事件：解析二进制数据并绘制单曲直方图"""
        if self._select_rowid == -1: return

        # 通过ROWID获取一行数据
        row_data = self._fetch_record_by_rowid(self._select_rowid)
        if not row_data:
            messagebox.showerror("错误", "未找到选中记录的数据！")
            return

        # 将数据库中的字段值赋给全局状态变量，供绘图函数使用
        self._data_song_name = row_data['SongMapName']
        self._data_record_time = row_data['RecordTime']
        self._data_diff = row_data['Diff']
        self._data_mode = row_data["Mode"]
        self._data_combo = row_data['Combo']
        self._data_avg_delay = row_data['AvgDelay']
        self._data_all_keys = row_data['AllKeys']
        self._data_avg_acc = row_data['AvgAcc']
        self._data_bytes = row_data['HitMap']

        if not self._data_bytes:
            messagebox.showwarning("警告", "该记录的击打数据为空或已损坏，无法绘图。")
            return

        try:
            # 将二进制数据解析为整数列表，注意小端序和 int32 类型
            num_ints: int = len(self._data_bytes) // 4
            data_tuple = struct.unpack('<' + ('i' * num_ints), self._data_bytes)
            self._data_list = [x/10000 for x in data_tuple]
        except struct.error as e:
            self._logger.error(f"解析 HitMap 二进制数据失败: {e}")

        self._logger.info(f"成功载入 {len(self._data_list)} 个 note 数据准备绘图。")
        self._do_matplotlib_draw()

    def _action_get_console_data(self) -> None:
        """UI 事件：通过 UIAutomation 捕获控制台数据并写入 V4 数据库"""
        self._logger.info("尝试获取控制台数据...")

        # 1. 尝试并复制文本
        for i in range(3): # 最多尝试3次，增加成功率
             self._get_console_handle()
             if self._game_console_handle is not None:
                 break
             self._logger.warning(f"第 {i+1} 次尝试获取控制台数据失败，正在重试...")
             time.sleep(1)
        else:
            self._logger.error("多次尝试后仍未找到控制台窗口，无法获取数据。")
            messagebox.showerror("获取失败", '无法获取控制台数据，请确认后台已运行 MUSYNX Delay 控制台程序！')
            return

        self._game_console_handle.SendKeys('{Ctrl}A', waitTime=0.1)
        self._game_console_handle.SendKeys('{Ctrl}C', waitTime=0.1)

        # 2. 从剪贴板提取数据并进行数据清洗
        raw_text: str = pyperclip.paste().replace('\r', '')
        lines: list[str] = [line.strip() for line in raw_text.split('\n') if line.strip()]

        hit_delays: list[float] = []
        combo_str: str = "0/0"
        song_info: str = "0"
        sync_number: float = "0"

        for line in lines:
            if line.startswith("> Delay:"):
                # 解析延迟数据: > Delay: -12.3ms
                try:
                    val_str = line.split(':')[1].replace('ms', '').strip()
                    hit_delays.append(float(val_str))
                except (IndexError, ValueError):
                    continue
            elif line.startswith("> SongInfo"):
                # 解析 Combo 数据: > "SongInfo::SID:141801,SN:12184,MC:536,TC:536"
                try:
                    parts = line.split(',')
                    # 谱面信息 SongID(SID)
                    song_info_id = parts[0].split(':')[-1]
                    # 同步率 (SN)，转换为小数形式
                    sync_number = int(parts[1].split(':')[1]) / 100.0
                    # MaxCombo
                    mc = parts[2].split(':')[1]
                    # TotalCombo
                    tc = parts[3].split(':')[1].replace('"', '')
                    combo_str = f"{mc}/{tc}"
                except IndexError:
                    self._logger.exception("解析 SongInfo 行时发生错误，行内容: " + line)
                    pass

        all_keys: int = len(hit_delays)
        if all_keys == 0:
            messagebox.showwarning("警告", "在控制台中未提取到任何有效的击打数据 (Delay)。")
            return

        # 3. 统计计算
        avg_delay: float = sum(hit_delays) / len(hit_delays) if hit_delays else 0.0
        avg_acc: float = sum(abs(x) for x in hit_delays) / all_keys

        # 4. 适配 V4 数据库：转换为小端序 int32 二进制流
        hitmap_ints: list[int] = [int(round(x * 10000)) for x in hit_delays]
        hitmap_bytes: bytes = struct.pack('<' + ('i' * len(hitmap_ints)), *hitmap_ints)

        record_time: str = dt.now().strftime("%Y-%m-%d %H:%M:%S")

        # 使用SID查询SongName
        # 列表结构为：[SongName, Mode_Keys, Mode_Diff, Difficulty]
        song_info: list = song_name.data.get(
            song_info_id,
            ['', -1, -1, 0]
            )
        input_name: str = song_info[0]
        default_name: str = input_name if input_name else f"未命名谱面 {dt.now().strftime('%H%M%S')}"
        mode: str = self._const_keys_mode.get(song_info[1], "ERR") + self._const_diff_mode[song_info[2]]
        diff:int = song_info[3]

        # 5. 写入数据库并自动刷新 UI
        try:
            self._cursor.execute("""
                INSERT INTO HitDelayHistory
                (SongMapName, RecordTime, Mode, Diff, Combo, AllKeys, AvgDelay, AvgAcc, HitMap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (default_name, record_time, mode, diff, combo_str, all_keys, avg_delay, avg_acc, hitmap_bytes))
            self._db.commit()

            new_rowid = self._cursor.lastrowid
            self._logger.info(f"成功导入来自控制台的数据，生成新记录 ROWID: {new_rowid}")

            # 刷新表格
            self._action_refresh_data()

        except sqlite3.Error as e:
            self._logger.error(f"将捕获数据写入数据库时失败: {e}")
            messagebox.showerror("数据库错误", f"保存捕获数据失败:\n{e}")

        # 6. 追加写入Acc-Sync.csv文件
        try:
            with open("./musync_data/Acc-Sync.csv", "a", encoding="utf-8") as f:
                f.write(f"{avg_acc:.4f},{sync_number:.2f},{diff}\n")
            self._logger.info("已将数据追加写入 Acc-Sync.csv 文件。")
        except Exception as e:
            self._logger.error(f"写入 Acc-Sync.csv 文件失败: {e}")

        # 7. 清理剪贴板，防止泄露敏感数据
        pyperclip.copy("")

        # 8. 自动选中并加载新捕获的数据进行绘图
        self._select_rowid = new_rowid
        self._action_draw_single_line()

    def _action_show_all_hit(self) -> None:
        """UI 事件：显示全局全量直方图 (调用外部模块)"""
        try:
            AllHitAnalyze().show()
        except Exception as e:
            self._logger.error(f"显示汇总图表失败: {e}")

    # ==========================================
    # [Level 0] 无状态 UI 独立交互 (Stateless UI callbacks)
    # ==========================================

    # def _on_treeview_resize(self, event: tk.Event) -> None:
    #     """当 Treeview 大小改变时，按比例调整列宽"""
    #     new_total_width = event.width
    #     if new_total_width <= 100: return # 忽略初始化时的极小值

    #     # 计算拉伸比例系数
    #     # 减去 20px 预留给滚动条的空间，防止出现水平滚动条
    #     scale_factor = (new_total_width - 20) / self._total_base_width

    #     for col_id, title, base_width, anchor in self._headings:
    #         # 核心算法：目标宽度 = 基准宽度 * 比例系数
    #         target_width = int(base_width * scale_factor)
    #         # 设置最小宽度防止缩没，并更新当前宽度
    #         self._treeview.column(col_id, width=target_width, minwidth=int(base_width*0.5))

    def _on_tree_select(self, event: tk.Event) -> None:
        """回调：点击表格行获取 ROWID 并更新右侧面板输入框"""
        selected_items: tuple[str, ...] = self._treeview.selection()
        if not selected_items: return

        values: tuple[Any, ...] = self._treeview.item(selected_items[0], "values")
        if values:
            self._select_rowid = int(values[0])
            self._his_name_entry.delete(0, tk.END)
            self._his_name_entry.insert(0, str(values[1]))
            self._his_record_time_value["text"] = str(values[2])
            self._his_mode_value.set(str(values[3]))
            self._his_difficulty_value.set(str(values[4]))
            self._his_combo_value["text"] = str(values[5])
            self._his_notes_value["text"] = str(values[6])
            self._his_delay_value["text"] = str(values[7])
            self._his_acc_value["text"] = str(values[8])

            # 激活对应的操作按钮
            self._his_delete_button.config(state=tk.NORMAL)
            self._his_update_button.config(state=tk.NORMAL)

    def _on_tree_double_click(self, event: tk.Event) -> None:
        """回调：双击表格行快捷绘制单曲分析图表"""
        # 极客技巧：防误触检测。判断双击的坐标是否在有效的数据行上，防止双击表头触发崩溃
        item_id: str = self._treeview.identify('item', event.x, event.y)
        if not item_id:
            return

        # 强制将选中的行设为当前双击的行 (防止双击过快导致 <<TreeviewSelect>> 未触发)
        self._treeview.selection_set(item_id)
        self._on_tree_select(event)

        # 直接调度控制层的绘图事件
        self._action_draw_single_line()

    # TODO: 疑似异常, 未能实现排序功能
    def _sort_treeview(self, col: str, reverse: bool) -> None:
        """回调：点击表头进行双向排序"""
        try:
            items: list[tuple[str, str]] = [(str(self._treeview.set(k, col)), k) for k in self._treeview.get_children('')]

            # 如果带有 'ms' 则尝试转换为 float 进行数值排序
            try:
                items.sort(key=lambda t: float(t[0].replace('ms', '')), reverse=reverse)
            except ValueError:
                items.sort(reverse=reverse)

            for index, (val, k) in enumerate(items):
                self._treeview.move(k, '', index)

            # 翻转下次点击的排序方向
            self._treeview.heading(col, command=lambda: self._sort_treeview(col, not reverse))
        except Exception as e:
            self._logger.warning(f"表格排序失败: {e}")

    def _on_closing(self) -> None:
        """UI 事件：窗口关闭时清理资源"""
        if messagebox.askokcancel("退出", "确定要退出高精度延迟分析吗？"):
            try:
                self._cursor.close()
                self._db.close()
            except Exception as e:
                self._logger.warning(f"关闭数据库连接时发生异常: {e}")
            self._subroot.destroy()

if __name__ == "__main__":
    from . import version, pre_version, is_pre_release

    # Init
    config.Version = pre_version.replace("pre",".") if (is_pre_release) else version

    # Launcher
    root: tk.Tk = tk.Tk()
    root.tk.call('tk', 'scaling', 1.25)
    HitDelay(root)
    root.update()
    root.mainloop()
