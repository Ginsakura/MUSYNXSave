# -*- coding: utf-8 -*-
import logging
import math
import sqlite3
import struct

from matplotlib import patches
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plot
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import CheckButtons

from .config_manager import config, Logger

class AllHitAnalyze(object):
    """docstring for HitAnalyze"""

    def __init__(self, data: bytes | None = None):
        # super(AllHitAnalyze, self).__init__()
        self._logger: logging.Logger = Logger.get_logger(name="AllHitAnalyze")
        # self._db_source: bool = True
        if data is None:
            self._db_mode: bool = True
            db: sqlite3.Connection = sqlite3.connect('./musync_data/HitDelayHistory.db')
            cur: sqlite3.Cursor = db.cursor()
            cur.execute('select HitMap from HitDelayHistory')
            res: list[tuple[bytes]] = cur.fetchall()
            cur.close()
            db.close()
        else:
            self._db_mode: bool = False
            res: list[tuple[bytes]] = [(data,)]  # 模拟数据库查询结果, 单行数据
        hit_map_a: list[int] = [0]*150   # -150~-1
        hit_map_b: list[int] = [0]*251   # 0~+250
        self._sum_y_num: int = 0          # with miss
        self._sum_y_num_ext: int = 0      # only Exact
        self._sum_y_num_core: int = 0     # only Cyan Exact
        # Cyan_Exact,Exact,Great,Right,Miss
        self._rate: list[int] = [0,0,0,0,0]
        # ±5ms,±10ms,±20ms,±45ms,Exact,Great,Right,Miss
        self._accurate_rate: list[int] = [0,0,0,0,0,0,0,0]

        # 阈值常量（乘以10000）
        THRESHOLD_5   = 5 * 10000      # 50000
        THRESHOLD_10  = 10 * 10000     # 100000
        THRESHOLD_20  = 20 * 10000     # 200000
        THRESHOLD_45  = 45 * 10000     # 450000
        THRESHOLD_90  = 90 * 10000     # 900000
        THRESHOLD_150 = 150 * 10000    # 1500000
        THRESHOLD_250 = 250 * 10000    # 2500000

        # 改进的循环：更健壮、可读、修正负值取整问题
        for row in res:
            blob: bytes = row[0]
            if not blob:
                continue
            # 确定整数个数：blob长度除以4（因为int32是4字节）
            count: int = len(blob) // 4
            # 使用struct.unpack一次性解析所有整数, 格式为'<i'*count
            # 注意：如果数据量极大, 一次性unpack所有整数可能会占用大量内存,
            # 但总数据量可能可控（如数百万）, 可以分批处理。这里按原样一次性。
            ints = struct.unpack('<' + 'i'*count, blob)   # 返回tuple
            # hitmap_field:str = row[0]
            for ival in ints:
                self._sum_y_num += 1
                abs_ival: int = abs(ival)
                # 分类统计（基于 abs_ival）
                if abs_ival < THRESHOLD_5:
                    self._rate[0] += 1
                    self._accurate_rate[0] += 1
                elif abs_ival < THRESHOLD_10:
                    self._rate[0] += 1
                    self._accurate_rate[1] += 1
                elif abs_ival < THRESHOLD_20:
                    self._rate[0] += 1
                    self._accurate_rate[2] += 1
                elif abs_ival < THRESHOLD_45:
                    self._rate[0] += 1
                    self._accurate_rate[3] += 1
                elif abs_ival < THRESHOLD_90:
                    self._rate[1] += 1
                    self._accurate_rate[4] += 1
                elif abs_ival < THRESHOLD_150:
                    self._rate[2] += 1
                    self._accurate_rate[5] += 1
                elif abs_ival < THRESHOLD_250:
                    self._rate[3] += 1
                    self._accurate_rate[6] += 1
                else:
                    self._rate[4] += 1
                    self._accurate_rate[7] += 1

                # 统计 exact / cyan exact
                if abs_ival < THRESHOLD_45:
                    self._sum_y_num_core += 1
                    self._sum_y_num_ext += 1
                elif abs_ival < THRESHOLD_90:
                    self._sum_y_num_ext += 1

                # 更新直方图 (直接取整)
                # 更新命中地图 (尽量保持原有逻辑：0..249 -> hitMapB[idx],
                # >=250 -> hitMapB[250], 否则放入 hitMapA)
                idx = ival // 10000       # 等价于 floor(val)
                if 0 <= idx < 250:
                    hit_map_b[idx] += 1
                elif idx >= 250:
                    hit_map_b[250] += 1
                elif idx >= -150:
                    hit_map_a[idx] += 1
                else:
                    hit_map_a[-150] += 1

        self._x_axis:list[int] = [i for i in range(-150,251)]
        self._y_axis:list[int] = hit_map_a + hit_map_b

        # 全局区间
        self._avg, self._var, self._std = self._calculate_weighted_stats(
            self._x_axis, self._y_axis, self._sum_y_num
        )

        # 扩展区间 (61-240)
        self._avg_ext, self._var_ext, self._std_ext = self._calculate_weighted_stats(
            self._x_axis[61:240], self._y_axis[61:240], self._sum_y_num_ext
        )

        # 核心区间 (106-195)
        self._avg_core, self._var_core, self._std_core = self._calculate_weighted_stats(
            self._x_axis[106:195], self._y_axis[106:195], self._sum_y_num_core
        )
        self._logger.info(f'All Rate Data:   {self._avg:.4f}  {self._var:.4f}  '\
            f'{self._std:.4f}  {self._sum_y_num}')
        self._logger.info(f'Exact Rate: {self._avg_ext:.4f}  {self._var_ext:.4f}  '\
            f'{self._std_ext:.4f}  {self._sum_y_num_ext}')
        self._logger.info(f'Cyan Exact Rate: {self._avg_core:.4f}  {self._var_core:.4f}  '\
            f'{self._std_core:.4f}  {self._sum_y_num_core}')

    def _calculate_weighted_stats(
        self,
        x_data: list[int],
        y_data: list[int],
        total_y: float
        ) -> tuple[float, float, float]:
        """
        计算加权统计量：平均数、方差、标准差。

        Args:
            x_data: 样本值列表
            y_data: 权重（频数）列表
            total_y: 权重总和

        Returns:
            tuple: (均值, 方差, 标准差)
        """
        # 防御性编程：处理分母为 0 或空数据的情况
        if total_y <= 0 or not x_data:
            return 0.0, 0.0, 0.0

        # 1. 计算加权平均数 (Weighted Mean)
        # 使用生成器表达式降低内存占用
        avg: float = sum(
            x * y / total_y
            for x, y in zip(x_data, y_data, strict=True)
        )

        # 2. 计算加权方差 (Weighted Variance)
        var: float = sum(
            (y / total_y) * ((x - avg) ** 2)
            for x, y in zip(x_data, y_data, strict=True)
        )

        # 3. 计算标准差 (Standard Deviation)
        # 使用 math.sqrt 比 ** 0.5 语义更明确且在某些解释器下更快
        std: float = math.sqrt(var)

        return avg, var, std

    def show(self) -> tuple[list[int], int] | None:
        """主绘制入口"""
        # 预设中文字体 (如果你系统安装了此字体)
        plot.rcParams['font.serif'] = ["LXGW WenKai Mono"]
        plot.rcParams["font.sans-serif"] = ["LXGW WenKai Mono"]

        # 创建画板
        fig: Figure = plot.figure(
            f"{'All Hit Analyze' if self._db_mode else 'One Map Analyze'} "\
                f"(Total:{self._sum_y_num},  CyanEx:{self._rate[0]},  "\
                f"BlueEx:{self._rate[1]},  Great:{self._rate[2]},  "\
                f"Right:{self._rate[3]},  Miss:{self._rate[4]})",
            figsize=(16, 9) if self._db_mode else (8, 4.5)
        )
        fig.clear()

        # 布局划分
        grid: gridspec.GridSpec = gridspec.GridSpec(
            nrows=3, ncols=5,
            left=0.045, right=1.0, top=1.0, bottom=0.06, wspace=0.0, hspace=0.0
        )

        # 直方图 Axes
        ax1: Axes = fig.add_subplot(grid[:, :])
        ax1.format_coord = lambda x, y: f"x={int(x)}, y={int(y)}"
        self._draw_histogram_and_curves(fig, ax1)

        # 饼图 Axes
        if config.DonutChartInAllHitAnalyze:
            ax2: Axes = fig.add_subplot(grid[0:2, 3:])
            self._draw_pie_chart(ax2)

        # 如果是数据库模式, 直接显示图表;
        # 如果是单图模式, 可能在其他环境中调用, 暂不自动显示, 留给调用者控制显示时机
        if self._db_mode:
            plot.show()
            return None
        else:
            return (self._rate, self._sum_y_num, )

    def _draw_histogram_and_curves(self, fig: Figure, ax: Axes) -> None:
        """绘制直方图与高斯拟合曲线, 并添加交互组件"""
        ax.xaxis.set_major_locator(MultipleLocator(10 if self._db_mode else 20))

        # 1. 绘制底层直方图 (一次性渲染, 极大地提升性能)
        ax.bar(self._x_axis[:-1], self._y_axis[:-1], width=1, color='skyblue')
        ax.bar(self._x_axis[-1], self._y_axis[-1], width=1.5, color='#FF5757')
        ax.axvline(x=0, c='black', ls='-', lw=1)
        ax.axvline(x=249.5, c='orange', ls='--', lw=1, alpha=0.8)

        # 配置对称线参数: (绝对值, 颜色, 透明度)
        symmetry_lines: list[tuple[float, str, float]] = [
            (5.5, '#9dfff0', 0.8),
            (10.5, '#69f1f1', 0.8),
            (20.5, '#25d8d8', 0.8),
            (45.5, '#32a9c7', 0.8),   # 青色
            (90.5, '#2F97FF', 0.8),   # 蓝色
            (150.5, 'green', 0.8)  # 绿色
        ]

        # 批量绘制正负对称虚线 (虚线, 1px)
        for x_val, color, alpha in symmetry_lines:
            ax.axvline(x=x_val, c=color, ls='--', lw=1, alpha=alpha)
            ax.axvline(x=-x_val, c=color, ls='--', lw=1, alpha=alpha)

        # 2. 设置坐标轴与自动网格 (摒弃原先的手动计算逻辑)
        ax.set_xlabel("Delay(ms)", fontsize=15)
        ax.set_ylabel("HitCount", fontsize=15)
        ax.set_xlim(-152.5, 252.5)
        ax.grid(axis='y', linestyle='--', alpha=0.7) # 自动横向辅助线

        # 3. 计算正态分布的通用闭包函数
        def _calculate_pdf(x_data: list[int], avg: float, var: float, std: float, count: int) -> list[float]:
            if var <= 0 or std <= 0:
                return [0.0] * len(x_data)
            # 正态分布公式： f(x) = (1 / (σ * sqrt(2π))) * e^(-(x - μ)² / (2σ²))
            # 乘以总数 count 以将面积放大至直方图级别
            coeff = count / (math.sqrt(2 * math.pi) * std)
            return [coeff * math.exp(-((x - avg) ** 2) / (2 * var)) for x in x_data]

        # 计算三条曲线的数据
        pdf_all = _calculate_pdf( self._x_axis, self._avg,      self._var,      self._std,      self._sum_y_num     )
        pdf_ext = _calculate_pdf( self._x_axis, self._avg_ext,  self._var_ext,  self._std_ext,  self._sum_y_num_ext )
        pdf_core = _calculate_pdf(self._x_axis, self._avg_core, self._var_core, self._std_core, self._sum_y_num_core)

        _line_width = 2 if self._db_mode else 1

        # 4. 绘制曲线, 但先保存对象引用以便后续控制 (初始状态设为隐藏 visible=False)
        line_all, = ax.plot(self._x_axis, pdf_all, c='grey', lw=_line_width,
                             label=f'Global Fit (μ={self._avg:.2f}, σ={self._std:.2f})')
        line_ext, = ax.plot(self._x_axis, pdf_ext, c='black', lw=_line_width,
                             label=f'Exact Fit (μ={self._avg_ext:.2f}, σ={self._std_ext:.2f})')
        line_core, = ax.plot(self._x_axis, pdf_core, c='blue', lw=_line_width,
                              label=f'Cyan Exact Fit (μ={self._avg_core:.2f}, σ={self._std_core:.2f})')
        ax.legend(loc='upper left', prop={'size': 12})

        if self._db_mode:
            # 生成图例后, 再把不需要默认显示的曲线隐藏
            line_all.set_visible(False)
            line_ext.set_visible(False)

            # ---------------- 交互模块：CheckButtons ----------------
            # 在图表的右上角开辟一块区域放置 CheckButtons
            # [left, bottom, width, height]
            ax_check = fig.add_axes((0.05, 0.70, 0.20, 0.15))

            curves = [line_all, line_ext, line_core]
            labels = [str(curve.get_label()).split(' (')[0] for curve in curves] # 提取简短的 Label
            visibilities = [curve.get_visible() for curve in curves]

            # 绑定到实例属性防止被垃圾回收 (Garbage Collection)
            self._check_btn = CheckButtons(ax_check, labels, visibilities)

            # 回调函数：切换可见性
            def toggle_visibility(label: str | None) -> None:
                if label is None:
                    return
                idx = labels.index(label)
                curves[idx].set_visible(not curves[idx].get_visible())
                fig.canvas.draw_idle() # 触发重绘

            self._check_btn.on_clicked(toggle_visibility)

    def _draw_pie_chart(self, ax: Axes) -> None:
        """绘制高精度命中率饼图/甜甜圈图"""
        # 1. 绘制白色半透明背景 (Background) 来增强对比度和美观度
        ax.add_patch(patches.Rectangle((-1.5, -1.5), 3, 3, color="white")).set_alpha(0.75)

        # 2. 替代原代码的 Rectangle 补丁：通过扩大坐标轴范围来生成完美的白色内边距 (Padding)
        # pie 图的标准半径是 1 (范围 -1 到 1), 设置 1.5 就相当于四周多了 50% 的留白
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)

        # 3. 隐藏刻度和边框
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        sum_acc = sum(self._accurate_rate)
        if sum_acc == 0:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=12)
            return

        wedgeprops = {'width': 0.15, 'edgecolor': 'black', 'linewidth': 0.2}
        colors = ['#9dfff0', '#69f1f1', '#25d8d8', '#32a9c7', '#2F97FF', 'green', 'orange', 'red']
        if self._db_mode:
            labels_pie = ["EXACT<5ms", "EXACT<10ms", "EXACT<20ms", "EXACT<45ms", "Exact", "Great", "Right", "Miss"]
        else:
            labels_pie = ["<5ms", "<10ms", "<20ms", "<45ms", "Exact", "Great", "Right", "Miss"]


        pie_rtn, _ = ax.pie( # type: ignore
            self._accurate_rate,
            wedgeprops=wedgeprops,
            startangle=90,
            colors=colors,
        )

        if self._db_mode:
            # 现代化 f-string 格式化对齐
            # :>6 表示占6位并右对齐; :>6.2f 表示总共6位、保留2位小数并右对齐
            legend_labels = [
                f"{labels_pie[i]:<12} {count:>6} {count/sum_acc*100:>7.3f}%"
                for i, count in enumerate(self._accurate_rate)
            ]

            ax.legend(
                handles=pie_rtn,
                labels=legend_labels,
                loc='center',
                prop={'size': 11, 'family': 'LXGW WenKai Mono'} # 强制等宽字体以保证严格对齐
            )

            # 文字
            core_exact_sum = sum(self._accurate_rate[0:4])
            core_exact_per = (core_exact_sum / sum_acc * 100) if sum_acc > 0 else 0
            center_text = f"EXACT Total  {core_exact_sum:>6} {core_exact_per:>7.3f}%"

            ax.text(
                -0.41, 0.51, center_text,
                ha='left', va='top', fontsize=11, c='#00B5B5', weight='bold'
            )
        else:
            legend_labels = [
                f"{labels_pie[i]:<5} {count:>4} {count/sum_acc*100:>3.0f}%"
                for i, count in enumerate(self._accurate_rate)
            ]

            ax.legend(
                handles=pie_rtn,
                labels=legend_labels,
                loc='center',
                prop={'size': 10, 'family': 'LXGW WenKai Mono'} # 强制等宽字体以保证严格对齐
            )


if __name__ == '__main__':
    AllHitAnalyze().show()
