using System;
using BepInEx;
using BepInEx.Logging;
using HarmonyLib;
using MUSYNCDelay.Config;
using MUSYNCDelay.Net;
using MUSYNCDelay.UI;
using UnityEngine;

namespace MUSYNCDelay
{
    [BepInPlugin(GUID, NAME, VERSION)]
    public class Plugin : BaseUnityPlugin
    {
        public const string GUID = "com.musync.delay";
        public const string NAME = "MUSYNCDelay";
        public const string VERSION = "1.0.0";

        internal static new ManualLogSource Logger;
        internal static PluginConfig Config;

        private Harmony _harmony;

        private void Awake()
        {
            Logger = base.Logger;
            Logger.LogInfo($"{NAME} v{VERSION} loading...");

            // 3.2 加载配置
            Config = ConfigManager.Load();

            // 2.4 Harmony patch
            _harmony = new Harmony(GUID);
            _harmony.PatchAll();
            Logger.LogInfo("Harmony patches applied.");

            // 6.1-6.4 创建 Overlay Canvas（DontDestroyOnLoad）
            OverlayCanvas.EnsureCreated();

            Logger.LogInfo($"{NAME} loaded successfully.");
        }

        // 2.5 生命周期：退出时关闭 Socket + 落盘 config
        private void OnApplicationQuit()
        {
            Logger.LogInfo($"{NAME} shutting down...");
            SocketClient.Shutdown();
            ConfigManager.SaveDebounced(force: true);
        }
    }
}
