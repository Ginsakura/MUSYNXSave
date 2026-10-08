using System.Collections.Generic;
using System.Threading;
using HarmonyLib;
using MUSYNCDelay.Data;
using MUSYNCDelay.Net;

namespace MUSYNCDelay.Patches
{
    /// <summary>
    /// Patch 3: 结算数据收集 + 后台 Socket 发送
    /// 主线程仅做 snapshot + 启动后台线程，绝不阻塞主线程
    /// </summary>
    [HarmonyPatch(typeof(SongInfoCore))]
    public static class SongInfoCorePatch
    {
        [HarmonyPatch("UpdateSync")]
        [HarmonyPostfix]
        public static void UpdateSyncPostfix(SongInfoCore __instance, int maxCombo)
        {
            try
            {
                // 9.1 snapshot 所有数据（主线程，<1ms）
                var snapshot = new SettleSnapshot
                {
                    songId = __instance.SongId,
                    maxComboThis = __instance.MaxComboThis,
                    syncNumberThis = __instance.SyncNumberThis,
                    newRecordThis = __instance.NewRecordThis,
                    totalEx = BMSLib.JudgeGrade.TotalEx,
                    totalExact = BMSLib.JudgeGrade.TotalExact,
                    totalGreat = BMSLib.JudgeGrade.TotalGreat,
                    totalRight = BMSLib.JudgeGrade.TotalRight,
                    totalMiss = BMSLib.JudgeGrade.TotalMiss,
                    totalCombo = BMSLib.JudgeGrade.TotalCombo,
                    hits = new List<long>(SessionData.GetHitsSnapshot())
                };

                // 9.2 启动后台线程，主线程立即返回
                ThreadPool.QueueUserWorkItem(_ =>
                {
                    try
                    {
                        // 9.3 后台线程：序列化 → Socket 发送 → 写缓存
                        SettleCache.SetConnected(false);
                        var result = SocketClient.SendSettle(snapshot);
                        if (result != null)
                        {
                            SettleCache.SetResult(result);
                            SettleCache.SetConnected(true);
                        }
                    }
                    catch (System.Exception ex)
                    {
                        Plugin.Logger?.LogWarning($"Settle background task error: {ex.Message}");
                        SettleCache.SetConnected(false);
                    }
                });
            }
            catch (System.Exception ex)
            {
                // 9.4 整体 try-catch：失败仅日志
                Plugin.Logger?.LogError($"UpdateSyncPostfix error: {ex.Message}");
            }
        }
    }

    /// <summary>结算数据快照（主线程创建，传给后台线程）</summary>
    public class SettleSnapshot
    {
        public int songId;
        public int maxComboThis;
        public int syncNumberThis;
        public bool newRecordThis;
        public int totalEx;
        public int totalExact;
        public int totalGreat;
        public int totalRight;
        public int totalMiss;
        public int totalCombo;
        public List<long> hits;
    }
}
