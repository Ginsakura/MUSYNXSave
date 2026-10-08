using MUSYNCDelay.Config;
using MUSYNCDelay.Data;
using MUSYNCDelay.Util;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace MUSYNCDelay.UI
{
    /// <summary>
    /// 7.1-7.7 delay overlay — 单行 UGUI 文本框
    /// 可拖拽/缩放/持久化，事件穿透不拦游戏判定
    /// </summary>
    public class DelayOverlay : MonoBehaviour,
        IPointerDownHandler, IPointerUpHandler, IDragHandler,
        IBeginDragHandler, IEndDragHandler
    {
        private static DelayOverlay _instance;
        private static bool _dirty;

        private RectTransform _rt;
        private Text _text;
        private RectTransform _titleBar;
        private RectTransform _resizeHandle;

        // 三态手势
        private Vector2 _pointerDownPos;
        private float _pointerDownTime;
        private bool _isDragging;
        private bool _isResizing;
        private Coroutine _holdCoroutine;

        // 视觉反馈
        private Image _bgImage;
        private Color _normalBgColor = new Color(0f, 0f, 0f, 0.5f);
        private Color _holdBgColor = new Color(0.2f, 0.2f, 0.2f, 0.7f);

        public static void MarkDirty() { _dirty = true; }

        public static void Create(Transform parent)
        {
            var go = new GameObject("DelayOverlay");
            go.transform.SetParent(parent, false);
            _instance = go.AddComponent<DelayOverlay>();
            _instance.Setup();
        }

        public static void SetVisible(bool visible)
        {
            if (_instance != null) _instance.gameObject.SetActive(visible);
        }

        private void Setup()
        {
            _rt = GetComponent<RectTransform>();

            // 7.1 布局：标题条 + 单行文本 + resize 手柄
            // 背景 Image — 7.2 RaycastTarget=false（不拦游戏判定）
            _bgImage = gameObject.AddComponent<Image>();
            _bgImage.color = _normalBgColor;
            _bgImage.raycastTarget = false; // 事件穿透！

            // 文本
            var textGo = new GameObject("Text");
            textGo.transform.SetParent(transform, false);
            _text = textGo.AddComponent<Text>();
            _text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            _text.fontSize = Plugin.Config.delay_overlay.font_size;
            _text.alignment = TextAnchor.MiddleCenter;
            _text.raycastTarget = false; // 事件穿透！
            var textRt = _text.rectTransform;
            textRt.anchorMin = Vector2.zero;
            textRt.anchorMax = Vector2.one;
            textRt.offsetMin = new Vector2(4, 2);
            textRt.offsetMax = new Vector2(-12, -2); // 右下角留给 resize 手柄

            // 标题条（拖拽手柄）— RaycastTarget=true
            var titleGo = new GameObject("TitleBar");
            titleGo.transform.SetParent(transform, false);
            _titleBar = titleGo.AddComponent<RectTransform>();
            _titleBar.anchorMin = new Vector2(0, 1);
            _titleBar.anchorMax = new Vector2(1, 1);
            _titleBar.pivot = new Vector2(0.5f, 1);
            _titleBar.anchoredPosition = Vector2.zero;
            _titleBar.sizeDelta = new Vector2(0, 6); // 6px 高的标题条
            var titleImg = titleGo.AddComponent<Image>();
            titleImg.color = new Color(0.3f, 0.3f, 0.3f, 0.3f);
            titleImg.raycastTarget = true; // 接收拖拽事件

            // resize 手柄 — RaycastTarget=true
            var resizeGo = new GameObject("ResizeHandle");
            resizeGo.transform.SetParent(transform, false);
            _resizeHandle = resizeGo.AddComponent<RectTransform>();
            _resizeHandle.anchorMin = new Vector2(1, 0);
            _resizeHandle.anchorMax = new Vector2(1, 0);
            _resizeHandle.pivot = new Vector2(1, 0);
            _resizeHandle.anchoredPosition = Vector2.zero;
            _resizeHandle.sizeDelta = new Vector2(12, 12);
            var resizeImg = resizeGo.AddComponent<Image>();
            resizeImg.color = new Color(0.5f, 0.5f, 0.5f, 0.5f);
            resizeImg.raycastTarget = true;

            // 7.7 应用默认位置
            CoordHelper.ApplyNormalizedRect(_rt, Plugin.Config.delay_overlay.rect);

            // 设置 alpha
            var cg = gameObject.AddComponent<CanvasGroup>();
            cg.alpha = Plugin.Config.delay_overlay.alpha;
        }

        private void Update()
        {
            // 脏标记驱动：仅打击时刷新文本，非每帧
            if (_dirty && _text != null)
            {
                _dirty = false;
                if (SessionData.HasCurrent)
                {
                    float ms = SessionData.CurrentDelayMs;
                    _text.text = (ms >= 0 ? "+" : "") + ms.ToString("F1");
                    _text.color = SessionData.CurrentColor;
                }
                else
                {
                    _text.text = "";
                }
            }
        }

        // ---- 三态手势 (7.5-7.6) ----

        public void OnPointerDown(PointerEventData e)
        {
            _pointerDownPos = e.position;
            _pointerDownTime = Time.unscaledTime;
            _isDragging = false;
            _isResizing = (e.pointerCurrentRaycast.gameObject == _resizeHandle.gameObject);

            // 启动 hold 监测协程
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

                if (_isResizing)
                {
                    // 7.4 resize
                    var delta = e.delta;
                    var sd = _rt.sizeDelta;
                    float newW = Mathf.Max(40, sd.x + delta.x);
                    float newH = Plugin.Config.delay_overlay.aspect_locked
                        ? newW * (sd.y / Mathf.Max(1, sd.x))
                        : Mathf.Max(20, sd.y - delta.y);
                    _rt.sizeDelta = new Vector2(newW, newH);
                }
                else
                {
                    // 7.3 拖拽移动
                    _rt.anchoredPosition += e.delta;
                }
            }
        }

        public void OnEndDrag(PointerEventData e)
        {
            if (_holdCoroutine != null) { StopCoroutine(_holdCoroutine); _holdCoroutine = null; }
            ResetVisualFeedback();

            if (_isDragging)
            {
                // 持久化
                Plugin.Config.delay_overlay.rect = CoordHelper.ReadNormalizedRect(_rt);
                ConfigManager.MarkDirty();
            }
            // else: click 或犹豫态 — 单行 overlay 无 click 语义，忽略
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
                    // click — 单行 overlay 暂无 click 语义
                }
                // else: 犹豫态 — 吞掉
            }
        }

        private System.Collections.IEnumerator HoldMonitor()
        {
            yield return new WaitForSecondsRealtime(Plugin.Config.gesture.hold_ms / 1000f);
            if (!_isDragging)
            {
                // 7.6 进入拖动模式视觉反馈
                if (_bgImage != null) _bgImage.color = _holdBgColor;
            }
        }

        private void ResetVisualFeedback()
        {
            if (_bgImage != null) _bgImage.color = _normalBgColor;
        }
    }
}
