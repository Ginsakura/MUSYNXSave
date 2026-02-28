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

from matplotlib import axes, pyplot as plt, gridspec, figure
from matplotlib.ticker import MultipleLocator
from tkinter import ttk, messagebox
from typing import Any, Literal

# 外部数据分析模块导入
from . import acc_sync_diff_analyze, AllHitAnalyze, Logger, Config

uiauto.SetGlobalSearchTimeout(1)

class HitDelay:
    """游玩延迟与历史记录可视化分析主界面"""

    def __init__(self, subroot: tk.Tk | tk.Toplevel) -> None:
        self._logger: logging.Logger = Logger.GetLogger("HitDelay.HitDelayText")

        db_path: str = './musync_data/HitDelayHistory.db'
        if not os.path.isfile(db_path):
            self._logger.fatal("Database Not Exists!")
            messagebox.showerror("Error", '发生错误: HitDelayHistory.db 数据库文件不存在!')
            return

        self._db: sqlite3.Connection = sqlite3.connect(db_path)
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

        # 全局状态容器
        self._data_list: list[int] = []
        self._select_rowid: int = -1
        self._game_console_handle: uiauto.DocumentControl | None = None;

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
            ("record_time", "记录时间", 160, tk.W),
            ("mode", "模式", 60, tk.CENTER),
            ("diff", "难度", 60, tk.CENTER),
            ("combo", "Combo", 80, tk.E),
            ("notes", "Notes", 60, tk.E),
            ("avg_delay", "平均延迟", 80, tk.E),
            ("avg_acc", "平均准度", 80, tk.E)
        ]

        for col_id, title, width, anchor in headings:
            self._treeview.heading(col_id, anchor=tk.CENTER, text=title)
            self._treeview.column(col_id, anchor=anchor, width=width)

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
        history_record_time_value: tk.Label = tk.Label(
            info_modify_frame,
            text="",
            font=self._font,
            relief="groove")
        history_record_time_value.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew')
        info_modify_row += 1

        # 行4: 游玩模式显示
        history_mode_label: tk.Label = tk.Label(
            info_modify_frame,
            text='模式: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_mode_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_mode_value: ttk.Combobox = ttk.Combobox(
            info_modify_frame,
            values=['', '4KEZ', '4KHD', '4KIN', "6KEZ", "6KHD", "6KIN"],
            font=self._font)
        history_mode_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行5: 游玩难度显示
        history_difficulty_label: tk.Label = tk.Label(
            info_modify_frame,
            text='难度: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_difficulty_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_difficulty_value: ttk.Combobox = ttk.Combobox(
            info_modify_frame,
            values=[f"{i}" for i in range(1, 16)],
            font=self._font)
        history_difficulty_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行6: Combo显示
        history_combo_label: tk.Label = tk.Label(
            info_modify_frame,
            text='Combo: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_combo_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_combo_value: tk.Label = tk.Label(
            info_modify_frame,
            text="0/0    ",
            font=self._font,
            relief="groove",
            anchor='e')
        history_combo_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行7: Notes数量显示
        history_keys_label: tk.Label = tk.Label(
            info_modify_frame,
            text='按键数量: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_keys_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_keys_value: tk.Label = tk.Label(
            info_modify_frame,
            text="0    ",
            font=self._font,
            relief="groove",
            anchor='e')
        history_keys_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行8: Avg Delay显示
        history_delay_label: tk.Label = tk.Label(
            info_modify_frame,
            text='平均延迟: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_delay_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_delay_value: tk.Label = tk.Label(
            info_modify_frame,
            text="000.000000ms  ",
            font=self._font,
            relief="groove",
            anchor='e')
        history_delay_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行9: Avg Acc显示
        history_acc_label: tk.Label = tk.Label(
            info_modify_frame,
            text='AvgAcc: ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_acc_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_acc_value: tk.Label = tk.Label(
            info_modify_frame,
            text='000.000000ms  ',
            font=self._font,
            relief="groove",
            anchor='e')
        history_acc_value.grid(row=info_modify_row, column=1, sticky='ew')
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
    def _fetch_history_records(self) -> list[tuple[Any, ...]]:
        """[纯函数] 仅负责从 V4 数据库获取全部历史记录"""
        try:
            self._cursor.execute("SELECT ROWID, SongMapName, RecordTime, Mode, Diff, Combo, AllKeys, AvgDelay, AvgAcc FROM HitDelayHistory")
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            self._logger.error(f"查询历史记录失败: {e}")
            return []

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
    def _reset_ui_state(self) -> None:
        """重置右侧控制面板的状态"""
        self._get_data_button.config(state=tk.DISABLED)
        self._history_delete_button.config(state=tk.DISABLED)
        self._history_update_button.config(state=tk.DISABLED)
        self._his_name_entry.delete(0, tk.END)
        self._select_rowid = -1

    def _render_treeview(self, data_rows: list[tuple[Any, ...]]) -> None:
        """清空并重新渲染 Treeview 数据"""
        for item in self._treeview.get_children():
            self._treeview.delete(item)

        for row in data_rows:
            row_id, name, rec_time, mode, diff, combo, notes, avg_delay, acc = row
            delay_str: str = f"{avg_delay:.2f}ms" if avg_delay is not None else "N/A"
            acc_str: str = f"{acc:.2f}ms" if acc is not None else "N/A"

            self._treeview.insert("", tk.END, values=(row_id, name, rec_time, mode, diff, combo, notes, delay_str, acc_str))

        if self._treeview.get_children():
            self._treeview.yview_moveto(1.0) # 自动滚动到底部

    def _do_matplotlib_draw(self) -> None:
        """[核心重构] 极简且稳健的 Matplotlib 数据绘图"""
        if not self._data_list:
            return

        plt.rcParams['font.family'] = ['LXGW WenKai Mono', 'SimHei', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.canvas.manager.set_window_title(f"单曲击打分析 - 记录ID: {self._select_rowid}")

        # 使用 matplotlib 原生 hist 进行高效率分桶，摒弃极易越界的 manual counting
        min_val, max_val = int(min(self._data_list)), int(max(self._data_list))
        bins = range(min_val - 1, max_val + 2)

        ax.hist(self._data_list, bins=bins, color='#32a9c7', edgecolor='black', alpha=0.8, linewidth=0.5)

        ax.set_title(f"击打延迟分布 (总计: {len(self._data_list)} notes)", fontsize=14)
        ax.set_xlabel("延迟量 Delay (ms)")
        ax.set_ylabel("击打频数 (Hits)")

        # 绘制 0ms 完美基准线
        ax.axvline(x=0, color='red', linestyle='--', linewidth=1.5, alpha=0.8, label='0ms 完美基准线')
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)

        # 强制格式化右下角坐标系为纯整数显示 (消除科学计数法)
        ax.format_coord = lambda x, y: f"Delay: {int(x)}ms, 频数: {int(y)}"

        plt.tight_layout()
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
        new_mark: str = self._his_name_entry.get().strip()
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
        messagebox.showinfo("提示", "功能占位：此部分逻辑即将被 UDP 通信模块重构替换。")

    def _action_show_all_hit(self) -> None:
        """UI 事件：显示全局全量直方图 (调用外部模块)"""
        try:
            AllHitAnalyze().show()
        except Exception as e:
            self._logger.error(f"显示汇总图表失败: {e}")

    # ==========================================
    # [Level 0] 无状态 UI 独立交互 (Stateless UI callbacks)
    # ==========================================
    def _on_tree_select(self, event: tk.Event) -> None:
        """回调：点击表格行获取 ROWID 并更新右侧面板输入框"""
        selected_items: tuple[str, ...] = self._treeview.selection()
        if not selected_items: return

        values: tuple[Any, ...] = self._treeview.item(selected_items[0], "values")
        if values:
            self._select_rowid = int(values[0])
            self._his_name_entry.delete(0, tk.END)
            self._his_name_entry.insert(0, str(values[1]))

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

if __name__ == "__main__":
    from . import version, pre_version, is_pre_release

    # Init
    Config().Version = pre_version.replace("pre",".") if (is_pre_release) else version

    # Launcher
    root: tk.Tk = tk.Tk()
    root.tk.call('tk', 'scaling', 1.25)
    HitDelay(root)
    root.update()
    root.mainloop()
