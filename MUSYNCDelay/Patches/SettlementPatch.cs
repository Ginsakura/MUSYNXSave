using HarmonyLib;
using MUSYNCDelay.UI;
using UnityEngine;

namespace MUSYNCDelay.Patches
{
    /// <summary>
    /// Patch 4: 结算界面 UI 注入
    /// 同时 patch SettlementController.Start 和 NewSettlementController.Start
    /// 用 flag 防重复注入
    /// </summary>
    public static class SettlementPatch
    {
        private static bool _injected;

        [HarmonyPatch(typeof(SettlementController), "Start")]
        [HarmonyPostfix]
        public static void SettlementStartPostfix()
        {
            InjectOnce();
        }

        [HarmonyPatch(typeof(NewSettlementController), "Start")]
        [HarmonyPostfix]
        public static void NewSettlementStartPostfix()
        {
            InjectOnce();
        }

        private static void InjectOnce()
        {
            try
            {
                if (_injected) return;
                _injected = true;

                // 确保 Overlay Canvas 存在并切换到结算模式
                OverlayCanvas.EnsureCreated();
                OverlayCanvas.UpdateVisibility();
            }
            catch (System.Exception ex)
            {
                Plugin.Logger?.LogError($"SettlementPatch error: {ex.Message}");
            }
        }

        /// <summary>
        /// 在场景切换时重置注入标志（由 OverlayCanvas 的显隐控制调用）
        /// </summary>
        public static void ResetInjectionFlag()
        {
            _injected = false;
        }
    }
}
