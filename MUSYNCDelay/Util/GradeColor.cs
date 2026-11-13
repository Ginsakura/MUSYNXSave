using UnityEngine;

namespace MUSYNCDelay.Util
{
    /// <summary>
    /// 4.1 颜色映射表 — 直接复用自旧 JudgeGrade.cs
    /// 符号语义：knockDistance &lt; 0 = 早击，≥ 0 = 晚击
    /// 返回 Color 值类型，零分配
    /// </summary>
    public static class GradeColor
    {
        // 预缓存 Color 值，避免每次 new
        private static readonly Color Cyan        = new Color(0f,    1f,    1f);
        private static readonly Color Yellow      = new Color(1f,    1f,    0f);
        private static readonly Color DarkCyan    = new Color(0f,    0.5f,  0.5f);
        private static readonly Color DarkYellow  = new Color(0.5f,  0.5f,  0f);
        private static readonly Color Blue        = new Color(0f,    0f,    1f);
        private static readonly Color Green       = new Color(0f,    1f,    0f);
        private static readonly Color Magenta     = new Color(1f,    0f,    1f);
        private static readonly Color DarkMagenta = new Color(0.5f,  0f,    0.5f);
        private static readonly Color Red         = new Color(1f,    0f,    0f);

        /// <summary>
        /// 根据 knockDistance 返回对应颜色。零分配，纯分支查表。
        /// </summary>
        public static Color Get(long knockDistance)
        {
            long abs = knockDistance < 0 ? -knockDistance : knockDistance;
            bool early = knockDistance < 0;

            if (abs < 50000L)       return Cyan;
            if (abs < 100000L)      return early ? Yellow : DarkCyan;
            if (abs < 450000L)      return early ? DarkYellow : Blue;
            if (abs < 900000L)      return early ? Green : Magenta;
            if (abs < 1500000L)     return DarkMagenta;
            return Red;
        }

        /// <summary>
        /// 将 knockDistance 转为毫秒（float），用于显示
        /// </summary>
        public static float ToMs(long knockDistance)
        {
            return knockDistance / 10000.0f;
        }
    }
}
