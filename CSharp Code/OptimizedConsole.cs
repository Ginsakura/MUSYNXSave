// OptimizedConsole.cs - 静态单例模式，与LocalUdpClient设计对齐
using Microsoft.Win32.SafeHandles;
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using UnityEngine;

namespace BMSLib
{
    /// <summary>
    /// 优化的控制台管理器（静态单例，延迟初始化，资源安全）
    /// 与LocalUdpClient设计模式保持一致
    /// </summary>
    public static class OptimizedConsole
    {
        /* ==================== 配置常量（可外部修改） ==================== */
        public static class Config
        {
            public static string Title = "MUSYNX Delay (请勿关闭)";
            public static ConsoleColor ForegroundColor = ConsoleColor.Red;
            public static ConsoleColor BackgroundColor = ConsoleColor.White;
            public static int WindowWidth = 30;
            public static int WindowHeight = 4;
            public static bool Enabled = true;  // 总开关，可全局禁用控制台
        }

        /* ==================== 延迟初始化单例 ==================== */
        private static readonly Lazy<ConsoleInstance> _instance = new Lazy<ConsoleInstance>(
            CreateInstance, LazyThreadSafetyMode.ExecutionAndPublication);

        private static bool _preloaded = false;

        /* ==================== 生命周期管理 ==================== */
        private static ConsoleInstance CreateInstance()
        {
            if (!Config.Enabled)
            {
                Debug.Log("[Console] 已禁用，跳过初始化");
                return null;
            }

            try
            {
                var instance = new ConsoleInstance();
                // 在构造函数中完成初始化（原子操作）
                return instance;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[Console] 实例创建失败: {ex.Message}");
                return null;  // 静默失败，不影响主程序
            }
        }

        /* ==================== 生命周期管理 ==================== */
        /// <summary>
        /// 预加载（可在Unity Awake()中调用）
        /// </summary>
        public static void Preload()
        {
            if (Config.Enabled && !_instance.IsValueCreated)
            {
                var _ = _instance.Value;
            }
        }

        /// <summary>
        /// 快速初始化并应用默认配置（一键完成）
        /// 等效于用户提供的示例代码
        /// </summary>
        public static void InitializeDefault()
        {
            Preload();

            if (IsAvailable)
            {
                SetTitle(Config.Title);
                Console.ForegroundColor = Config.ForegroundColor;
                Console.BackgroundColor = Config.BackgroundColor;
                Console.SetWindowSize(Config.WindowWidth, Config.WindowHeight);

                Debug.Log("[Console] 默认配置已应用");
            }
        }

        /// <summary>
        /// 清理资源（可在Unity OnDestroy()中调用）
        /// </summary>
        public static void Cleanup()
        {
            if (_instance.IsValueCreated && _instance.Value != null)
            {
                _instance.Value.Shutdown();
                Debug.Log("[Console] 资源已释放");
            }
        }

        /* ==================== 状态查询 ==================== */
        public static bool IsInitialized => _instance.IsValueCreated;
        public static bool IsAvailable => _instance.IsValueCreated && _instance.Value != null;

        /* ==================== 简化API ==================== */
        /// <summary>
        /// 输出一行文本（带颜色可选）
        /// </summary>
        public static void WriteLine(string message, ConsoleColor? color = null)
        {
            if (!IsAvailable) return;

            var originalColor = Console.ForegroundColor;
            if (color.HasValue) Console.ForegroundColor = color.Value;

            Console.WriteLine(message);

            Console.ForegroundColor = originalColor;  // 恢复颜色
        }

        /// <summary>
        /// 输出文本（不换行）
        /// </summary>
        public static void Write(string message, ConsoleColor? color = null)
        {
            if (!IsAvailable) return;

            var originalColor = Console.ForegroundColor;
            if (color.HasValue) Console.ForegroundColor = color.Value;

            Console.Write(message);

            Console.ForegroundColor = originalColor;
        }

