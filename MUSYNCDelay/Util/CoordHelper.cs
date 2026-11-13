using UnityEngine;

namespace MUSYNCDelay.Util
{
    /// <summary>
    /// 3.3 坐标归一化 ↔ RectTransform 锚点位置换算
    /// 约定：y=0 顶、y=1 底；x=0 左、x=1 右；rect 的 (x,y) 为框左上角
    /// </summary>
    public static class CoordHelper
    {
        /// <summary>
        /// 将归一化 rect (x,y,w,h) 应用到 RectTransform。
        /// 锚点设为左上 (0,1)，pivot 设为左上 (0,1)，
        /// 然后 anchoredPosition 根据归一化坐标换算。
        /// </summary>
        public static void ApplyNormalizedRect(RectTransform rt, Config.RectConfig rect)
        {
            var canvas = rt.GetComponentInParent<Canvas>();
            if (canvas == null) return;
            var canvasRect = canvas.GetComponent<RectTransform>();
            float cw = canvasRect.rect.width;
            float ch = canvasRect.rect.height;

            rt.anchorMin = new Vector2(0f, 1f);
            rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);

            // 归一化 y=0 顶 → UGUI anchoredPosition.y=0 也是顶（因为 anchor 在左上）
            rt.anchoredPosition = new Vector2(rect.x * cw, -(rect.y * ch));
            rt.sizeDelta = new Vector2(rect.w * cw, rect.h * ch);
        }

        /// <summary>
        /// 从 RectTransform 当前状态读回归一化 rect，用于持久化
        /// </summary>
        public static Config.RectConfig ReadNormalizedRect(RectTransform rt)
        {
            var canvas = rt.GetComponentInParent<Canvas>();
            if (canvas == null) return new Config.RectConfig();
            var canvasRect = canvas.GetComponent<RectTransform>();
            float cw = canvasRect.rect.width;
            float ch = canvasRect.rect.height;
            if (cw <= 0 || ch <= 0) return new Config.RectConfig();

            return new Config.RectConfig
            {
                x = rt.anchoredPosition.x / cw,
                y = -rt.anchoredPosition.y / ch,
                w = rt.sizeDelta.x / cw,
                h = rt.sizeDelta.y / ch
            };
        }
    }
}
