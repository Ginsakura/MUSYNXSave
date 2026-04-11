import tkinter as tk

class Tooltip:
    """
    Tkinter 悬停提示框 (Tooltip) 封装类
    可以绑定到任何 Tkinter 控件 (Frame, Button, Label 等)
    """
    def __init__(self, widget, text_func, ):
        self.widget = widget
        self.text_func = text_func  # 传入一个函数，这样可以每次悬停时动态获取最新的统计数据
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

        # 绑定鼠标进入和离开事件
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        """鼠标进入控件时触发，增加一个微小的延迟防止闪烁"""
        self.schedule()

    def _on_leave(self, event=None):
        """鼠标离开时销毁提示框"""
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        self.unschedule()
        # 延迟 400 毫秒显示，这是现代 UI 的标准做法，避免鼠标划过时弹出一屏幕框
        self.id = self.widget.after(100, self.show_tip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show_tip(self, event=None):
        if self.tip_window or not self.text_func:
            return

        text = self.text_func() if callable(self.text_func) else self.text_func

        # 1. 先创建隐藏的 Toplevel 和 Label
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)

        label = tk.Label(
            tw, text=text, justify='center',   # 如果是多行，建议居中对齐
            background="#F5F5F5",              # 换个极客点的深色背景
            foreground="#0A0A0A",              # 浅色字体
            relief='groove',                   # 凹槽边框样式
            bd=2,                              # 边框宽度
            font=("LXGW WenKai Mono", "14", "normal"))
        label.pack(ipadx=8, ipady=6)

        # 让 Tkinter 立即计算出 Label 需要的真实宽度和高度，不等待主循环
        tw.update_idletasks()

        # 获取刚刚计算出的 Tooltip 实际宽度
        tip_width = tw.winfo_width()

        # 依靠鼠标来定位 Tooltip 的位置，确保它始终出现在鼠标附近
        # # 获取鼠标的实时绝对坐标
        # mouse_x = self.widget.winfo_pointerx()
        # mouse_y = self.widget.winfo_pointery()

        # # X坐标：鼠标当前X - (Tooltip宽度的一半) -> 实现完美水平居中
        # # Y坐标：鼠标当前Y + 20像素的安全距离 -> 放在鼠标正下方
        # x = int(mouse_x - (tip_width / 2))
        # y = int(mouse_y + 20)  # 保持 20 像素 Y 轴偏移，防止鼠标直接贴到框上触发 Leave 事件

        # 依靠Frame控件来定位Tooltip的位置，确保它始终出现在Frame附近
        # 获取目标 Frame 在屏幕上的绝对起始坐标 (左上角)
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()

        # 获取目标 Frame 的实际宽度和高度
        widget_width = self.widget.winfo_width()
        widget_height = self.widget.winfo_height()

        # X坐标计算：
        # widget_x + (widget_width / 2)   -> 先找到 Frame 的水平中心点
        # - (tip_width / 2)               -> 然后向左偏移 Tooltip 宽度的一半，实现完美居中对齐
        x = int(widget_x + (widget_width / 2) - (tip_width / 2))

        # Y坐标计算：
        # widget_y + widget_height        -> 刚好落在 Frame 的下边线上
        # + 5                             -> 增加 5 像素的微小间距，看起来不那么拥挤 (类似下拉菜单)
        y = int(widget_y + widget_height + 5)

        # 设定最终计算好的几何位置，并将窗口真正推送到屏幕上
        tw.wm_geometry(f"+{x}+{y}")

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