        public static void WriteHitDelay(long delay, string prefix = "> ")
        {
            long absDelay = Math.Abs(delay);
            string message = string.Format("Hit Delay: {0:F1}ms", delay / 10000.0);  // 保留1位小数

            // 颜色阈值映射（与原始逻辑完全对齐）
            ConsoleColor color = absDelay switch
            {
                < 50000L => ConsoleColor.Green,
                < 100000L => ConsoleColor.Cyan,
                < 450000L => ConsoleColor.DarkCyan,
                < 900000L => ConsoleColor.DarkBlue,
                < 1500000L => ConsoleColor.DarkGreen,
                _ => ConsoleColor.Red
            };

            // 使用统一API输出（自动恢复颜色）
            WriteLine(prefix + message, color);
        }

        /// <summary>
        /// 设置控制台标题
        /// </summary>
        public static void SetTitle(string title)
        {
            if (IsAvailable)
            {
                _instance.Value.SetTitle(title ?? Config.Title);
            }
        }

        /* ==================== 改造后的ConsoleInstance ==================== */
        private class ConsoleInstance
        {
            private TextWriter _oldOutput;

            public ConsoleInstance()
            {
                // 将原始Initialize()逻辑移入构造函数
                if (!AttachConsole(4294967295U))
                {
                    AllocConsole();
                }

                // 2. 关闭“快速编辑”模式，防止鼠标选中阻塞
                DisableQuickEditMode();

                _oldOutput = Console.Out;
                try
                {
                    var handle = new SafeFileHandle(GetStdHandle(-11), true);
                    var stream = new FileStream(handle, FileAccess.Write);
                    Console.SetOut(new StreamWriter(stream, Encoding.ASCII) { AutoFlush = true });
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[Console] 输出重定向失败: {ex.Message}");
                }
            }

            #region ---- 新增：关闭快速编辑 ----

            private const int STD_INPUT_HANDLE = -10;
            private const uint ENABLE_QUICK_EDIT_MODE = 0x0040;

            [DllImport("kernel32.dll", SetLastError = true)]
            private static extern IntPtr GetStdHandle(int nStdHandle);

            [DllImport("kernel32.dll", SetLastError = true)]
            private static extern bool GetConsoleMode(IntPtr hConsoleHandle, out uint lpMode);

            [DllImport("kernel32.dll", SetLastError = true)]
            private static extern bool SetConsoleMode(IntPtr hConsoleHandle, uint dwMode);

            private static void DisableQuickEditMode()
            {
                IntPtr hStdin = GetStdHandle(STD_INPUT_HANDLE);
                if (GetConsoleMode(hStdin, out uint mode))
                {
                    mode &= ~ENABLE_QUICK_EDIT_MODE;   // 关掉快速编辑
                    SetConsoleMode(hStdin, mode);
                }
            }

            #endregion ---- 新增：关闭快速编辑 ----

            public void Shutdown()
            {
                try
                {
                    Console.SetOut(_oldOutput);
                    FreeConsole();
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[Console] 关闭失败: {ex.Message}");
                }
            }

            public void SetTitle(string title)
            {
                try
                {
                    SetConsoleTitle(title);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[Console] 设置标题失败: {ex.Message}");
                }
            }

            // P/Invoke声明（保持完全一致）
            [DllImport("kernel32.dll", SetLastError = true)]
            private static extern bool AttachConsole(uint dwProcessId);

            [DllImport("kernel32.dll", SetLastError = true)]
            private static extern bool AllocConsole();

            [DllImport("kernel32.dll", SetLastError = true)]
            private static extern bool FreeConsole();

            [DllImport("kernel32.dll", CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Auto, SetLastError = true)]
            private static extern IntPtr GetStdHandle(int nStdHandle);

            [DllImport("kernel32.dll")]
            private static extern bool SetConsoleTitle(string lpConsoleTitle);
        }
    }
}