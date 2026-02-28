# -*- coding: utf-8 -*-
import logging
import os
import pyperclip
import struct
import sqlite3
import tkinter as tk
import uiautomation as uiauto

from matplotlib import axes, pyplot as plt, gridspec, figure
from matplotlib.ticker import MultipleLocator
from tkinter import ttk, messagebox
from typing import Any, Literal

# 外部数据分析模块导入
from . import acc_sync_diff_analyze, AllHitAnalyze, Logger

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

        self.db: sqlite3.Connection = sqlite3.connect(db_path)
        self.cur: sqlite3.Cursor = self.db.cursor()

        self.subroot: tk.Tk | tk.Toplevel = subroot
        self.font: tuple[str, int] = ('霞鹜文楷等宽', 16)

        try:
            self.subroot.iconbitmap('./musync_data/Musync.ico')
        except Exception:
            self._logger.warning("Musync.ico 未找到，使用默认图标")

        self.subroot.geometry('1200x600+300+300')
        self.subroot.title("高精度延迟分析")
        self.subroot['background'] = '#efefef'

        self.style: ttk.Style = ttk.Style()
        self.style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',13))
        self.style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',15))

        # 全局状态容器
        self.data_list: list[int] = []
        self.select_rowid: int = -1

        # MVC 架构流转：初始化视图 -> 加载数据 -> 渲染数据
        self._init_ui()
        self._action_refresh_data()

    # ==========================================
    # [Level 0] 视图初始化与布局层 (View / UI)
    # ==========================================
    def _init_ui(self) -> None:
        """初始化动态流式 UI 布局 (嵌套 Grid 架构)"""
        # 1. 主容器 (左右分割)
        main_frame: tk.Frame = tk.Frame(self.subroot, bg='#efefef')
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
        self.tree: ttk.Treeview = ttk.Treeview(data_frame, show="headings",
                                               columns=columns, selectmode='browse')

        headings: list[tuple[str, str, int, Literal['w', 'center', 'e']]] = [
            ("rowid", "ID", 40, tk.W),
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
            self.tree.heading(col_id, anchor=tk.CENTER, text=title)
            self.tree.column(col_id, anchor=anchor, width=width)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._on_tree_double_click)

        # 滚动条绑定
        self.bar: tk.Scrollbar = tk.Scrollbar(data_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.bar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.bar.grid(row=0, column=1, sticky="ns")

        # ---------------- 右侧：控制面板区域 ----------------
        ctrl_frame: tk.Frame = tk.Frame(main_frame, bg='#efefef', width=250,
                                        relief="groove", borderwidth=2)
        ctrl_frame.grid(row=0, column=1, sticky="ns", padx=0)
        ctrl_frame.grid_propagate(False) # 强制锁定宽度

        control_grid: tk.Frame = tk.Frame(ctrl_frame, bg='#efefef')
        control_grid.pack(fill=tk.X, pady=2)
        control_grid.columnconfigure(0, weight=1)
        control_grid.columnconfigure(1, weight=1)

        btn_config: dict[str, Any] = {'font': self.font, 'height': 2}

        control_row: int = 0
        # 各种操作按钮映射到 Controller 层
        self._get_data_button: tk.Button = tk.Button(control_grid,
                                                    text="获取控制台结果",
                                                    command=self._action_get_console_data,
                                                    **btn_config)
        self._get_data_button.grid(row=control_row, column=0, sticky="ew", padx=5, pady=5)
        self.update_data_button: tk.Button = tk.Button(control_grid,
                                                   text="刷新本地记录表",
                                                   command=self._action_refresh_data,
                                                   **btn_config)
        self.update_data_button.grid(row=control_row, column=1, sticky="ew", padx=5, pady=5)
        control_row += 1

        self.all_hit_button: tk.Button = tk.Button(control_grid,
                                                   text="All Hit",
                                                   command=self._action_show_all_hit,
                                                   **btn_config)
        self.all_hit_button.grid(row=control_row, column=0, sticky="ew", padx=5, pady=5)
        self.avg_sync_button: tk.Button = tk.Button(control_grid,
                                                    text="AvgAcc Sync Diff",
                                                    command=acc_sync_diff_analyze.analyze_3d,
                                                    **btn_config)
        self.avg_sync_button.grid(row=control_row, column=1, sticky="ew", padx=5, pady=5)
        control_row += 1

        info_modify_frame = tk.Frame(control_grid, relief="groove", borderwidth=2)
        info_modify_frame.grid(row=control_row, column=0, columnspan=2, sticky='n', padx=5, pady=5)
        info_modify_frame.columnconfigure(0, weight=1)
        info_modify_frame.columnconfigure(1, weight=1)

        info_modify_row: int = 0

        # 行0: '谱面游玩标识'
        history_name_label: tk.Label = tk.Label(info_modify_frame,
                                                text='谱面游玩标识',
                                                font=self.font,
                                                relief="groove")
        history_name_label.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew', padx=0, pady=0)
        info_modify_row += 1

        # 行1: 铺面游玩标识名称显示
        self.history_name_entry = tk.Entry(info_modify_frame, font=self.font, relief="sunken")
        self.history_name_entry.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew')
        info_modify_row += 1
        
        # 行2: '记录时间'
        history_record_time_label: tk.Label = tk.Label(info_modify_frame,
                                                       text='记录时间',
                                                       font=self.font,
                                                       relief="groove")
        history_record_time_label.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew')
        info_modify_row += 1

        # 行3: 铺面游玩时间显示
        history_record_time_value: tk.Label = tk.Label(info_modify_frame,
                                                       text="",
                                                       font=self.font,
                                                       relief="groove")
        history_record_time_value.grid(row=info_modify_row, column=0, columnspan=2, sticky='ew')
        info_modify_row += 1

        # 行4: 游玩模式显示
        history_mode_label: tk.Label = tk.Label(info_modify_frame,
                                                text='模式: ',
                                                font=self.font,
                                                relief="groove",
                                                anchor='e')
        history_mode_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_mode_value: ttk.Combobox = ttk.Combobox(
            info_modify_frame,
            values=['', '4KEZ', '4KHD', '4KIN', "6KEZ", "6KHD", "6KIN"],
            font=self.font)
        history_mode_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行4: 游玩难度显示
        history_difficulty_label: tk.Label = tk.Label(info_modify_frame,
                                                text='难度: ',
                                                font=self.font,
                                                relief="groove",
                                                anchor='e')
        history_difficulty_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_difficulty_value: ttk.Combobox = ttk.Combobox(
            info_modify_frame,
            values=[f"{i}" for i in range(1, 16)],
            font=self.font)
        history_difficulty_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行4: Combo显示
        history_combo_label: tk.Label = tk.Label(info_modify_frame,
                                                text='Combo: ',
                                                font=self.font,
                                                relief="groove",
                                                anchor='e')
        history_combo_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_combo_value: tk.Label = tk.Label(info_modify_frame,
                                                 text="0/0    ",
                                                 font=self.font,
                                                 relief="groove",
                                                 anchor='e')
        history_combo_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1

        # 行4: Notes数量显示
        history_keys_label: tk.Label = tk.Label(info_modify_frame,
                                                text='按键数量: ',
                                                font=self.font,
                                                relief="groove",
                                                anchor='e')
        history_keys_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_keys_value: tk.Label = tk.Label(info_modify_frame,
                                                text="0    ",
                                                font=self.font,
                                                relief="groove",
                                                anchor='e')
        history_keys_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1
        
        # 行5: Avg Delay显示
        history_delay_label: tk.Label = tk.Label(info_modify_frame,
                                                 text='平均延迟: ',
                                                 font=self.font,
                                                 relief="groove",
                                                 anchor='e')
        history_delay_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_delay_value: tk.Label = tk.Label(info_modify_frame,
                                                 text="000.000000ms  ",
                                                 font=self.font,
                                                 relief="groove",
                                                 anchor='e')
        history_delay_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1
        
        # 行6: Avg Acc显示
        history_acc_label: tk.Label = tk.Label(info_modify_frame,
                                               text='AvgAcc: ',
                                               font=self.font,
                                               relief="groove",
                                               anchor='e')
        history_acc_label.grid(row=info_modify_row, column=0, sticky='ew')
        history_acc_value: tk.Label = tk.Label(info_modify_frame,
                                               text='000.000000ms  ',
                                               font=self.font,
                                               relief="groove",
                                               anchor='e')
        history_acc_value.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1
        
        # 行7: 操作按钮
        self.style.configure("update.TButton", font=self.font, relief="raised",background='#A6E22B')
        self.history_update_button: ttk.Button = ttk.Button(info_modify_frame,
                                                            text='更新记录',
                                                            style="update.TButton",
                                                            command=self._action_change_mark)
        self.history_update_button.grid(row=info_modify_row, column=0, sticky='ew')
        
        self.style.configure("delete.TButton", font=self.font, relief="raised", foreground='#FF4040', background='#FF2020')
        self.history_delete_button: ttk.Button = ttk.Button(info_modify_frame,
                                                            text='删除记录',
                                                            style="delete.TButton",
                                                            command=self._action_delete_record)
        self.history_delete_button.grid(row=info_modify_row, column=1, sticky='ew')
        info_modify_row += 1


    # ==========================================
    # [Level 2] 数据访问与解析层 (Model / DAL)
    # ==========================================
    def _fetch_history_records(self) -> list[tuple[Any, ...]]:
        """[纯函数] 仅负责从 V4 数据库获取全部历史记录"""
        try:
            self.cur.execute("SELECT ROWID, SongMapName, RecordTime, Mode, Diff, Combo, AvgDelay, AllKeys, AvgAcc FROM HitDelayHistory")
            return self.cur.fetchall()
        except sqlite3.Error as e:
            self._logger.error(f"查询历史记录失败: {e}")
            return []

    def _parse_v4_hitmap(self, rowid: int) -> list[int]:
        """[纯函数] 负责从 V4 数据库读取 BLOB 并反序列化为小端整数列表"""
        try:
            self.cur.execute("SELECT HitMap FROM HitDelayHistory WHERE ROWID=?", (rowid,))
            result = self.cur.fetchone()
            if not result or not result[0]:
                return []

            hitmap_blob: bytes = result[0]
            num_ints: int = len(hitmap_blob) // 4
            ints_tuple: tuple[int, ...] = struct.unpack('<' + ('i' * num_ints), hitmap_blob)
            return list(ints_tuple)
        except (sqlite3.Error, struct.error) as e:
            self._logger.error(f"解析 HitMap 二进制数据失败: {e}")
            return []

    # ==========================================
    # [Level 2] 局部视图渲染层 (View Render)
    # ==========================================
    def _reset_ui_state(self) -> None:
        """重置右侧控制面板的状态"""
        self._get_data_button.config(state=tk.DISABLED)
        self.history_delete_button.config(state=tk.DISABLED)
        self.history_update_button.config(state=tk.DISABLED)
        self.history_name_entry.delete(0, tk.END)
        self.select_rowid = -1

    def _render_treeview(self, data_rows: list[tuple[Any, ...]]) -> None:
        """清空并重新渲染 Treeview 数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in data_rows:
            row_id, name, rec_time, mode, diff, combo, avg_delay, keys, acc = row
            delay_str: str = f"{avg_delay:.2f}ms" if avg_delay is not None else "N/A"
            acc_str: str = f"{acc:.2f}ms" if acc is not None else "N/A"

            self.tree.insert("", tk.END, values=(row_id, name, rec_time, mode, diff, combo, delay_str, keys, acc_str))

        if self.tree.get_children():
            self.tree.yview_moveto(1.0) # 自动滚动到底部

    def _do_matplotlib_draw(self) -> None:
        """[核心重构] 极简且稳健的 Matplotlib 数据绘图"""
        if not self.data_list:
            return

        plt.rcParams['font.family'] = ['LXGW WenKai Mono', 'SimHei', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.canvas.manager.set_window_title(f"单曲击打分析 - 记录ID: {self.select_rowid}")

        # 使用 matplotlib 原生 hist 进行高效率分桶，摒弃极易越界的 manual counting
        min_val, max_val = int(min(self.data_list)), int(max(self.data_list))
        bins = range(min_val - 1, max_val + 2)

        ax.hist(self.data_list, bins=bins, color='#32a9c7', edgecolor='black', alpha=0.8, linewidth=0.5)

        ax.set_title(f"击打延迟分布 (总计: {len(self.data_list)} notes)", fontsize=14)
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
        if self.select_rowid == -1: return
        if not messagebox.askyesno("确认删除", "确定要删除这条游玩记录吗？\n删除后不可恢复！"): return

        try:
            self.cur.execute("DELETE FROM HitDelayHistory WHERE ROWID=?", (self.select_rowid,))
            self.db.commit()
            self._logger.info(f"已删除记录 ROWID: {self.select_rowid}")
            self._action_refresh_data()
        except sqlite3.Error as e:
            self._logger.error(f"删除记录失败: {e}")
            messagebox.showerror("数据库错误", f"删除失败:\n{e}")

    def _action_change_mark(self) -> None:
        """UI 事件：修改选中记录的标记名称"""
        if self.select_rowid == -1: return
        new_mark: str = self.history_name_entry.get().strip()
        if not new_mark:
            messagebox.showwarning("警告", "请输入有效的标记名称！")
            return

        try:
            self.cur.execute("UPDATE HitDelayHistory SET SongMapName=? WHERE ROWID=?", (new_mark, self.select_rowid))
            self.db.commit()
            self._logger.info(f"已将 ROWID {self.select_rowid} 的标记修改为: {new_mark}")
            self._action_refresh_data()
        except sqlite3.Error as e:
            self._logger.error(f"修改标记失败: {e}")
            messagebox.showerror("数据库错误", f"修改失败:\n{e}")

    def _action_draw_single_line(self) -> None:
        """UI 事件：解析二进制数据并绘制单曲直方图"""
        if self.select_rowid == -1: return

        self.data_list = self._parse_v4_hitmap(self.select_rowid)
        if not self.data_list:
            messagebox.showwarning("警告", "该记录的击打数据为空或已损坏，无法绘图。")
            return

        self._logger.info(f"成功载入 {len(self.data_list)} 个 note 数据准备绘图。")
        self._do_matplotlib_draw()

    def _action_get_console_data(self) -> None:
        """UI 事件：通过 UIAutomation 获取控制台数据 (即将重构为 UDP)"""
        self._logger.info("尝试获取控制台数据...")
        messagebox.showinfo("提示", "功能占位：此部分逻辑即将被 UDP 通信模块重构替换。")

    def _action_show_all_hit(self) -> None:
        """UI 事件：显示全局全量直方图 (调用外部模块)"""
        try:
            analyzer = AllHitAnalyze()
        except Exception as e:
            self._logger.error(f"显示汇总图表失败: {e}")

    # ==========================================
    # [Level 0] 无状态 UI 独立交互 (Stateless UI callbacks)
    # ==========================================
    def _on_tree_select(self, event: tk.Event) -> None:
        """回调：点击表格行获取 ROWID 并更新右侧面板输入框"""
        selected_items: tuple[str, ...] = self.tree.selection()
        if not selected_items: return

        values: tuple[Any, ...] = self.tree.item(selected_items[0], "values")
        if values:
            self.select_rowid = int(values[0])
            self.history_name_entry.delete(0, tk.END)
            self.history_name_entry.insert(0, str(values[1]))

            # 激活对应的操作按钮
            self._get_data_button.config(state=tk.NORMAL)
            self.history_delete_button.config(state=tk.NORMAL)
            self.history_update_button.config(state=tk.NORMAL)

    def _on_tree_double_click(self, event: tk.Event) -> None:
        """回调：双击表格行快捷绘制单曲分析图表"""
        # 极客技巧：防误触检测。判断双击的坐标是否在有效的数据行上，防止双击表头触发崩溃
        item_id: str = self.tree.identify('item', event.x, event.y)
        if not item_id:
            return

        # 强制将选中的行设为当前双击的行 (防止双击过快导致 <<TreeviewSelect>> 未触发)
        self.tree.selection_set(item_id)
        self._on_tree_select(event)

        # 直接调度控制层的绘图事件
        self._action_draw_single_line()

    def _sort_treeview(self, col: str, reverse: bool) -> None:
        """回调：点击表头进行双向排序"""
        try:
            items: list[tuple[str, str]] = [(str(self.tree.set(k, col)), k) for k in self.tree.get_children('')]

            # 如果带有 'ms' 则尝试转换为 float 进行数值排序
            try:
                items.sort(key=lambda t: float(t[0].replace('ms', '')), reverse=reverse)
            except ValueError:
                items.sort(reverse=reverse)

            for index, (val, k) in enumerate(items):
                self.tree.move(k, '', index)

            # 翻转下次点击的排序方向
            self.tree.heading(col, command=lambda: self._sort_treeview(col, not reverse))
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
