using MUSYNCDelay.Config;
using MUSYNCDelay.Data;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace MUSYNCDelay.UI
{
    /// <summary>
    /// 6.1-6.4 UGUI 基础设施 — DontDestroyOnLoad Overlay Canvas
    /// </summary>
    public static class OverlayCanvas
    {
        private static Canvas _canvas;
        private static GameObject _root;

        public static Canvas Canvas { get { return _canvas; } }
        public static GameObject Root { get { return _root; } }

        public static void EnsureCreated()
        {
            if (_root != null) return;

            _root = new GameObject("MUSYNCDelay_Overlay");
            Object.DontDestroyOnLoad(_root);

            // 6.1 Canvas + GraphicRaycaster
            _canvas = _root.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 32767; // 高于游戏原生 Canvas
            _root.AddComponent<GraphicRaycaster>();

            // 6.2 EventSystem 兜底
            if (EventSystem.current == null)
            {
                var esGo = new GameObject("MUSYNCDelay_EventSystem");
                Object.DontDestroyOnLoad(esGo);
                esGo.AddComponent<EventSystem>();
                esGo.AddComponent<StandaloneInputModule>();
            }

            // 6.3 事件拦截红线：根节点无 Image 组件，不会拦截事件
            // （Canvas 本身不拦截，只有带 RaycastTarget=true 的 Graphic 才拦截）

            // 创建子组件
            DelayOverlay.Create(_root.transform);
            SettlementDrawer.Create(_root.transform);

            // 6.4 初始显隐
            UpdateVisibility();
        }

        /// <summary>6.4 按场景/状态切换显隐</summary>
        public static void UpdateVisibility()
        {
            if (_root == null) return;
            // delay overlay 在游玩场景显示，结算场景隐藏
            // 抽屉在结算场景显示，游玩场景隐藏
            // 简化判断：通过场景名或全局标志
            string sceneName = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name;
            bool isSettlement = sceneName != null &&
                (sceneName.Contains("Settlement") || sceneName.Contains("settlement") ||
                 sceneName.Contains("Result") || sceneName.Contains("result"));

            DelayOverlay.SetVisible(!isSettlement && Plugin.Config.delay_overlay.enabled);
            SettlementDrawer.SetVisible(isSettlement);
        }
    }
}
