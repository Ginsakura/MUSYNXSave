using System;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;

namespace MUSYNCDelay.Config
{
    /// <summary>
    /// 3.1 配置 POCO — 字段对应 design D7 schema
    /// </summary>
    public class PluginConfig
    {
        public NetworkConfig network = new NetworkConfig();
        public GestureConfig gesture = new GestureConfig();
        public DelayOverlayConfig delay_overlay = new DelayOverlayConfig();
        public DrawerConfig drawer = new DrawerConfig();
    }

    public class NetworkConfig
    {
        public string host = "127.0.0.1";
        public int port = 26531;
        public int read_timeout_ms = 1500;
    }

    public class GestureConfig
    {
        public int drag_distance_px = 5;
        public int hold_ms = 300;
    }

    public class DelayOverlayConfig
    {
        public bool enabled = true;
        public RectConfig rect = new RectConfig { x = 0.02f, y = 0.30f, w = 0.12f, h = 0.045f };
        public bool aspect_locked = true;
        public int font_size = 24;
        public float alpha = 0.85f;
    }

    public class DrawerConfig
    {
        public EarConfig ear = new EarConfig();
        public float width_ratio = 0.5f;
        public float min_width_ratio = 0.3f;
        public float max_width_ratio = 0.95f;
    }

    public class EarConfig
    {
        public string side = "right";
        public float y = 0.5f;
    }

    public class RectConfig
    {
        public float x;
        public float y;
        public float w;
        public float h;
    }

    /// <summary>
    /// 3.2-3.4 JSON 配置读写 + debounce 写盘
    /// 使用极简手写 JSON 序列化/反序列化，避免引入第三方依赖。
    /// 配置结构简单且固定，手写解析足够。
    /// </summary>
    public static class ConfigManager
    {
        private static string _configPath;
        private static Timer _saveTimer;
        private static readonly object _lock = new object();
        private static bool _dirty;

        public static string ConfigPath
        {
            get
            {
                if (_configPath == null)
                {
                    string dir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
                    _configPath = Path.Combine(dir ?? ".", "config.json");
                }
                return _configPath;
            }
        }

        /// <summary>3.2 加载配置，文件缺失或字段缺失时写/补默认值</summary>
        public static PluginConfig Load()
        {
            var cfg = new PluginConfig();
            try
            {
                if (File.Exists(ConfigPath))
                {
                    string json = File.ReadAllText(ConfigPath, Encoding.UTF8);
                    SimpleJson.Populate(json, cfg);
                }
                else
                {
                    Save(cfg);
                }
            }
            catch (Exception ex)
            {
                Plugin.Logger?.LogWarning($"Config load failed, using defaults: {ex.Message}");
            }
            return cfg;
        }

        /// <summary>立即写盘</summary>
        public static void Save(PluginConfig cfg = null)
        {
            lock (_lock)
            {
                cfg = cfg ?? Plugin.Config;
                if (cfg == null) return;
                try
                {
                    string json = SimpleJson.Serialize(cfg);
                    File.WriteAllText(ConfigPath, json, Encoding.UTF8);
                    _dirty = false;
                }
                catch (Exception ex)
                {
                    Plugin.Logger?.LogError($"Config save failed: {ex.Message}");
                }
            }
        }

        /// <summary>3.4 标记脏 + debounce 写盘（300ms 合并）</summary>
        public static void MarkDirty()
        {
            _dirty = true;
            SaveDebounced(force: false);
        }

        public static void SaveDebounced(bool force)
        {
            if (force)
            {
                _saveTimer?.Dispose();
                _saveTimer = null;
                if (_dirty) Save();
                return;
            }
            // 重置 debounce timer
            _saveTimer?.Dispose();
            _saveTimer = new Timer(_ => Save(), null, 300, Timeout.Infinite);
        }
    }
}
