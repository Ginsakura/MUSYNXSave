using BMSLib;
using HarmonyLib;
using MUSYNCDelay.Data;
using MUSYNCDelay.Util;
using UnityEngine;

namespace MUSYNCDelay.Patches
{
    /// <summary>
    /// Patch 1: 实时延迟采集 (GetJudgeGrade Postfix)
    /// Patch 2: 新一局重置 (Reset Postfix)
    /// </summary>
    [HarmonyPatch(typeof(JudgeGrade))]
    public static class JudgeGradePatch
    {
        // 4.3 异常隔离：整体 try-catch，绝不向游戏抛异常
        [HarmonyPatch("GetJudgeGrade")]
        [HarmonyPostfix]
        public static void GetJudgeGradePostfix(long knockDistance)
        {
            try
            {
                // 5.1 算 ms → 查表得颜色 → 存当前值 → 追加 hits
                float ms = GradeColor.ToMs(knockDistance);
                Color color = GradeColor.Get(knockDistance);
                SessionData.SetCurrent(ms, color);
                SessionData.AddHit(knockDistance);

                // 标记 overlay 文本脏（由 OverlayCanvas 的 Update 检测并 SetText）
                UI.DelayOverlay.MarkDirty();
            }
            catch (System.Exception ex)
            {
                Plugin.Logger?.LogError($"JudgeGradePostfix error: {ex.Message}");
            }
        }

        // 5.2 Reset Postfix：清空本局数据 + 重置 overlay
        [HarmonyPatch("Reset")]
        [HarmonyPostfix]
        public static void ResetPostfix()
        {
            try
            {
                SessionData.Reset();
                UI.DelayOverlay.MarkDirty();
            }
            catch (System.Exception ex)
            {
                Plugin.Logger?.LogError($"ResetPostfix error: {ex.Message}");
            }
        }
    }
}
