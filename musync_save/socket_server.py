# -*- coding: utf-8 -*-
"""
Socket Server — 接收游戏插件的 SETTLE 数据，处理/持久化/生成图表/回传 RESULT。
对应 tasks 10.1-10.7。
"""
import io
import json
import logging
import math
import os
import socket
import struct
import sqlite3
import threading
from datetime import datetime as dt
from typing import Optional

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from .config_manager import config, Logger

_logger: logging.Logger = Logger.get_logger("SocketServer")

# ---- 颜色映射（与 C# GradeColor 同步） ----
# knockDistance 阈值 → (early_color, late_color) as matplotlib hex
_COLOR_TABLE = [
    (50000,   '#00FFFF', '#00FFFF'),   # Cyan
    (100000,  '#FFFF00', '#008080'),   # Yellow / DarkCyan
    (450000,  '#808000', '#0000FF'),   # DarkYellow / Blue
    (900000,  '#00FF00', '#FF00FF'),   # Green / Magenta
    (1500000, '#800080', '#800080'),   # DarkMagenta
]
_COLOR_DEFAULT = '#FF0000'  # Red


def grade_color_hex(knock_distance: int) -> str:
    """返回 matplotlib hex 颜色字符串。零分配概念（Python 侧不苛求）。"""
    abs_kd = abs(knock_distance)
    early = knock_distance < 0
    for threshold, early_c, late_c in _COLOR_TABLE:
        if abs_kd < threshold:
            return early_c if early else late_c
    return _COLOR_DEFAULT


# ---- 帧协议 ----

def _read_frame(conn: socket.socket) -> Optional[bytes]:
    """读取一帧: [4 字节大端长度][payload]"""
    header = _recv_exact(conn, 4)
    if header is None:
        return None
    length = struct.unpack('>I', header)[0]
    if length <= 0 or length > 10 * 1024 * 1024:
        return None
    return _recv_exact(conn, length)


def _write_frame(conn: socket.socket, payload: bytes) -> None:
    header = struct.pack('>I', len(payload))
    conn.sendall(header + payload)


def _recv_exact(conn: socket.socket, n: int) -> Optional[bytes]:
    buf = bytearray()
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            return None
        buf.extend(chunk)
    return bytes(buf)


# ---- 统计计算 ----

def _compute_stats(hits: list[int]) -> dict:
    """计算 avg（带符号）、std、各判定计数。hits 元素为 knockDistance。"""
    if not hits:
        return {'avg': 0.0, 'std': 0.0, 'count': 0}

    delays_ms = [kd / 10000.0 for kd in hits]
    n = len(delays_ms)
    avg = sum(delays_ms) / n
    variance = sum((d - avg) ** 2 for d in delays_ms) / n
    std = math.sqrt(variance)

    # 各判定计数（与游戏 JudgeGrade 阈值对齐）
    ex = exact = great = right = miss = 0
    for kd in hits:
        abs_kd = abs(kd)
        if abs_kd < 50000:
            ex += 1
        elif abs_kd < 100000:
            exact += 1
        elif abs_kd < 450000:
            great += 1
        elif abs_kd < 900000:
            right += 1
        elif abs_kd < 1500000:
            miss += 1  # 注意：这里 miss 对应的是 >=900000 但 <1500000 的区间
        else:
            miss += 1

    return {
        'avg': round(avg, 2),
        'std': round(std, 2),
        'count': n,
        'ex': ex, 'exact': exact, 'great': great, 'right': right, 'miss': miss,
    }


# ---- 校准字段 ----

def _compute_calibration(avg: float) -> dict:
    """计算校准窗口。|avg|<=2 → calibrated=true。"""
    if abs(avg) <= 2.0:
        return {'calibrated': True, 'calDir': 0, 'calLo': 0, 'calHi': 0}

    direction = 1.0 if avg > 0 else -1.0
    abs_avg = abs(avg)
    lo = max(0.0, abs_avg - 3.0)
    hi = abs_avg + 3.0
    return {
        'calibrated': False,
        'calDir': direction,
        'calLo': round(lo, 1),
        'calHi': round(hi, 1),
    }


# ---- 图表生成 ----

def _generate_scatter_png(hits: list[int]) -> bytes:
    """散点图：x=序号，y=delay_ms，颜色=早/晚编码。标注 0 线。"""
    if not hits:
        return b''

    delays_ms = [kd / 10000.0 for kd in hits]
    colors = [grade_color_hex(kd) for kd in hits]
    x = list(range(len(delays_ms)))

    fig = Figure(figsize=(8, 4), dpi=100)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.scatter(x, delays_ms, c=colors, s=8, edgecolors='none')
    ax.axhline(y=0, color='white', linewidth=0.5, linestyle='--')
    ax.set_xlabel('Note #')
    ax.set_ylabel('Delay (ms)')
    ax.set_title('Hit Delay Scatter')
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_color('#444')
    fig.tight_layout()

    buf = io.BytesIO()
    canvas.print_png(buf)
    plt.close(fig)
    return buf.getvalue()


