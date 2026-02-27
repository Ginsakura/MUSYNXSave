# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from typing import Final

from Resources import MapDataInfo, SaveDataInfo

# 定义偏移量常量，避免魔法数字
JITTER_OFFSET: Final[float] = 0.15

def diff_score_analyze() -> None:
    """分析谱面数据并生成难度与分数散点图"""

    # 1. 语义化的数据容器
    diff_4k: list[float] = []
    scores_4k: list[float] = []
    scores_by_diff_4k: dict[int, list[float]] = {i: [] for i in range(1, 16)}

    diff_6k: list[float] = []
    scores_6k: list[float] = []
    scores_by_diff_6k: dict[int, list[float]] = {i: [] for i in range(1, 16)}

    # 2. 数据解析层 (Data Parsing)
    data: list[MapDataInfo] = SaveDataInfo.saveInfoList
    for map_data in data:
        sync_rate: float = map_data.SyncNumber / 100.0

        if sync_rate <= 0.0:
            continue

        difficulty: int = int(map_data.SongDifficultyNumber)

        if map_data.SongKeys == "4Key":
            diff_4k.append(difficulty - JITTER_OFFSET)
            scores_4k.append(sync_rate)
            if difficulty in scores_by_diff_4k:
                scores_by_diff_4k[difficulty].append(sync_rate)
        else: # 6Key Mode
            diff_6k.append(difficulty + JITTER_OFFSET)
            scores_6k.append(sync_rate)
            if difficulty in scores_by_diff_6k:
                scores_by_diff_6k[difficulty].append(sync_rate)

    # 3. 统计计算层 (Statistics Calculation)
    stats_4k: dict[int, tuple[float, int]] = {}
    for diff, score_list in scores_by_diff_4k.items():
        if score_list:
            stats_4k[diff] = (sum(score_list) / len(score_list), len(score_list))

    stats_6k: dict[int, tuple[float, int]] = {}
    for diff, score_list in scores_by_diff_6k.items():
        if score_list:
            stats_6k[diff] = (sum(score_list) / len(score_list), len(score_list))

    # 4. 视图渲染层 (View Rendering)
    fig: Figure = plt.figure('难度与分数散点图', figsize=(8, 8))
    fig.clear()
    fig.subplots_adjust(left=0.075, bottom=0.06, right=0.58, top=0.994)

    ax: Axes = fig.add_subplot(111)
    ax_right: Axes = ax.twinx()  # 右侧双 Y 轴

    # 坐标轴刻度配置
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax_right.yaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.set_xlim(0, 16)

    # 自适应 Y 轴下限计算 (防御空列表)
    all_scores = scores_4k + scores_6k
    min_score: int = int(min(all_scores)) if all_scores else 125
    ax.set_ylim(min_score - 1, 125)
    ax_right.set_ylim(min_score - 1, 125)

    # 原生网格线
    # 替代原代码低效的 for 循环画竖线：ax.plot([mapData]*N, ...)
    ax.grid(axis='x', linestyle='--', alpha=0.6, linewidth=1)

    # 向量化水平延伸线
    # 替代原代码用推导式生成 [i for i in range(17)] 的笨重写法
    for diff, (avg, _) in stats_4k.items():
        # 4K 从当前难度向右延伸至 16
        ax.plot([diff, 16], [avg, avg], linestyle='--', alpha=1, linewidth=1, color='#1f77b4')
    for diff, (avg, _) in stats_6k.items():
        # 6K 从 0 向右延伸至当前难度
        ax.plot([0, diff], [avg, avg], linestyle='--', alpha=1, linewidth=1, color='#ff7f0e')

    # 批量绘制等级参考线
    ref_lines: list[tuple[float, str, str]] = [
        (122.0, 'BlackEx', 'black'),
        (120.0, 'RedEx', 'red'),
        (117.0, 'CyanEx', 'cyan'),
        (110.0, 'S', 'blue'),
        (95.0,  'A', 'green'),
        (75.0,  'B', 'orange')
    ]
    for y_val, label, color in ref_lines:
        if min_score < y_val:
            # axhline 比手动绘制一整条线性能高得多且无视 X 轴缩放
            ax.axhline(y=y_val, color=color, linestyle='-', alpha=0.7, linewidth=1)
            ax.text(15.5, y_val + 0.75, label, ha='right', va='top', fontsize=9, alpha=0.7)

    # 排序后绘制折线
    font_cn = {'family': 'LXGW WenKai Mono', 'weight': 'normal', 'size': 12}

    # 必须对 diff 排序，防止由于数据乱序导致折线图连线交叉错乱
    diff_keys_4k = sorted(stats_4k.keys())
    avg_vals_4k = [stats_4k[d][0] for d in diff_keys_4k]
    ax.plot(diff_keys_4k, avg_vals_4k, linestyle='-', color='orange',
            marker="D", markerfacecolor="Blue", alpha=0.7, linewidth=2, label="4Key Mode")

    diff_keys_6k = sorted(stats_6k.keys())
    avg_vals_6k = [stats_6k[d][0] for d in diff_keys_6k]
    ax.plot(diff_keys_6k, avg_vals_6k, linestyle='-', color='orange',
            marker="D", markerfacecolor="Red", alpha=0.7, linewidth=2, label="6Key Mode")

    # 绘制散点
    ax.scatter(diff_4k, scores_4k, alpha=0.7, color='#8A68D0', s=5)
    ax.scatter(diff_6k, scores_6k, alpha=0.7, color='#F83535', s=5)

    # 现代化文本格式化
    label_texts: list[str] = []
    for d in diff_keys_4k:
        avg, count = stats_4k[d]
        # 使用现代 f-string 的 :>7.3f 进行右对齐保留三位小数格式化
        label_texts.append(f"难度: 4K {d:02d} Avg:{avg:>7.3f}% 计数:{count:02d}")
    label_texts.append("")
    for d in diff_keys_6k:
        avg, count = stats_6k[d]
        label_texts.append(f"难度: 6K {d:02d} Avg:{avg:>7.3f}% 计数:{count:02d}")

    # 将总结文本输出在图表外部空白处 (X=18)
    ax.text(18, 123, "\n".join(label_texts), ha="left", va="top", alpha=1, fontdict=font_cn)

    ax.set_xlabel('Difficulty')
    ax.set_ylabel('SYNC.Rate')
    ax.legend(prop=font_cn, framealpha=0.4)

    plt.show()

if __name__ == '__main__':
    analyze()
