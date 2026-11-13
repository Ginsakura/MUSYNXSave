using System.Collections.Generic;
using System.Threading;
using UnityEngine;

namespace MUSYNCDelay.Data
{
    /// <summary>
    /// 4.2 当前延迟值存储（单条模式，两个值类型字段，无 GC）
    /// + 本局 hits 缓冲（结算时发送，用 List 但在 Reset 时 Clear 而非 new）
    /// </summary>
    public static class SessionData
    {
        // 4.2 当前一条延迟（值类型，覆盖写，无 GC）
        private static float _currentDelayMs;
        private static Color _currentColor;
        private static bool _hasCurrent;

        public static float CurrentDelayMs { get { return _currentDelayMs; } }
        public static Color CurrentColor { get { return _currentColor; } }
        public static bool HasCurrent { get { return _hasCurrent; } }

        /// <summary>每次打击覆盖写（主线程调用，无需锁）</summary>
        public static void SetCurrent(float delayMs, Color color)
        {
            _currentDelayMs = delayMs;
            _currentColor = color;
            _hasCurrent = true;
        }

        // 本局 hits 缓冲（结算时发送）
        // 预分配 List，Reset 时 Clear 而非 new，减少 GC
        private static readonly List<long> _hits = new List<long>(2048);

        public static void AddHit(long knockDistance)
        {
            _hits.Add(knockDistance);
        }

        /// <summary>返回 hits 的只读快照引用（结算时调用，之后 Clear）</summary>
        public static List<long> GetHitsSnapshot()
        {
            return _hits;
        }

        /// <summary>Reset 时清空</summary>
        public static void Reset()
        {
            _currentDelayMs = 0f;
            _currentColor = Color.white;
            _hasCurrent = false;
            _hits.Clear();
        }
    }

    /// <summary>
    /// 4.4 线程安全缓存容器 — 后台 Socket 线程写入、主线程读取的结算结果
    /// </summary>
    public static class SettleCache
    {
        // 用 Interlocked.Exchange 交换引用，避免半写状态
        private static SettleResult _result;
        private static int _connected; // 0 = 未连接/失败, 1 = 已连接

        public static SettleResult Result { get { return _result; } }
        public static bool Connected { get { return VolatileRead(ref _connected) == 1; } }

        public static void SetResult(SettleResult result)
        {
            Interlocked.Exchange(ref _result, result);
        }

        public static void SetConnected(bool connected)
        {
            Interlocked.Exchange(ref _connected, connected ? 1 : 0);
        }

        public static void Clear()
        {
            Interlocked.Exchange(ref _result, null);
            Interlocked.Exchange(ref _connected, 0);
        }

        private static int VolatileRead(ref int loc)
        {
            return Thread.VolatileRead(ref loc);
        }
    }

    /// <summary>
    /// 结算结果数据结构（后台线程反序列化后写入缓存）
    /// </summary>
    public class SettleResult
    {
        public SettleStats stats;
        public List<ChartEntry> charts;
    }

    public class SettleStats
    {
        public float avg;
        public float std;
        public int totalEx;
        public int totalExact;
        public int totalGreat;
        public int totalRight;
        public int totalMiss;
        public int totalCombo;
        public bool calibrated;
        // 校准窗口
        public float calDir;     // +1 或 -1
        public float calLo;      // 幅度下界
        public float calHi;      // 幅度上界
    }

    public class ChartEntry
    {
        public string name;
        public int len;
        public byte[] pngBytes;
    }
}
