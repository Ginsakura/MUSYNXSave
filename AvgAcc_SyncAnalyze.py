# -*- coding: utf-8 -*-
import csv
import logging

from matplotlib import pyplot as plot
from matplotlib.ticker import MultipleLocator

from Resources import Logger

def analyze_3d() -> None:
    """读取 CSV 数据并生成 3D 散点图分析视图"""
    logger: logging.Logger = Logger.GetLogger("AvgAcc_SyncAnalyze.Analyze3D")

    # 强制类型注解
    acc: list[float] = []
    sync: list[float] = []
    diff: list[float] = []

    # 1. 安全的数据读取 (使用 csv 模块代替手动 split)
    try:
        with open('./musync_data/Acc-Sync.csv', mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for line_num, row in enumerate(reader, start=1):
                # 忽略空行
                if not row:
                    continue
                try:
                    # 按照 X, Z, Y 的逻辑读取 (假设 CSV 列序为: acc, sync, diff)
                    acc.append(float(row[0]))
                    sync.append(float(row[1]))
                    diff.append(float(row[2]))
                except (ValueError, IndexError):
                    logger.warning(f"Failed to parse row {line_num}: {row} - 已跳过")
                    continue
    except FileNotFoundError:
        logger.error("Acc-Sync.csv not found. 请确保文件路径正确。")
        return

    # 防御性检查
    if not acc or not sync or not diff:
        logger.error("No valid 3D data found in Acc-Sync.csv")
        return

    # 2. 3D 画布初始化
    # 解决中文字体显示问题
    plot.rcParams['font.sans-serif'] = ['LXGW WenKai Mono', 'SimHei']
    plot.rcParams['axes.unicode_minus'] = False

    fig = plot.figure('AvgAcc vs SYNC.Rate vs Diff (3D)', figsize=(9, 9))
    fig.clear()

    # 使用 projection='3d' 声明 3D 子图
    ax = fig.add_subplot(111, projection='3d')

    # 3. 动态轴距计算与限制 (依据你的 0~250, 0~125, 1~15 规范)
    max_acc: float = min(max(acc) + 5, 250.0)  # 最大不超过 250
    min_acc: float = max(min(acc) - 2.5, 0.0)
    min_sync: float = max(int(min(sync))-1, 0)

    ax.set_xlim(min_acc, max_acc)
    ax.set_ylim(1, 15)   # Diff 轴严格限制在 1~15
    ax.set_zlim(min_sync, 125)

    # 调整 3D 渲染包围盒的比例
    # 参数分别对应 (X轴渲染长度, Y轴渲染长度, Z轴渲染长度)
    # 我们将 X(acc) 设为最长 3，Z(sync) 设为中等 1.5，Y(diff) 深度压缩为 0.8
    ax.set_box_aspect((2.0, 1.0, 2.0))

    # 设置主刻度步长
    if (max(acc) <= 75):
        ax.xaxis.set_major_locator(MultipleLocator(2.5))
    else:
        ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    if (min(sync) > 80):
        ax.zaxis.set_major_locator(MultipleLocator(1))
    else:
        ax.zaxis.set_major_locator(MultipleLocator(2))

    # 设置 labelrotation=45 使得文字倾斜，避免紧凑布局下的重叠
    ax.tick_params(axis='x', labelrotation=30)

    # 4. 绘制参考线 (使用“后墙投影法”，绘制在 Y = 15 的面上)
    y_wall: float = 15.0  # 难度最大面

    reference_lines: dict[str, tuple[float, str]] = {
        'Max':      (125.0, 'red'),
        'BlackEx':  (122.0, 'black'),
        'RedEx':    (120.0, 'red'),
        'CyanEx':   (117.0, 'cyan'),
        'S':        (110.0, 'blue'),
        'A':        (95.0,  'green'),
        'B':        (75.0,  'orange'),
    }

    # 横向等级线
    for label, (z_line, color) in reference_lines.items():
        if z_line < min_sync:
            continue  # 跳过不在当前 Z 范围内的线

        line_style = "-" if z_line == 125.0 else "--"
        line_width = 1.5 if z_line == 125.0 else 1.2

        # 在 3D 中画线需要传入 (X_list, Y_list, Z_list)
        ax.plot(
            [min_acc, max_acc], [y_wall, y_wall], [z_line, z_line],
            linestyle=line_style, alpha=0.5, linewidth=line_width, color=color
        )
        # 添加文本标注 (zdir='x' 让文本贴合墙面)
        ax.text(
            max_acc, y_wall, z_line,
            f' {label}', color=color, fontsize=9, alpha=0.8
        )

    # 纵向 5ms 参考线 (同样绘制在 Y = 15 的后墙上)
    # for acc_line in range(0, int(max_acc) + 1, 5):
    #     if acc_line < min_acc:
    #         continue
    #     line_style = "-" if acc_line == 0 else "--"
    #     alpha_val = 1.0 if acc_line == 0 else 0.3

    #     ax.plot(
    #         [acc_line, acc_line], [y_wall, y_wall], [min(sync), 125],
    #         linestyle=line_style, alpha=alpha_val, linewidth=1, color='gray'
    #     )

    # 5. 绘制 3D 散点图
    # 增加深度着色或使用统一颜色
    scatter = ax.scatter(
        acc, diff, sync,
        c='#8a68d0', alpha=0.7, s=15, edgecolors='none'
    )

    # 6. 设置轴标签
    ax.set_xlabel('AvgAcc (ms)')
    ax.set_ylabel('Difficulty (Level)')
    ax.set_zlabel('SYNC.Rate (%)')

    # 调整初始视角 (仰角 20 度, 方位角 -45 度)
    ax.view_init(elev=20, azim=-45)

    # 紧凑布局
    plot.tight_layout()
    plot.show()

if __name__ == '__main__':
    analyze_3d()
