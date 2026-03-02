# -*- coding: utf-8 -*-
import logging
import matplotlib as mpl
import os
import pyperclip
import struct
import sqlite3
import time
import tkinter as tk
import uiautomation as uiauto

from datetime import datetime as dt
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator
from tkinter import ttk, messagebox
from typing import Any, Literal


# 外部数据分析模块导入
from . import acc_sync_diff_analyze, AllHitAnalyze, Logger, Config, Toolkit

uiauto.SetGlobalSearchTimeout(1)

class HitDelay:
    """游玩延迟与历史记录可视化分析主界面"""
    _DB_PATH: str = './musync_data/HitDelayHistory.db'
    _db: sqlite3.Connection = sqlite3.connect(_DB_PATH)
    _cursor: sqlite3.Cursor = _db.cursor()
    _font: tuple[str, int] = ('霞鹜文楷等宽', 16)
    _mode_list: list[str] = ['', '4KEZ', '4KHD', '4KIN', "6KEZ", "6KHD", "6KIN"]
    _heading_list: list[str] = []

    # 全局状态容器
    _data_list: list[int] = []
    _select_rowid: int = -1
    _game_console_handle: uiauto.DocumentControl | None = None

    def __init__(self, root: tk.Tk | tk.Toplevel) -> None:
        self._logger: logging.Logger = Logger.GetLogger("HitDelay")

        if not os.path.isfile(self._DB_PATH):
            self._logger.fatal("Database Not Exists!")
            messagebox.showerror("Error", '发生错误: HitDelayHistory.db 数据库文件不存在!')
            return

        self._root: tk.Tk | tk.Toplevel = root

        try:
            self._root.iconbitmap('./musync_data/Musync.ico')
        except Exception:
            self._logger.warning("Musync.ico 未找到，使用默认图标")

        # 修改组件样式
        self._root.geometry('1200x600+300+300')
        self._root.title("高精度延迟分析")
        self._root['background'] = '#efefef'

        self._style: ttk.Style = ttk.Style()
        self._style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',13))
        self._style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',15))
        self._style.configure("TButton", font=self._font, relief="raised")
        self._style.configure("update.TButton", font=self._font, relief="raised",background='#A6E22B')
        self._style.configure("delete.TButton", font=self._font, relief="raised", foreground='#FF4040', background='#FF2020')
        
        self._root.option_add('*TCombobox*Listbox.font', self._font)

        # TODO: 绑定全局按键
        self._root.bind('<F5>', self._on_refresh_data)
        self._root.bind('<Control-Escape>', self._on_closing)
        self._root.bind("<Control-r>", self._on_reset_ui_state)
        self._root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # MVC 架构流转：初始化视图 -> 加载数据 -> 渲染数据
        self._init_ui()
        self._action_refresh_data()

        # 初始化 Matplotlib 图表窗口
        self._line_chart_window: tk.Toplevel = tk.Toplevel(self._root)
        mpl.rcParams['font.family'] = ['LXGW WenKai Mono', 'sans-serif']
        mpl.rcParams['axes.unicode_minus'] = False
        self._fig_line = Figure(figsize=(9, 4))
        self._fig_line.subplots_adjust(left=0.045, bottom=0.055, right=1.0, top=1.0)
        self._axis = self._fig_line.add_subplot(111)
        self._fig_canvas = FigureCanvasTkAgg(self._fig_line, master=self._line_chart_window)
        self._fig_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # ==========================================
    # [Level 0] 视图初始化与布局层 (View / UI)
    # ==========================================
    def _init_ui(self) -> None:
        """初始化动态流式 UI 布局 (嵌套 Grid 架构)"""
        # 1. 主容器 (左右分割)
        main_frame: tk.Frame = tk.Frame(self._root, bg='#efefef')
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
            ("record_time", "记录时间", 170, tk.W),
            ("mode", "模式", 50, tk.CENTER),
            ("diff", "难度", 45, tk.CENTER),
            ("combo", "Combo", 80, tk.E),
            ("notes", "Notes", 60, tk.E),
            ("avg_delay", "平均延迟", 100, tk.E),
            ("avg_acc", "平均准度", 100, tk.E)
        ]

        for col_id, title, width, anchor in headings:
            self._heading_list.append(col_id)
            self._treeview.heading(col_id, anchor=tk.CENTER, text=title)
            self._treeview.column(col_id, anchor=anchor, width=width)
            # 如果是曲名或时间，允许拉伸；其他列固定宽度
            is_stretch = col_id == "song_name"
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
            command=acc_sync_diff_analyze.analyze_3d)
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
        self._history_name_entry = tk.Entry(info_modify_frame, font=self._font, relief="sunken")
        self._history_name_entry.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew')
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
        self._history_record_time_value: tk.Label = tk.Label(
            info_modify_frame,
            text="",
            font=self._font,
            relief="groove")
        self._history_record_time_value.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew')
        info_modify_row += 1

        # 行4: 游玩模式显示
        history_mode_label: tk.Label = tk.Label(
            info_modify_frame,
            text='模式: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_mode_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._history_mode_value: ttk.Combobox = ttk.Combobox(
            info_modify_frame,
            values=self._mode_list,
            font=self._font)
        self._history_mode_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行5: 游玩难度显示
        history_difficulty_label: tk.Label = tk.Label(
            info_modify_frame,
            text='难度: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_difficulty_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._history_difficulty_value: ttk.Combobox = ttk.Combobox(
            info_modify_frame,
            values=[f"{i}" for i in range(1, 16)],
            font=self._font)
        self._history_difficulty_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行6: Combo显示
        history_combo_label: tk.Label = tk.Label(
            info_modify_frame,
            text='Combo: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_combo_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._history_combo_value: tk.Label = tk.Label(
            info_modify_frame,
            text="0/0    ",
            font=self._font,
            relief="groove",
            anchor='e')
        self._history_combo_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行7: Notes数量显示
        history_notes_label: tk.Label = tk.Label(
            info_modify_frame,
            text='按键数量: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_notes_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._history_notes_value: tk.Label = tk.Label(
            info_modify_frame,
            text="0    ",
            font=self._font,
            relief="groove",
            anchor='e')
        self._history_notes_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行8: Avg Delay显示
        history_delay_label: tk.Label = tk.Label(
            info_modify_frame,
            text='平均延迟: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_delay_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._history_delay_value: tk.Label = tk.Label(
            info_modify_frame,
            text="000.000000ms  ",
            font=self._font,
            relief="groove",
            anchor='e')
        self._history_delay_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行9: Avg Acc显示
        history_acc_label: tk.Label = tk.Label(
            info_modify_frame,
            text='AvgAcc: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_acc_label.grid(row=info_modify_row, column=0, sticky='ew')
        self._history_acc_value: tk.Label = tk.Label(
            info_modify_frame,
            text='000.000000ms  ',
            font=self._font,
            relief="groove",
            anchor='e')
        self._history_acc_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行10: 操作按钮
        self._history_update_button: ttk.Button = ttk.Button(
            info_modify_frame,
            text='更新记录',
            style="update.TButton",
            command=self._action_change_mark)
        self._history_update_button.grid(row=info_modify_row, column=0, sticky='ew')

        self._history_delete_button: ttk.Button = ttk.Button(
            info_modify_frame,
            text='删除记录',
            style="delete.TButton",
            command=self._action_delete_record)
        self._history_delete_button.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        for i in range(info_modify_row):
            info_modify_frame.rowconfigure(i, weight=1, uniform="info_grid")


    # ==========================================
    # [Level 2] 数据访问与解析层 (Model / DAL)
    # ==========================================
    def _fetch_history_records(self, rowid: str = "") -> list[tuple[Any, ...]]:
        """[纯函数] 仅负责从 V4 数据库获取全部历史记录"""
        try:
            query = "SELECT ROWID, SongMapName, RecordTime, Mode, Diff, Combo, AllKeys, AvgDelay, AvgAcc FROM HitDelayHistory"
            if rowid:
                query += f" WHERE ROWID=?"
            self._cursor.execute(query, (rowid,) if rowid else ())
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            self._logger.error(f"查询历史记录失败: {e}")
            return []
        
    def _fetch_all_history_records(self) -> list[tuple[Any, ...]]:
        return self._fetch_history_records()

    def _parse_hitmap(self, rowid: int) -> list[int]:
        """[纯函数] 负责从 V4 数据库读取 BLOB 并反序列化为小端整数列表"""
        try:
            self._cursor.execute("SELECT HitMap FROM HitDelayHistory WHERE ROWID=?", (rowid,))
            result = self._cursor.fetchone()
            if not result or not result[0]:
                return []

            hitmap_blob: bytes = result[0]
            num_ints: int = len(hitmap_blob) // 4
            ints_tuple: tuple[int, ...] = struct.unpack('<' + ('i' * num_ints), hitmap_blob)
            return list(ints_tuple)
        except (sqlite3.Error, struct.error) as e:
            self._logger.error(f"解析 HitMap 二进制数据失败: {e}")
            return []

    def _get_console_handle(self) -> bool:
        try:
            # 尝试查找常规状态下的控制台
            win = uiauto.WindowControl(searchDepth=1, Name='MUSYNX Delay', searchInterval=1)
            self._game_console_handle = win.DocumentControl(searchDepth=1, Name='Text Area', searchInterval=1)
            return True
        except Exception:
            self._logger.warning("常规控制台窗口未找到，尝试查找处于“选择”状态的窗口...")
        try:
            # 尝试查找处于被点击选中状态的控制台 (Windows CMD 特性)
            win = uiauto.WindowControl(searchDepth=1, Name='选择 MUSYNX Delay', searchInterval=1)
            self._game_console_handle = win.DocumentControl(searchDepth=1, Name='Text Area', searchInterval=1)
        except Exception:
            self._logger.exception("处于“选择”状态的控制台窗口也未找到。")
            return False
        return True

    # ==========================================
    # [Level 2] 局部视图渲染层 (View Render)
    # ==========================================
    def _reset_ui_state(self, event: tk.Event) -> None:
        """重置右侧控制面板的状态"""
        self._get_data_button.config(state=tk.DISABLED)
        self._history_delete_button.config(state=tk.DISABLED)
        self._history_update_button.config(state=tk.DISABLED)
        self._history_name_entry.delete(0, tk.END)
        self._select_rowid = -1

    def _render_treeview(self, data_rows: list[tuple[Any, ...]]) -> None:
        """清空并重新渲染 Treeview 数据"""
        for item in self._treeview.get_children():
            self._treeview.delete(item)

        for row in data_rows:
            row_id, name, rec_time, mode, diff, combo, notes, avg_delay, avg_acc = row
            rec_time = rec_time.split('.')[0]
            delay_str: str = f"{avg_delay:.4f}ms" if avg_delay is not None else "N/A"
            acc_str: str = f"{avg_acc:.4f}ms" if avg_acc is not None else "N/A"

            self._treeview.insert("", tk.END, values=(row_id, name, rec_time, mode, diff, combo, notes, delay_str, acc_str))

        if self._treeview.get_children():
            self._treeview.yview_moveto(1.0) # 自动滚动到底部

    def _do_matplotlib_draw(self) -> None:
        """Matplotlib 数据绘图"""
        if not self._data_list:
            return
        
        font: dict = {'family': 'LXGW WenKai Mono', 'weight': 'normal', 'size': 12}

        # 绘制当前数据的 All Hit 分析结果
        rate, data_length = AllHitAnalyze(self._root, self._data_list).show()
        
        self._line_chart_window.title(f'AvgDelay: {self._selected_row_data["avg_delay"]:.4f}ms    Notes: {self._selected_row_data["notes"]}    '\
            f'Combo: {self._selected_row_data["combo"]}    AvgAcc: {self._selected_row_data["avg_acc"]:.4f}ms')
        self._logger.info(f'data info:\n'\
            f'\tAvgDelay: {self._selected_row_data["avg_delay"]}\n'\
            f'\tNotes: {self._selected_row_data["notes"]}\n'\
            f'\tAvgAcc: {self._selected_row_data["avg_acc"]}')
        
        self._fig_line.clear()

        self._axis.text(-10,5,"Slower→", ha='left',color='#c22472',rotation=90, fontdict=font)
        self._axis.text(-10,-5,"←Faster", ha='left',va='top',color='#288328',rotation=90, fontdict=font)

        max_y_axis: int = max(int(max(self._data_list)), 45)
        min_y_axis: int = min(int(min(self._data_list)), -45)

        self._axis.set_ylim(min_y_axis - 5, max_y_axis + 5)
        self._axis.set_xlim(-15, data_length * 1.02)

        # ==========================================
        # 正值部分：从外向内判断 (max_y_axis >= 阈值)
        # ==========================================
        if max_y_axis >= 250:
            self._axis.axhline(y=250, c='orange', ls='--', lw=1, alpha=0.8, label=f"> 250 ms    -- MISS {rate[4]:>4}")
        if max_y_axis >= 150:
            self._axis.axhline(y=150, c='green', ls='--', lw=1, alpha=0.8, label=f"> 150 ms    --RIGHT {rate[3]:>4}")
        if max_y_axis >= 90:
            self._axis.axhline(y=90, c='blue', ls='--', lw=1, alpha=0.8, label=f">  90 ms    --GREAT {rate[2]:>4}")
        if max_y_axis >= 45:
            self._axis.axhline(y=45, c='cyan', ls='--', lw=1, alpha=0.8, label=f">  45 ms    --EXACT {rate[1]:>4}")
        self._axis.axhline(y=0, c='red', ls='-', lw=1, alpha=1.0, label=f"   0 ms    -- CyEX  {rate[0]:>4}")

        # ==========================================
        # 负值部分：从外向内判断 (min_y_axis <= 阈值)
        # 注意：不再重复添加 label，防止图例重复
        # ==========================================
        if min_y_axis <= -150:
            self._axis.axhline(y=-150, c='green', ls='--', lw=1, alpha=0.8)
        if min_y_axis <= -90:
            self._axis.axhline(y=-90, c='blue', ls='--', lw=1, alpha=0.8)
        if min_y_axis <= -45:
            self._axis.axhline(y=-45, c='cyan', ls='--', lw=1, alpha=0.8)

        self._axis.legend()

        # TODO: 图表绘制

        self._axis.set_xlabel("延迟量 Delay (ms)")
        self._axis.set_ylabel("击打频数 (Hits)")

        # 强制格式化右下角坐标系为纯整数显示 (消除科学计数法)
        self._axis.format_coord = lambda x, y: f"Delay: {y:.1f}ms, 频数: {int(x)}"
        
        self._fig_canvas.draw()

    # ==========================================
    # [Level 1] 统筹调度与事件响应层 (Controllers)
    # ==========================================
    def _action_refresh_data(self) -> None:
        """统筹事件：拉取数据 -> 重置界面状态 -> 渲染表格"""
        data = self._fetch_all_history_records()
        self._reset_ui_state()
        self._render_treeview(data)

    def _action_delete_record(self) -> None:
        """UI 事件：删除选中记录"""
        if self._select_rowid == -1: return
        if not messagebox.askyesno("确认删除", "确定要删除这条游玩记录吗？\n删除后不可恢复！"): return

        try:
            self._cursor.execute("DELETE FROM HitDelayHistory WHERE ROWID=?", (self._select_rowid,))
            self._db.commit()
            self._logger.info(f"已删除记录 ROWID: {self._select_rowid}")
            self._action_refresh_data()
        except sqlite3.Error as e:
            self._logger.error(f"删除记录失败: {e}")
            messagebox.showerror("数据库错误", f"删除失败:\n{e}")

    def _action_change_mark(self) -> None:
        """UI 事件：修改选中记录的标记名称"""
        if self._select_rowid == -1: return
        new_mark: str = self._history_name_entry.get().strip()
        if not new_mark:
            messagebox.showwarning("警告", "请输入有效的标记名称！")
            return

        try:
            self._cursor.execute("UPDATE HitDelayHistory SET SongMapName=? WHERE ROWID=?", (new_mark, self._select_rowid))
            self._db.commit()
            self._logger.info(f"已将 ROWID {self._select_rowid} 的标记修改为: {new_mark}")
            self._action_refresh_data()
        except sqlite3.Error as e:
            self._logger.error(f"修改标记失败: {e}")
            messagebox.showerror("数据库错误", f"修改失败:\n{e}")

    def _action_draw_single_line(self) -> None:
        """UI 事件：解析二进制数据并绘制单曲直方图"""
        if self._select_rowid == -1: return

        self._data_list = self._parse_hitmap(self._select_rowid)
        if not self._data_list:
            messagebox.showwarning("警告", "该记录的击打数据为空或已损坏，无法绘图。")
            return

        self._logger.info(f"成功载入 {len(self._data_list)} 个 note 数据准备绘图。")
        self._do_matplotlib_draw()

    def _action_get_console_data(self) -> None:
        """UI 事件：通过 UIAutomation 捕获控制台数据并写入 V4 数据库"""
        self._logger.info("尝试获取控制台数据...")
        start_time: int = time.perf_counter_ns()

        # 1. 尝试并复制文本
        for i in range(3): # 最多尝试3次，增加成功率
            self._get_data_button.config(
                state=(
                    tk.NORMAL if self._get_console_handle() else tk.DISABLED
                    )
                )
            if self._game_console_handle is not None:
                break
            self._logger.warning(f"第 {i+1} 次尝试获取控制台数据失败，正在重试...")
            time.sleep(0.5)
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

        for line in lines:
            if line.startswith("> SongInfo"):
                # 解析 Combo 数据: > "SongInfo::SID:141801,SN:12184,MC:536,TC:536"
                try:
                    parts = line.split(',')
                    mc = parts[2].split(':')[1]
                    tc = parts[3].split(':')[1].replace('"', '')
                    combo_str = f"{mc}/{tc}"
                except IndexError:
                    pass
            elif line.startswith("> Delay:"):
                # 解析延迟数据: > Delay: -12.3ms
                try:
                    val_str = line.split(':')[1].replace('ms', '').strip()
                    hit_delays.append(float(val_str))
                except (IndexError, ValueError):
                    continue

        all_keys: int = len(hit_delays)
        if all_keys == 0:
            messagebox.showwarning("警告", "在控制台中未提取到任何有效的击打数据 (Delay)。")
            return

        # 3. 统计计算 (过滤极端的 Miss 延迟以计算平均偏差)
        delay_interval: int = 150 # 定义有效判定区间，规避极端数值影响平均值
        valid_delays = [x for x in hit_delays if -delay_interval < x < delay_interval]

        avg_delay: float = sum(valid_delays) / len(valid_delays) if valid_delays else 0.0
        avg_acc: float = sum(abs(x) for x in hit_delays) / all_keys

        # 4. 适配 V4 数据库：转换为小端序 int32 二进制流
        hitmap_ints: list[int] = [int(x) for x in hit_delays]
        hitmap_bytes: bytes = struct.pack('<' + ('i' * len(hitmap_ints)), *hitmap_ints)

        record_time: str = dt.now().strftime("%Y-%m-%d %H:%M:%S")

        # 智能获取命名：优先使用界面输入框内的文本，为空则填充默认名
        input_name = self._history_name_entry.get().strip().replace("\'", "’")
        default_name: str = input_name if input_name else "新导入记录"

        # 5. 写入数据库并自动刷新 UI
        try:
            self._cursor.execute("""
                INSERT INTO HitDelayHistory
                (SongMapName, RecordTime, Mode, Diff, Combo, AllKeys, AvgDelay, AvgAcc, HitMap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (default_name, record_time, "4K", 0, combo_str, all_keys, avg_delay, avg_acc, hitmap_bytes))
            self._db.commit()

            new_rowid: int | None = self._cursor.lastrowid
            if new_rowid is None:
                new_rowid = len(self._treeview.get_children()) + 1
            self._logger.info(f"成功导入来自控制台的数据，生成新记录 ROWID: {new_rowid}")

            # 刷新表格
            self._action_refresh_data()

            # 自动选中并加载新捕获的数据进行绘图
            self._select_rowid = new_rowid
            self._data_list = hitmap_ints
            self._do_matplotlib_draw()

        except sqlite3.Error as e:
            self._logger.error(f"将捕获数据写入数据库时失败: {e}")
            messagebox.showerror("数据库错误", f"保存捕获数据失败:\n{e}")
        self._logger.debug(f"_action_get_console_data() Run Time: {Toolkit.calc_end_time(start_time):.3f} ms")

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

    def on_closing(self) -> None:
        """UI 事件：窗口关闭时清理资源"""
        if messagebox.askokcancel("退出", "确定要退出高精度延迟分析吗？"):
            try:
                self._cursor.close()
                self._db.close()
            except Exception as e:
                self._logger.warning(f"关闭数据库连接时发生异常: {e}")
            self._root.destroy()

    def _on_tree_select(self, event: tk.Event) -> None:
        """回调：点击表格行获取 ROWID 并更新右侧面板输入框"""
        selected_items: tuple[str, ...] = self._treeview.selection()
        if not selected_items: return

        rowid: str = self._treeview.item(selected_items[0], "values")[0]
        data: tuple[Any, ...] = self._fetch_history_records(rowid)[0]

        if data:
            pass
            self._select_rowid = data[0]
            # 将选中行的数据和数据标题添加为字典
            self._selected_row_data = dict(zip(self._heading_list, data))
            print(self._selected_row_data)

            self._history_name_entry.delete(0, tk.END)
            self._history_name_entry.insert(0, data[1])
            self._history_record_time_value.config(text=data[2])
            self._history_mode_value.current(self._mode_list.index(data[3]))
            self._history_difficulty_value.current(data[4])
            self._history_combo_value.config(text=f"{data[5]}    ")
            self._history_notes_value.config(text=f"{data[6]}    ")
            self._history_delay_value.config(text=f"{data[7]:.6f}ms  ")
            self._history_acc_value.config(text=f"{data[8]:.6f}ms  ")

            # 激活对应的操作按钮
            self._history_delete_button.config(state=tk.NORMAL)
            self._history_update_button.config(state=tk.NORMAL)

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

    def _on_closing(self, event: tk.Event) -> None:
        self.on_closing()

    def _on_refresh_data(self, event: tk.Event) -> None:
        """快捷键事件: F5 刷新数据"""
        self._action_refresh_data()

    def _on_reset_ui_state(self, event: tk.Event) -> None:
        """快捷键事件: Esc 重置 UI 状态"""
        self._reset_ui_state(event)