def _generate_distribution_png(hits: list[int]) -> bytes:
    """分布直方图：体现非对称。"""
    if not hits:
        return b''

    delays_ms = [kd / 10000.0 for kd in hits]

    fig = Figure(figsize=(8, 4), dpi=100)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.hist(delays_ms, bins=50, color='#4fc3f7', edgecolor='#1a1a2e', alpha=0.8)
    ax.axvline(x=0, color='red', linewidth=1, linestyle='--', label='0 ms')
    ax.set_xlabel('Delay (ms)')
    ax.set_ylabel('Count')
    ax.set_title('Delay Distribution')
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.legend(facecolor='#333', edgecolor='#555', labelcolor='white')
    for spine in ax.spines.values():
        spine.set_color('#444')
    fig.tight_layout()

    buf = io.BytesIO()
    canvas.print_png(buf)
    plt.close(fig)
    return buf.getvalue()


# ---- 持久化 ----

def _persist_to_db(data: dict, stats: dict, hits: list[int]) -> None:
    """写入 HitDelayHistory.db，复用现有 schema。"""
    db_path = './musync_data/HitDelayHistory.db'
    if not os.path.isfile(db_path):
        _logger.warning(f"Database not found: {db_path}, skip persist.")
        return

    try:
        # 构造 HitMap bytes（小端 int32 数组）
        hitmap_bytes = struct.pack('<' + ('i' * len(hits)), *hits) if hits else b''

        record_time = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        song_name_str = data.get('songName', f"SID_{data.get('sid', 0)}")
        mode = data.get('mode', '')
        diff = data.get('diff', 0)
        combo_str = f"{data.get('maxcombo', 0)}/{data.get('maxcombo', 0)}"
        all_keys = len(hits)
        avg_delay = stats['avg']
        avg_acc = 0.0  # 可从 stats 推算，暂留 0

        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO HitDelayHistory
                (SongMapName, RecordTime, Mode, Diff, Combo, AllKeys, AvgDelay, AvgAcc, HitMap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (song_name_str, record_time, mode, diff, combo_str, all_keys, avg_delay, avg_acc, hitmap_bytes))
            db.commit()
        _logger.info(f"Persisted settle data to DB: {song_name_str}")
    except Exception as e:
        _logger.error(f"DB persist failed: {e}")


# ---- 连接处理 ----

def _handle_connection(conn: socket.socket) -> None:
    """处理单个连接（在 worker 线程中执行）。"""
    try:
        payload = _read_frame(conn)
        if payload is None:
            return

        data = json.loads(payload.decode('utf-8'))
        if data.get('cmd') != 'SETTLE':
            return

        hits = data.get('hits', [])
        stats = _compute_stats(hits)

        # 合并游戏端传来的 Total 计数（如果有的话优先用游戏端的）
        for key in ('totalEx', 'totalExact', 'totalGreat', 'totalRight', 'totalMiss', 'totalCombo'):
            game_key = key[5:].lower() if key.startswith('total') else key  # ex, exact, ...
            # 游戏端 JSON 字段名: ex, exact, great, right, miss, combo
            short_key = key.replace('total', '').lower()
            if short_key in data:
                stats[key] = data[short_key]
            elif key.lower() in stats:
                stats[key] = stats[key.lower()]

        # 校准
        cal = _compute_calibration(stats['avg'])
        stats.update(cal)

        # 持久化
        _persist_to_db(data, stats, hits)

        # 生成图表
        charts = []
        scatter_png = _generate_scatter_png(hits)
        if scatter_png:
            charts.append({'name': 'scatter', 'len': len(scatter_png), 'bytes': scatter_png})

        dist_png = _generate_distribution_png(hits)
        if dist_png:
            charts.append({'name': 'distribution', 'len': len(dist_png), 'bytes': dist_png})

        # 组装 RESULT 响应
        result_json = json.dumps({
            'cmd': 'RESULT',
            'stats': stats,
            'charts': [{'name': c['name'], 'len': c['len']} for c in charts],
        }).encode('utf-8')

        # 帧 = JSON + 各 PNG bytes
        response = result_json
        for c in charts:
            response += c['bytes']

        _write_frame(conn, response)
        _logger.info(f"RESULT sent: {len(charts)} charts, avg={stats['avg']}")

    except Exception as e:
        _logger.error(f"Connection handler error: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ---- Server 主循环 ----

_server_thread: Optional[threading.Thread] = None
_running = False


def start_server() -> None:
    """启动 TCP Server（后台守护线程）。"""
    global _server_thread, _running
    if _running:
        return
    _running = True
    _server_thread = threading.Thread(target=_server_loop, daemon=True, name="MUSYNC_SocketServer")
    _server_thread.start()
    _logger.info("Socket Server started.")


def stop_server() -> None:
    global _running
    _running = False


def _server_loop() -> None:
    port = config.SocketPort if hasattr(config, 'SocketPort') else 26531
    host = '127.0.0.1'

    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(4)
        srv.settimeout(1.0)  # 每秒检查 _running 标志
        _logger.info(f"Socket Server listening on {host}:{port}")

        while _running:
            try:
                conn, addr = srv.accept()
                # 10.7 worker 线程处理单连接，不阻塞 accept 循环
                t = threading.Thread(target=_handle_connection, args=(conn,), daemon=True)
                t.start()
            except socket.timeout:
                continue
    except Exception as e:
        _logger.error(f"Socket Server error: {e}")
    finally:
        try:
            srv.close()
        except Exception:
            pass
        _logger.info("Socket Server stopped.")
