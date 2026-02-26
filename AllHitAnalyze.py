# -*- coding: utf-8 -*-
import logging
import math
import sqlite3
import struct

from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plot
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import CheckButtons

from Resources import Config, Logger

class AllHitAnalyze(object):
    """docstring for HitAnalyze"""

    def __init__(self):
        # super(AllHitAnalyze, self).__init__()
        self.logger: logging.Logger = Logger.GetLogger(name="AllHitAnalyze")
        db: sqlite3.Connection = sqlite3.connect('./musync_data/HitDelayHistory.db')
        cur: sqlite3.Cursor = db.cursor()
        cur.execute('select HitMap from HitDelayHistory')
        res: list[tuple[bytes]] = cur.fetchall()
        cur.close()
        db.close()
        hit_map_a: list[int] = [0]*150   # -150~-1
        hit_map_b: list[int] = [0]*251   # 0~+250
        self.sum_y_num: int = 0          # with miss
        self.sum_y_num_ext: int = 0      # only Exact
        self.sum_y_num_core: int = 0     # only Cyan Exact
        # Cyan_Exact,Exact,Great,Right,Miss
        self.rate: list[int] = [0,0,0,0,0]
        # ±5ms,±10ms,±20ms,±45ms,Exact,Great,Right,Miss
        self.accurate_rate: list[int] = [0,0,0,0,0,0,0,0]

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
            # 使用struct.unpack一次性解析所有整数，格式为'<i'*count
            # 注意：如果数据量极大，一次性unpack所有整数可能会占用大量内存，但总数据量可能可控（如数百万），可以分批处理。这里按原样一次性。
            ints = struct.unpack('<' + 'i'*count, blob)   # 返回tuple
            # hitmap_field:str = row[0]
            for ival in ints:
                self.sum_y_num += 1
                abs_ival: int = abs(ival)
                # 分类统计（基于 abs_ival）
                if abs_ival < THRESHOLD_5:
                    self.rate[0] += 1
                    self.accurate_rate[0] += 1
                elif abs_ival < THRESHOLD_10:
                    self.rate[0] += 1
                    self.accurate_rate[1] += 1
                elif abs_ival < THRESHOLD_20:
                    self.rate[0] += 1
                    self.accurate_rate[2] += 1
                elif abs_ival < THRESHOLD_45:
                    self.rate[0] += 1
                    self.accurate_rate[3] += 1
                elif abs_ival < THRESHOLD_90:
                    self.rate[1] += 1
                    self.accurate_rate[4] += 1
                elif abs_ival < THRESHOLD_150:
                    self.rate[2] += 1
                    self.accurate_rate[5] += 1
                elif abs_ival < THRESHOLD_250:
                    self.rate[3] += 1
                    self.accurate_rate[6] += 1
                else:
                    self.rate[4] += 1
                    self.accurate_rate[7] += 1

                # 统计 exact / cyan exact
                if abs_ival < THRESHOLD_45:
                    self.sum_y_num_core += 1
                    self.sum_y_num_ext += 1
                elif abs_ival < THRESHOLD_90:
                    self.sum_y_num_ext += 1

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

        self.x_axis:list[int] = [i for i in range(-150,251)]
        self.y_axis:list[int] = hit_map_a + hit_map_b

        # 全局区间
        self.avg, self.var, self.std = self._calculate_weighted_stats(
            self.x_axis, self.y_axis, self.sum_y_num
        )

        # 扩展区间 (61-240)
        self.avg_ext, self.var_ext, self.std_ext = self._calculate_weighted_stats(
            self.x_axis[61:240], self.y_axis[61:240], self.sum_y_num_ext
        )

        # 核心区间 (106-195)
        self.avg_core, self.var_core, self.std_core = self._calculate_weighted_stats(
            self.x_axis[106:195], self.y_axis[106:195], self.sum_y_num_core
        )
        self.logger.info(f'All Rate Data:   {self.avg:.4f}  {self.var:.4f}  {self.std:.4f}  {self.sum_y_num}')
        self.logger.info(f'Exact Rate: {self.avg_ext:.4f}  {self.var_ext:.4f}  {self.std_ext:.4f}  {self.sum_y_num_ext}')
        self.logger.info(f'Cyan Exact Rate: {self.avg_core:.4f}  {self.var_core:.4f}  {self.std_core:.4f}  {self.sum_y_num_core}')

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

    def show(self) -> None:
        """主绘制入口"""
        # 预设中文字体 (如果你系统安装了此字体)
        plot.rcParams['font.serif'] = ["LXGW WenKai Mono"]
        plot.rcParams["font.sans-serif"] = ["LXGW WenKai Mono"]

        # 创建画板
        fig: Figure = plot.figure(
            f"HitAnalyze (Total:{self.sum_y_num},  CyanEx:{self.rate[0]},  "
            f"BlueEx:{self.rate[1]},  Great:{self.rate[2]},  Right:{self.rate[3]},  Miss:{self.rate[4]})",
            figsize=(16, 9)
        )
        fig.clear()

        # 布局划分
        grid: gridspec.GridSpec = gridspec.GridSpec(
            3, 5, left=0.045, right=0.98, top=0.95, bottom=0.06, wspace=0.2, hspace=0.2
        )

        # 直方图 Axes
        ax1: Axes = fig.add_subplot(grid[:, :])
        ax1.format_coord = lambda x, y: f"x={int(x)}, y={int(y)}"
        self._draw_histogram_and_curves(fig, ax1)

        # 饼图 Axes
        if Config.DonutChartinAllHitAnalyze:
            ax2: Axes = fig.add_subplot(grid[0:2, 3:])
            ax2.format_coord = lambda x, y: f"x={x:.3f}, y={y:.3f}"
            self._draw_pie_chart(ax2)

        plot.show()

    def _draw_histogram_and_curves(self, fig: Figure, ax1: Axes) -> None:
        """绘制直方图与高斯拟合曲线，并添加交互组件"""

        # 1. 绘制底层直方图 (一次性渲染，极大地提升性能)
        ax1.bar(self.x_axis, self.y_axis, width=1, color='skyblue')

        # 2. 设置坐标轴与自动网格 (摒弃原先的手动计算逻辑)
        ax1.set_xlabel("Delay(ms)", fontsize=15)
        ax1.set_ylabel("HitCount", fontsize=15)
        ax1.set_xlim(-155, 255)
        ax1.grid(axis='y', linestyle='--', alpha=0.7) # 自动横向辅助线

        # 3. 计算正态分布的通用闭包函数
        def calculate_pdf(x_data: list[int], avg: float, var: float, std: float, count: int) -> list[float]:
            if var <= 0 or std <= 0:
                return [0.0] * len(x_data)
            # 正态分布公式： f(x) = (1 / (σ * sqrt(2π))) * e^(-(x - μ)² / (2σ²))
            # 乘以总数 count 以将面积放大至直方图级别
            coeff = count / (math.sqrt(2 * math.pi) * std)
            return [coeff * math.exp(-((x - avg) ** 2) / (2 * var)) for x in x_data]

        # 计算三条曲线的数据
        pdf_all = calculate_pdf( self.x_axis, self.avg,      self.var,      self.std,      self.sum_y_num     )
        pdf_ext = calculate_pdf( self.x_axis, self.avg_ext,  self.var_ext,  self.std_ext,  self.sum_y_num_ext )
        pdf_core = calculate_pdf(self.x_axis, self.avg_core, self.var_core, self.std_core, self.sum_y_num_core)

        # 4. 绘制曲线，但先保存对象引用以便后续控制 (初始状态设为隐藏 visible=False)
        line_all, = ax1.plot(self.x_axis, pdf_all, color='grey', linewidth=2,
                             label=f'Global Fit (μ={self.avg:.2f}, σ={self.std:.2f})')
        line_ext, = ax1.plot(self.x_axis, pdf_ext, color='black', linewidth=2,
                             label=f'Exact Fit (μ={self.avg_ext:.2f}, σ={self.std_ext:.2f})')
        line_core, = ax1.plot(self.x_axis, pdf_core, color='blue', linewidth=2,
                              label=f'Cyan Exact Fit (μ={self.avg_core:.2f}, σ={self.std_core:.2f})')
        ax1.legend(loc='upper left', prop={'size': 12})

        # 生成图例后，再把不需要默认显示的曲线隐藏
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
        self.check_btn = CheckButtons(ax_check, labels, visibilities)

        # 回调函数：切换可见性
        def toggle_visibility(label: str | None) -> None:
            if label is None:
                return
            idx = labels.index(label)
            curves[idx].set_visible(not curves[idx].get_visible())
            fig.canvas.draw_idle() # 触发重绘

        self.check_btn.on_clicked(toggle_visibility)

    def _draw_pie_chart(self, ax2: Axes) -> None:
        """绘制高精度命中率饼图/甜甜圈图"""
        # 1. 强制设置背景为纯白，不透明，且提升 Z 轴层级盖住 ax1
        ax2.patch.set_visible(True)
        ax2.patch.set_facecolor('white')
        ax2.patch.set_alpha(1.0)
        ax2.set_zorder(10)  # 关键点：层级设为 10，确保它在直方图上方

        # 2. 替代原代码的 Rectangle 补丁：通过扩大坐标轴范围来生成完美的白色内边距 (Padding)
        # pie 图的标准半径是 1 (范围 -1 到 1)，设置 1.5 就相当于四周多了 50% 的留白
        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-1.5, 1.5)

        # 3. 隐藏刻度和边框
        ax2.set_xticks([])
        ax2.set_yticks([])
        for spine in ax2.spines.values():
            spine.set_visible(False)

        sum_acc = sum(self.accurate_rate)
        if sum_acc == 0:
            ax2.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=12)
            return

        wedgeprops = {'width': 0.15, 'edgecolor': 'black', 'linewidth': 0.2}
        colors = ['#9dfff0', '#69f1f1', '#25d8d8', '#32a9c7', '#2F97FF', 'green', 'orange', 'red']
        labels_pie = ["EXACT<5ms", "EXACT<10ms", "EXACT<20ms", "EXACT<45ms", "Exact", "Great", "Right", "Miss"]

        pie_rtn, _ = ax2.pie(
            self.accurate_rate,
            wedgeprops=wedgeprops,
            startangle=90,
            colors=colors,
        )

        # 现代化 f-string 格式化对齐
        # :>6 表示占6位并右对齐; :>6.2f 表示总共6位、保留2位小数并右对齐
        legend_labels = [
            f"{labels_pie[i]:<12} {count:>6} {count/sum_acc*100:>7.3f}%"
            for i, count in enumerate(self.accurate_rate)
        ]

        ax2.legend(
            handles=pie_rtn,
            labels=legend_labels,
            loc='center',
            prop={'size': 11, 'family': 'LXGW WenKai Mono'} # 强制等宽字体以保证严格对齐
        )

        # 文字
        core_exact_sum = sum(self.accurate_rate[0:4])
        core_exact_per = (core_exact_sum / sum_acc * 100) if sum_acc > 0 else 0
        center_text = f"EXACT Total  {core_exact_sum:>6} {core_exact_per:>7.3f}%"

        ax2.text(
            -0.41, 0.51, center_text,
            ha='left', va='top', fontsize=11, color='#00B5B5', weight='bold'
        )

if __name__ == '__main__':
    AllHitAnalyze().show()
