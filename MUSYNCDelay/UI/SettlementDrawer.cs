using System.Collections;
using System.Collections.Generic;
using MUSYNCDelay.Config;
using MUSYNCDelay.Data;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace MUSYNCDelay.UI
{
    /// <summary>
    /// 11.1-11.11 + 12.1-12.4 结算抽屉 UGUI
    /// 耳朵 + 抽屉面板 + 动态分页 + 校准提示 + 断开态
    /// </summary>
    public class SettlementDrawer : MonoBehaviour,
        IPointerDownHandler, IPointerUpHandler, IDragHandler,
        IBeginDragHandler, IEndDragHandler
    {
        private static SettlementDrawer _instance;

        // 耳朵
        private RectTransform _earRt;
        private Image _earImage;

        // 抽屉面板
        private GameObject _panel;
        private RectTransform _panelRt;

        // 分页
        private int _currentPage;
        private List<Texture2D> _chartTextures = new List<Texture2D>();
        private RawImage _chartImage;
        private Text _pageText;
        private Text _statsText;
        private Text _calText;
        private Text _emptyText;

        // 状态
        private bool _isOpen;
        private bool _isSettlement;

        // 手势
        private Vector2 _pointerDownPos;
        private float _pointerDownTime;
        private bool _isDragging;
        private Coroutine _holdCoroutine;

        // 视觉反馈
        private Color _earNormal = new Color(0.8f, 0.2f, 0.2f, 0.7f);
        private Color _earHold = new Color(1f, 0.4f, 0.4f, 0.9f);

        public static void Create(Transform parent)
        {
            var go = new GameObject("SettlementDrawer");
            go.transform.SetParent(parent, false);
            _instance = go.AddComponent<SettlementDrawer>();
            _instance.Setup();
        }

        public static void SetVisible(bool visible)
        {
            if (_instance == null) return;
            _instance._isSettlement = visible;
            _instance.gameObject.SetActive(visible);
            if (visible) _instance.OnSettlementEnter();
        }

        private void Setup()
        {
            var rt = GetComponent<RectTransform>();
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;

            // 耳朵 Button
            var earGo = new GameObject("Ear");
            earGo.transform.SetParent(transform, false);
            _earRt = earGo.AddComponent<RectTransform>();
            _earRt.sizeDelta = new Vector2(24, 60);
            _earImage = earGo.AddComponent<Image>();
            _earImage.color = _earNormal;
            _earImage.raycastTarget = true;
            PositionEar();

            // 抽屉面板
            _panel = new GameObject("Panel");
            _panel.transform.SetParent(transform, false);
            _panelRt = _panel.AddComponent<RectTransform>();
            _panelRt.anchorMin = new Vector2(1, 0);
            _panelRt.anchorMax = new Vector2(1, 1);
            _panelRt.pivot = new Vector2(1, 0.5f);
            var panelImg = _panel.AddComponent<Image>();
            panelImg.color = new Color(0.1f, 0.1f, 0.1f, 0.85f);
            panelImg.raycastTarget = true;

            // 面板内容
            var contentGo = new GameObject("Content");
            contentGo.transform.SetParent(_panel.transform, false);
            var contentRt = contentGo.AddComponent<RectTransform>();
            contentRt.anchorMin = Vector2.zero;
            contentRt.anchorMax = Vector2.one;
            contentRt.offsetMin = new Vector2(10, 10);
            contentRt.offsetMax = new Vector2(-10, -10);

            // 统计文本
            var statsGo = new GameObject("StatsText");
            statsGo.transform.SetParent(contentGo.transform, false);
            _statsText = statsGo.AddComponent<Text>();
            _statsText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            _statsText.fontSize = 18;
            _statsText.color = Color.white;
            _statsText.raycastTarget = false;
            var statsRt = _statsText.rectTransform;
            statsRt.anchorMin = new Vector2(0, 0.7f);
            statsRt.anchorMax = new Vector2(1, 1);
            statsRt.offsetMin = Vector2.zero;
            statsRt.offsetMax = Vector2.zero;

            // 校准提示
            var calGo = new GameObject("CalText");
            calGo.transform.SetParent(contentGo.transform, false);
            _calText = calGo.AddComponent<Text>();
            _calText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            _calText.fontSize = 16;
            _calText.color = new Color(1f, 0.9f, 0.3f);
            _calText.raycastTarget = false;
            var calRt = _calText.rectTransform;
            calRt.anchorMin = new Vector2(0, 0.55f);
            calRt.anchorMax = new Vector2(1, 0.7f);
            calRt.offsetMin = Vector2.zero;
            calRt.offsetMax = Vector2.zero;

            // 图表 RawImage
            var chartGo = new GameObject("ChartImage");
            chartGo.transform.SetParent(contentGo.transform, false);
            _chartImage = chartGo.AddComponent<RawImage>();
            _chartImage.raycastTarget = false;
            var chartRt = _chartImage.rectTransform;
            chartRt.anchorMin = new Vector2(0, 0.08f);
            chartRt.anchorMax = new Vector2(1, 0.55f);
            chartRt.offsetMin = Vector2.zero;
            chartRt.offsetMax = Vector2.zero;

            // 分页文本
            var pageGo = new GameObject("PageText");
            pageGo.transform.SetParent(contentGo.transform, false);
            _pageText = pageGo.AddComponent<Text>();
            _pageText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            _pageText.fontSize = 14;
            _pageText.color = Color.gray;
            _pageText.alignment = TextAnchor.MiddleCenter;
            _pageText.raycastTarget = false;
            var pageRt = _pageText.rectTransform;
            pageRt.anchorMin = new Vector2(0, 0);
            pageRt.anchorMax = new Vector2(1, 0.08f);
            pageRt.offsetMin = Vector2.zero;
            pageRt.offsetMax = Vector2.zero;

            // 空状态文本
            var emptyGo = new GameObject("EmptyText");
            emptyGo.transform.SetParent(contentGo.transform, false);
            _emptyText = emptyGo.AddComponent<Text>();
            _emptyText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            _emptyText.fontSize = 16;
            _emptyText.color = Color.gray;
            _emptyText.alignment = TextAnchor.MiddleCenter;
            _emptyText.raycastTarget = false;
            var emptyRt = _emptyText.rectTransform;
            emptyRt.anchorMin = Vector2.zero;
            emptyRt.anchorMax = Vector2.one;
            emptyRt.offsetMin = Vector2.zero;
            emptyRt.offsetMax = Vector2.zero;

            // 初始隐藏面板
            _panel.SetActive(false);
            gameObject.SetActive(false);
        }

        private void PositionEar()
        {
            var cfg = Plugin.Config.drawer.ear;
            float screenH = Screen.height;
            float yPos = -(cfg.y * screenH);
            if (cfg.side == "left")
            {
                _earRt.anchorMin = new Vector2(0, 1);
                _earRt.anchorMax = new Vector2(0, 1);
                _earRt.pivot = new Vector2(0, 0.5f);
                _earRt.anchoredPosition = new Vector2(0, yPos);
            }
            else
            {
                _earRt.anchorMin = new Vector2(1, 1);
                _earRt.anchorMax = new Vector2(1, 1);
                _earRt.pivot = new Vector2(1, 0.5f);
                _earRt.anchoredPosition = new Vector2(0, yPos);
            }
        }

        private void OnSettlementEnter()
        {
            _isOpen = false;
            _panel.SetActive(false);
            _currentPage = 0;
            _chartTextures.Clear();

            // 11.9 读缓存
            var result = SettleCache.Result;
            if (result != null && result.charts != null)
            {
                foreach (var chart in result.charts)
                {
                    if (chart.pngBytes != null && chart.pngBytes.Length > 0)
                    {
                        var tex = new Texture2D(2, 2);
                        tex.LoadImage(chart.pngBytes);
                        _chartTextures.Add(tex);
                    }
                }
            }
        }

        private void Update()
        {
            if (!_isSettlement) return;

            // 11.9 轮询刷新（缓存可能在后台线程延迟到达）
            if (_isOpen && _chartTextures.Count == 0)
            {
                var result = SettleCache.Result;
                if (result != null && result.charts != null && result.charts.Count > 0)
                {
                    OnSettlementEnter(); // 重新加载
                    RefreshPage();
                }
            }
        }

        private void ToggleDrawer()
        {
            _isOpen = !_isOpen;
            _panel.SetActive(_isOpen);
            if (_isOpen)
            {
                // 设置宽度
                float w = Screen.width * Plugin.Config.drawer.width_ratio;
                _panelRt.sizeDelta = new Vector2(w, 0);
                RefreshPage();
            }
        }

        private void RefreshPage()
        {
            var result = SettleCache.Result;

            // 11.10 断开态
            if (!SettleCache.Connected || result == null)
            {
                _statsText.text = "";
                _calText.text = "";
                _chartImage.texture = null;
                _pageText.text = "";
                _emptyText.gameObject.SetActive(true);
                _emptyText.text = "分析服务未连接\n请启动 MUSYNCSavDecode 工具\n端口: " + Plugin.Config.network.port;
                return;
            }

            _emptyText.gameObject.SetActive(false);

            // 11.7 首页统计文本
            if (result.stats != null)
            {
                var s = result.stats;
                _statsText.text = string.Format(
                    "Avg: {0:+0.0;-0.0;0.0} ms  Std: {1:F1}\nEX:{2} EXACT:{3} GREAT:{4} RIGHT:{5} MISS:{6}\nCombo: {7}",
                    s.avg, s.std, s.totalEx, s.totalExact, s.totalGreat, s.totalRight, s.totalMiss, s.totalCombo);
            }

            // 11.8 校准提示
            if (result.stats != null)
            {
                var s = result.stats;
                if (s.calibrated)
                {
                    _calText.text = "已校准，无需调整";
                }
                else
                {
                    string dir = s.calDir > 0 ? "+" : "-";
                    _calText.text = string.Format("建议：向 {0} 方向调整 {1:F0}~{2:F0} ms", dir, s.calLo, s.calHi);
                }
            }

            // 11.5-11.6 分页图表
            if (_chartTextures.Count > 0)
            {
                if (_currentPage >= _chartTextures.Count) _currentPage = 0;
                _chartImage.texture = _chartTextures[_currentPage];
                _pageText.text = string.Format("< {0}/{1} >", _currentPage + 1, _chartTextures.Count);
            }
            else
            {
                _chartImage.texture = null;
                _pageText.text = "";
            }
        }

        // ---- 耳朵手势 (12.1-12.3) ----

        public void OnPointerDown(PointerEventData e)
        {
            _pointerDownPos = e.position;
            _pointerDownTime = Time.unscaledTime;
            _isDragging = false;
            _holdCoroutine = StartCoroutine(HoldMonitor());
        }

        public void OnBeginDrag(PointerEventData e) { }

        public void OnDrag(PointerEventData e)
        {
            float dist = Vector2.Distance(e.position, _pointerDownPos);
            if (dist > Plugin.Config.gesture.drag_distance_px)
            {
                _isDragging = true;
                if (_holdCoroutine != null) { StopCoroutine(_holdCoroutine); _holdCoroutine = null; }

                if (_isOpen)
                {
                    // 12.1 展开态横向拖 = 改宽
                    float delta = e.delta.x;
                    if (Plugin.Config.drawer.ear.side == "right") delta = -delta;
                    float curW = _panelRt.sizeDelta.x;
                    float minW = Screen.width * Plugin.Config.drawer.min_width_ratio;
                    float maxW = Screen.width * Plugin.Config.drawer.max_width_ratio;
                    float newW = Mathf.Clamp(curW + delta, minW, maxW);
                    _panelRt.sizeDelta = new Vector2(newW, _panelRt.sizeDelta.y);
                }
                else
                {
                    // 12.1 收起态拖 = 垂直移位
                    var pos = _earRt.anchoredPosition;
                    pos.y += e.delta.y;
                    _earRt.anchoredPosition = pos;
                }
            }
        }

        public void OnEndDrag(PointerEventData e)
        {
            if (_holdCoroutine != null) { StopCoroutine(_holdCoroutine); _holdCoroutine = null; }
            ResetVisualFeedback();

            if (_isDragging)
            {
                if (_isOpen)
                {
                    // 12.4 持久化宽度
                    Plugin.Config.drawer.width_ratio = _panelRt.sizeDelta.x / Screen.width;
                }
                else
                {
                    // 12.3 吸附
                    float screenMid = Screen.width * 0.5f;
                    float earX = _earRt.position.x;
                    Plugin.Config.drawer.ear.side = earX < screenMid ? "left" : "right";
                    float normY = -_earRt.anchoredPosition.y / Screen.height;
                    Plugin.Config.drawer.ear.y = Mathf.Clamp01(normY);
                    PositionEar();
                }
                ConfigManager.MarkDirty();
            }
        }

        public void OnPointerUp(PointerEventData e)
        {
            if (_holdCoroutine != null) { StopCoroutine(_holdCoroutine); _holdCoroutine = null; }
            ResetVisualFeedback();

            if (!_isDragging)
            {
                float dist = Vector2.Distance(e.position, _pointerDownPos);
                float hold = (Time.unscaledTime - _pointerDownTime) * 1000f;
                if (dist <= Plugin.Config.gesture.drag_distance_px &&
                    hold <= Plugin.Config.gesture.hold_ms)
                {
                    // click → 切换展开/收起
                    ToggleDrawer();
                }
                // else: 犹豫态 — 吞掉
            }
        }

        private IEnumerator HoldMonitor()
        {
            yield return new WaitForSecondsRealtime(Plugin.Config.gesture.hold_ms / 1000f);
            if (!_isDragging && _earImage != null)
                _earImage.color = _earHold;
        }

        private void ResetVisualFeedback()
        {
            if (_earImage != null) _earImage.color = _earNormal;
        }
    }
}
