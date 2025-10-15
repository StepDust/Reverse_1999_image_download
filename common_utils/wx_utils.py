import wx
import re
import os
import threading
import functools

import logging
from .logger_setup import ColorFormatter
import random

# 配置日志
logger = logging.getLogger(__name__)


class WxUtils:
    def __init__(
        self,
        wx_frame,
        config=None,
        row_height=30,
        text_width=250,
        label_width=120,
        btn_width=60,
        gap=20,
    ):

        self.wx_frame = wx_frame
        self.config = config
        self.is_test = False
        # 初始化布局参数
        self.row_height = row_height
        self.text_width = text_width
        self.label_width = label_width
        self.btn_width = btn_width
        self.gap = gap
        # 初始化文本控件列表
        self.text_ctrls = []
        self.btn_ctrls = []

        # 设置光标
        self.normal_cursor = wx.Cursor(wx.CURSOR_HAND)
        self.disabled_cursor = wx.Cursor(wx.CURSOR_NO_ENTRY)

    # region 控件创建

    def create_folder_ctrls(
        self,
        sizer,
        rows,
        parent=None,
        row_height=None,
        text_width=None,
        label_width=None,
        btn_width=None,
        gap=None,
    ):
        """
        创建多个文件夹选择控件。

        :param panel: 父面板
        :param main_sizer: 主布局器
        :param rows: 行配置列表，每个元素是一个字典，包含 'config_key', 'title' 等
        :param row_height: 行高
        :param text_width: 文本框宽度
        :param label_width: 标签宽度
        :param btn_width: 按钮宽度
        :param gap: 元素间距
        """

        # 初始化布局参数
        if row_height is None:
            row_height = self.row_height
        if text_width is None:
            text_width = self.text_width
        if label_width is None:
            label_width = self.label_width
        if btn_width is None:
            btn_width = self.btn_width
        if gap is None:
            gap = self.gap

        if parent is None:
            parent = sizer.GetContainingWindow()  # 获取 sizer 所在面板

        for row in rows:
            config_key = row.get("config_key", "").strip()
            title = row.get("title", "")
            text_ctrl, browse_btn = self.create_text_ctrl(
                sizer=sizer,
                row=row,
                parent=parent,
                btn_text="浏览",
                btn_event=None,
                row_height=row_height,
                text_width=text_width,
                label_width=label_width,
                btn_width=btn_width,
                gap=gap,
            )
            browse_btn.Bind(
                wx.EVT_BUTTON,
                lambda event, ctrl=text_ctrl, title=f"选择{title}", config_key=config_key: self.on_select_dir(
                    event=event, text_ctrl=ctrl, title=title, config_key=config_key
                ),
            )

    def create_file_ctrls(
        self,
        sizer,
        rows,
        parent=None,
        row_height=None,
        text_width=None,
        label_width=None,
        btn_width=None,
        gap=None,
    ):
        """
        创建多个文件选择控件。

        :param panel: 父面板
        :param main_sizer: 主布局器
        :param rows: 行配置列表，每个元素是一个字典，包含 'config_key', 'title' 等
        :param row_height: 行高
        :param text_width: 文本框宽度
        :param label_width: 标签宽度
        :param btn_width: 按钮宽度
        :param gap: 元素间距
        """

        # 初始化布局参数
        if row_height is None:
            row_height = self.row_height
        if text_width is None:
            text_width = self.text_width
        if label_width is None:
            label_width = self.label_width
        if btn_width is None:
            btn_width = self.btn_width
        if gap is None:
            gap = self.gap

        if parent is None:
            parent = sizer.GetContainingWindow()  # 获取 sizer 所在面板

        for row in rows:
            config_key = row.get("config_key", "").strip()
            title = row.get("title", "")
            text_ctrl, browse_btn = self.create_text_ctrl(
                sizer=sizer,
                row=row,
                btn_text="浏览",
                btn_event=None,
                parent=parent,
                row_height=row_height,
                text_width=text_width,
                label_width=label_width,
                btn_width=btn_width,
                gap=gap,
            )
            browse_btn.Bind(
                wx.EVT_BUTTON,
                lambda event, ctrl=text_ctrl, title=f"选择{title}", config_key=config_key, suffixs=row.get(
                    "suffixs", []
                ): self.on_select_file(
                    event=event,
                    text_ctrl=ctrl,
                    title=title,
                    config_key=config_key,
                    suffixs=suffixs,
                ),
            )

    def create_text_ctrl(
        self,
        sizer,
        row,
        parent=None,
        btn_text="",
        btn_event=None,
        row_height=None,
        text_width=None,
        label_width=None,
        btn_width=None,
        gap=None,
    ):
        """
        创建一个标签+文本框+按钮的行布局。

        :param panel: 父面板
        :param main_sizer: 主布局器
        :param row: 行配置字典，包含 'config_key', 'title' 等
        :param btn_text: 按钮文本
        :param btn_event: 按钮点击事件处理函数
        :param row_height: 行高
        :param text_width: 文本框宽度
        :param label_width: 标签宽度
        :param btn_width: 按钮宽度
        :param gap: 元素间距
        :return: 文本框和按钮的元组
        """

        # 初始化布局参数
        # 初始化参数
        if row_height is None:
            row_height = self.row_height
        if text_width is None:
            text_width = self.text_width
        if label_width is None:
            label_width = self.label_width
        if btn_width is None:
            btn_width = self.btn_width
        if gap is None:
            gap = self.gap
        if parent is None:
            parent = sizer.GetContainingWindow()  # 获取主面板

        name = row.get("name", "").strip()
        config_key = row.get("config_key", "").strip()
        title = row.get("title", "")
        if not name:
            name = config_key

        if not config_key and not name:
            wx.MessageBox(
                f"渲染文本框控件时【{title}】的config_key或name不能为空", "配置错误"
            )
            return

        # 创建行容器 Panel 并设置背景色
        row_panel = wx.Panel(parent, size=(-1, row_height))
        row_panel.SetBackgroundColour(self.get_test_color(parent))

        # 行水平布局
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_panel.SetSizer(row_sizer)

        # 标签
        label = wx.StaticText(row_panel, label=title, style=wx.ALIGN_RIGHT)
        label.SetMinSize((label_width, -1))
        row_sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, int(gap / 2))

        # 文本框
        text_ctrl = wx.TextCtrl(
            row_panel,
            size=(text_width, row_height),
            style=wx.TE_MULTILINE,
        )
        # 如果有配置文件且 config_key 不为空，从配置文件获取默认值
        if config_key.strip() and self.config:
            text_ctrl.SetValue(self.config.Read(config_key, ""))
        text_ctrl.Bind(
            wx.EVT_TEXT, lambda event: self.on_text_change(event, text_ctrl, config_key)
        )
        row_sizer.Add(text_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, gap)
        self.text_ctrls.append({"ctrl": text_ctrl, "name": name})

        # 按钮
        btn = None
        if btn_text:
            btn = wx.Button(row_panel, label=btn_text, size=(btn_width, row_height))
            btn.SetCursor(self.normal_cursor)
            if btn_event:
                btn.Bind(wx.EVT_BUTTON, btn_event)
            row_sizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL)
            self.btn_ctrls.append({"ctrl": btn, "name": name})

        # 添加行到主布局
        sizer.Add(row_panel, 0, wx.TOP | wx.EXPAND, gap)

        return text_ctrl, btn

    def create_hr(
        self, sizer, parent=None, gap=None, color=wx.Colour(47, 54, 60), border=0
    ):
        """
        在 sizer 中添加一条水平分割线，占据指定行高，并可设置背景色。
        :param sizer: 目标 sizer
        :param row_height: 分割线行高（控件高度）
        :param color: 分割线颜色
        :param bg_color: 背景颜色
        :param border: sizer 边距
        """
        if not gap:
            gap = self.gap
        if parent is None:
            parent = sizer.GetContainingWindow()  # 获取 sizer 所在面板

        # 创建行 Panel
        line_panel = wx.Panel(parent, size=(-1, gap))
        line_panel.SetBackgroundColour(self.get_test_color(parent))

        # 绘制细线
        def on_paint(event):
            dc = wx.PaintDC(line_panel)
            width, height = line_panel.GetSize()
            y = height - 1
            dc.SetPen(wx.Pen(color, 1))
            dc.DrawLine(0, y, width, y)

        line_panel.Bind(wx.EVT_PAINT, on_paint)
        sizer.Add(line_panel, 0, wx.EXPAND | wx.ALL, border)

    def create_run_btns(self, sizer, btn_group, parent=None, row_height=None, gap=None):
        """
        创建按钮，宽度略微拉伸以填满容器，固定高度，按钮之间间距固定
        """
        if not gap:
            gap = self.gap
        if not row_height:
            row_height = self.row_height
        if parent is None:
            parent = sizer.GetContainingWindow()

        btn_panel = wx.Panel(parent)
        btn_panel.SetBackgroundColour(wx.Colour(221, 221, 221))

        # 水平 BoxSizer
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        for idx, item in enumerate(btn_group):
            name = item.get("name", "").strip()
            if not name:
                name = item["title"]
            btn = wx.Button(btn_panel, label=item["title"], size=(-1, row_height))
            btn.SetCursor(self.normal_cursor)
            # 去掉边框
            btn.SetWindowStyleFlag(wx.BORDER_NONE)
            # 设置圆角
            btn.SetWindowStyle(wx.NO_BORDER)
            btn.Bind(wx.EVT_BUTTON, item["event"])
            self.btn_ctrls.append({"ctrl": btn, "name": name})

            # proportion=1 表示按钮会均分剩余空间，wx.EXPAND 保证填满
            # 每个按钮四周留 gap/2
            if idx < len(btn_group) - 1:
                btn_sizer.Add(btn, 1, wx.EXPAND | wx.RIGHT, gap // 2)
            else:
                btn_sizer.Add(btn, 1, wx.EXPAND | wx.RIGHT, 0)

        # 给按钮面板四周留 gap/2 内边距
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_sizer.Add(btn_sizer, 1, wx.EXPAND | wx.ALL, gap // 2)

        btn_panel.SetSizer(outer_sizer)

        # 添加到主 sizer 底部
        sizer.Add(btn_panel, 0, wx.EXPAND)

    # region 创建日志控件
    def create_log_ctrls(
        self,
        panel,
        main_sizer,
        row_height=None,
        text_width=None,
        label_width=None,
        btn_width=None,
        gap=None,
    ):
        """
        创建日志控件。

        :param panel: 父面板
        :param main_sizer: 主布局器
        :param row_height: 行高
        :param text_width: 文本框宽度
        :param label_width: 标签宽度
        :param btn_width: 按钮宽度
        :param gap: 元素间距
        """
        # 初始化布局参数
        if row_height is None:
            row_height = self.row_height
        if text_width is None:
            text_width = self.text_width
        if label_width is None:
            label_width = self.label_width
        if btn_width is None:
            btn_width = self.btn_width
        if gap is None:
            gap = self.gap

        # 第一行按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer(1)

        btn_open = wx.Button(panel, label="打开日志", size=(btn_width, row_height))
        btn_clear = wx.Button(panel, label="清空日志", size=(btn_width, row_height))
        btn_up = wx.Button(panel, label="向上翻页", size=(btn_width, row_height))
        btn_down = wx.Button(panel, label="向下翻页", size=(btn_width, row_height))

        btn_group = [btn_open, btn_clear, btn_up, btn_down]
        # 设置按钮样式
        for btn in btn_group:
            btn.SetBackgroundColour(wx.Colour(35, 41, 46))  # #23292e
            btn.SetForegroundColour(wx.Colour(247, 247, 247))
            # 去掉边框
            btn.SetWindowStyleFlag(wx.BORDER_NONE)
            # 设置圆角
            btn.SetWindowStyle(wx.NO_BORDER)
            # 添加左右边距
            btn.SetWindowVariant(wx.WINDOW_VARIANT_NORMAL)
            btn.SetMinSize((btn.GetSize().width + gap / 2, btn.GetSize().height))

        # 设置按钮间距
        for btn in btn_group:
            btn_sizer.Add(btn, 0, wx.TOP | wx.RIGHT, gap)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND)

        # 第二行 日志文本框
        self.log_text = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE
            | wx.TE_READONLY
            | wx.TE_RICH2
            | wx.NO_BORDER
            | wx.TE_NO_VSCROLL,
            size=(text_width, row_height * 10),  # 日志框高度设为按钮高度的10倍
        )
        # 设置背景色和边框色为#2f363c
        self.log_text.SetBackgroundColour(wx.Colour(47, 54, 60))  # #2f363c
        main_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, gap)
        # 去掉内边距
        self.log_text.SetMargins(0, 0)

        self.btn_hovering = False  # 鼠标悬浮标志
        # 鼠标进入/离开按钮
        self.log_text.Bind(wx.EVT_ENTER_WINDOW, self.on_btn_enter)
        self.log_text.Bind(wx.EVT_LEAVE_WINDOW, self.on_btn_leave)
        # 滚轮事件绑定到父窗口或者 frame
        self.log_text.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        # 绑定按钮事件
        btn_clear.Bind(wx.EVT_BUTTON, self.on_clear_log)
        btn_open.Bind(wx.EVT_BUTTON, self.on_open_log)
        btn_up.Bind(wx.EVT_BUTTON, self.on_up_log)
        btn_down.Bind(wx.EVT_BUTTON, self.on_down_log)

        # 绑定 logger
        wx_handler = WxLogHandler(self.log_text)
        wx_handler.setFormatter(ColorFormatter("%(asctime)s %(message)s"))

        logger = logging.getLogger()
        logger.addHandler(wx_handler)

    def on_btn_enter(self, event):
        self.btn_hovering = True
        event.Skip()

    def on_btn_leave(self, event):
        self.btn_hovering = False
        event.Skip()

    def on_mouse_wheel(self, event):
        if self.btn_hovering:
            rotation = event.GetWheelRotation()
            lines = rotation // event.GetWheelDelta() * event.GetLinesPerAction()
            # 滚动 txt 文本控件
            current_pos = self.log_text.GetScrollPos(wx.VERTICAL)
            self.log_text.ScrollLines(-lines)  # wx TextCtrl 中向上滚动是负数
        event.Skip()

    def on_clear_log(self, event):
        self.log_text.Clear()

    def on_open_log(self, event):
        log_file = logger.log_path()
        if log_file:
            os.startfile(log_file)

    def on_up_log(self, event):
        self.log_text.ScrollPages(-1)  # 向上一页

    def on_down_log(self, event):
        # 向下滚动一页
        self.log_text.ScrollPages(1)  # 向下一页

    # endregion

    # endregion

    # region 事件处理

    def on_text_change(self, event, text_ctrl, config_key):
        """
        文本框内容改变事件处理函数。

        :param event: 事件对象
        :param text_ctrl: 文本框控件
        :param config_key: 配置键，用于保存文本框内容
        """
        if config_key.strip() and self.config:
            self.config.Write(config_key, text_ctrl.GetValue())
            self.config.Flush()

    def on_select_dir(self, event, text_ctrl, title, config_key):
        """
        浏览文件夹事件处理函数。

        :param event: 事件对象
        :param text_ctrl: 文本框控件
        :param title: 对话框标题
        :param config_key: 配置键，用于保存选择的路径
        """
        dlg = wx.DirDialog(self.wx_frame, title, style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            text_ctrl.SetValue(dlg.GetPath())
            # 保存到配置文件
            if config_key.strip() and self.config:
                self.config.Write(config_key, dlg.GetPath())
                self.config.Flush()  # 使用 Flush() 保存，不要调用 Save()
        dlg.Destroy()

    def on_select_file(self, event, suffixs, text_ctrl, title, config_key):
        """
        浏览文件事件处理函数。

        :param event: 事件对象
        :param text_ctrl: 文本框控件
        :param suffixs: 文件后缀
        :param title: 对话框标题
        :param config_key: 配置键，用于保存选择的路径
        """
        # 构建文件类型过滤器
        wildcard = "所有文件 (*.*)|*.*"
        if suffixs and isinstance(suffixs, str):
            suffixs = [suffixs]

        if suffixs and isinstance(suffixs, list):
            filters = []
            for suffix in suffixs:
                suffix = suffix.strip()
                if suffix:
                    # 去掉前面的点号(如果有)
                    suffix = suffix.lstrip(".")
                    filters.append(f"*.{suffix}")
            if filters:
                wildcard = f"支持的文件 ({', '.join(filters)})|{';'.join(filters)}"

        dlg = wx.FileDialog(
            self.wx_frame,
            title,
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        )

        if dlg.ShowModal() == wx.ID_OK:
            text_ctrl.SetValue(dlg.GetPath())
            # 保存到配置文件
            if config_key.strip() and self.config:
                self.config.Write(config_key, dlg.GetPath())
                self.config.Flush()  # 使用 Flush() 保存，不要调用 Save()
        dlg.Destroy()

    # endregion

    # region 工具函数

    def get_test_color(self, panel, is_test=None):
        """返回随机颜色,非测试模式返回透明色"""
        if not is_test:
            is_test = self.is_test
        if is_test:
            # 随机生成RGB三个通道的值
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            return wx.Colour(r, g, b)
        # 非测试模式返回默认颜色
        return panel.GetBackgroundColour()

    def get_text_ctrl(self, name):
        """
        获取指定配置键的文本框控件。

        :param config_key: 配置键
        :return: 文本框控件
        """
        for item in self.text_ctrls:
            if item["name"] == name:
                return item["ctrl"]
        return None

    def get_btn_ctrl(self, name):
        """
        获取指定配置键的按钮控件。

        :param config_key: 配置键
        :return: 按钮控件
        """
        for item in self.btn_ctrls:
            if item["name"] == name:
                return item["ctrl"]
        return None

    def toggle_btn(self, label, name=None, btn=None):
        """
        切换按钮状态
        :param btn: 按钮控件
        :param name: 按钮名字
        """
        if btn is None and (name is None or name.strip() == ""):
            logger.error("切换按钮状态失败，name和btn至少有一个有值")
            return

        if btn is None:
            btn = self.get_btn_ctrl(name=name)

        if btn is None:
            logger.error(f"未找到 name = {name} 的按钮")
            return

        # 获取当前状态
        is_enabled = getattr(btn, "_disabled_simulate", False)

        # 设置标签
        btn.SetLabel(label)

        btn.SetCursor(self.disabled_cursor if not is_enabled else self.normal_cursor)
        btn._disabled_simulate = not is_enabled
        btn.Refresh()

    @staticmethod
    def run_in_thread(func):
        """
        装饰器：让函数自动在子线程中运行
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            thread = threading.Thread(
                target=functools.partial(func, *args, **kwargs), daemon=True
            )
            thread.start()
            return thread

        return wrapper

    @staticmethod
    def copy_to_clipboard(content):
        """
        复制内容到剪贴板
        :param content: 要复制的内容
        """
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(str(content)))
            wx.TheClipboard.Close()
            return True
        return False

    @staticmethod
    def custom_alert(
        title,
        msg,
        close_time=0,
        position_x=0,
        position_y=0,
        btn_group=None,
        initial="左上",
    ):
        """
        自定义弹窗：支持初始点（initial）四象限参考，position_left/position_top为对应角的相对偏移
        :param title: 弹窗标题 str
        :param msg: 弹窗内容 str
        :param close_time: 自动关闭，单位秒
        :param position_x: X轴偏移量（int，正负均可，和initial结合）
        :param position_y: Y轴偏移量（int，正负均可，和initial结合）
        :param btn_group: 按钮文本 list
        :param initial: 定位参考点，可选值["左上", "右上", "左下", "右下"]，默认为"左上"
        :return: 按钮文本或"自动关闭"
        """

        # region 使用示例
        # result = WxUtils.custom_alert(
        #         "提示111",
        #         "这是一个基本的梵蒂冈\n变化幅度和提示框",
        #         0,
        #         "auto",
        #         "100",
        #         [],
        #         "右上",
        #     )
        #     print(f"基础用法结果: {result}")
        # endregion

        dlg = MiniLayerAlert(
            title, msg, close_time, position_x, position_y, btn_group, initial
        )
        dlg.ShowModal()
        dlg.Destroy()  # 必须销毁！
        return getattr(dlg, "result", None)

    # endregion


# region 弹窗类


class MiniLayerAlert(wx.Dialog):
    def __init__(self, title, msg, close_time, pos_x, pos_y, btn_group, initial):
        super().__init__(
            None, title=title, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        )
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bitmap = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (32, 32))
        icon = wx.StaticBitmap(panel, bitmap=bitmap)
        top_sizer.Add(icon, 0, wx.LEFT | wx.TOP, 20)
        self.SetIcon(wx.ArtProvider.GetIcon(wx.ART_FILE_SAVE, wx.ART_FRAME_ICON))
        message_text = wx.StaticText(panel, label=msg)
        font = message_text.GetFont()
        font.SetPointSize(10)
        message_text.SetFont(font)
        top_sizer.Add(message_text, 1, wx.LEFT | wx.TOP | wx.RIGHT, 20)
        main_sizer.Add(top_sizer, 1, wx.EXPAND)
        line = wx.StaticLine(panel, style=wx.LI_HORIZONTAL)
        main_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.countdown_label = wx.StaticText(panel, label="")
        button_sizer.Add(
            self.countdown_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20
        )
        button_sizer.AddStretchSpacer()
        self.btn_map = {}
        for idx, label in enumerate(btn_group or ["确定"]):
            btn = wx.Button(panel, id=10000 + idx, label=label)
            btn.SetBackgroundColour(wx.Colour(230, 230, 230))
            btn.Bind(wx.EVT_BUTTON, self.on_button)
            button_sizer.Add(btn, 0, wx.LEFT, 10)
            self.btn_map[btn.GetId()] = label
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 20)
        panel.SetSizer(main_sizer)
        self.SetMinSize(wx.Size(600, 225))
        self.SetSize(600, 225)
        display_size = wx.DisplaySize()
        frame_size = self.GetSize()
        # 处理 auto 情况，实现自动居中并计算偏移
        frame_w, frame_h = frame_size[0], frame_size[1]
        screen_w, screen_h = display_size[0], display_size[1]
        # 解析 left/top
        if isinstance(pos_x, str) and pos_x == "auto":
            pl = 0
            left_auto = True
        else:
            pl = int(pos_x)
            left_auto = False
        if isinstance(pos_y, str) and pos_y == "auto":
            pt = 0
            top_auto = True
        else:
            pt = int(pos_y)
            top_auto = False
        # 计算起始点居中和偏移
        if initial == "左上":
            base_x = (screen_w - frame_w) // 2 if left_auto else 0
            base_y = (screen_h - frame_h) // 2 if top_auto else 0
            new_x = base_x + pl
            new_y = base_y + pt
        elif initial == "右上":
            base_x = (screen_w - frame_w) // 2 if left_auto else (screen_w - frame_w)
            base_y = (screen_h - frame_h) // 2 if top_auto else 0
            new_x = base_x - pl if left_auto else base_x - pl
            new_y = base_y + pt
        elif initial == "左下":
            base_x = (screen_w - frame_w) // 2 if left_auto else 0
            base_y = (screen_h - frame_h) // 2 if top_auto else (screen_h - frame_h)
            new_x = base_x + pl
            new_y = base_y - pt if top_auto else base_y - pt
        elif initial == "右下":
            base_x = (screen_w - frame_w) // 2 if left_auto else (screen_w - frame_w)
            base_y = (screen_h - frame_h) // 2 if top_auto else (screen_h - frame_h)
            new_x = base_x - pl if left_auto else base_x - pl
            new_y = base_y - pt if top_auto else base_y - pt
        else:
            base_x = (screen_w - frame_w) // 2 if left_auto else 0
            base_y = (screen_h - frame_h) // 2 if top_auto else 0
            new_x = base_x + pl
            new_y = base_y + pt
        self.SetPosition((new_x, new_y))
        if wx.Platform == "__WXMSW__":
            self.SetWindowStyle(self.GetWindowStyle() | wx.BORDER_NONE)
            self.SetTransparent(254)
        self.remaining_time = close_time
        self.result = None
        if self.remaining_time > 0:
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
            self.timer.Start(1000)
            self.update_countdown()

    def on_button(self, event):
        self.result = self.btn_map.get(event.GetEventObject().GetId(), None)
        self.EndModal(0)

    def on_timer(self, event):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.result = "自动关闭"
            self.EndModal(0)
        else:
            self.update_countdown()

    def update_countdown(self):
        self.countdown_label.SetLabel(f"倒计时: {self.remaining_time}秒")


# endregion

# region 日志捕获


class WxLogHandler(logging.Handler):
    """把带 ANSI 颜色码的日志输出到 wx.TextCtrl"""

    ANSI_TRUECOLOR_FG = re.compile(r"\x1b\[38;2;(\d+);(\d+);(\d+)m")
    ANSI_RESET = "\x1b[0m"

    def __init__(self, text_ctrl: wx.TextCtrl):
        super().__init__()
        self.text_ctrl = text_ctrl
        self.default_attr = wx.TextAttr(wx.BLACK, wx.NullColour)
        # 设置字体
        font_list = [
            "Maple Mono NF CN",
            "Menlo",
            "Consolas",
            "Maple UI",
            "PingFang",
            "Microsoft YaHei",
            "monospace",
        ]
        self.font = self._get_first_available_font(font_list)
        self.text_ctrl.SetFont(self.font)
        self.line_count = 0

    def _get_first_available_font(self, font_names):
        """按顺序返回第一个可用字体"""
        for name in font_names:
            font = wx.Font(wx.FontInfo().FaceName(name))
            if font.IsOk():
                return font
        return wx.Font(wx.FontInfo())  # 默认字体

    def emit(self, record):
        msg = self.format(record)
        wx.CallAfter(self._append, msg)
        self.flush()  # ✅ 强制刷新

    def flush(self):
        pass  # 这里不用真的写，因为 wx.TextCtrl 是立即写入的

    def _append_text(self, text, color_tuple):
        if not text:
            return

        # 自动换行
        if not text.endswith("\n"):
            text += "\n"

        # 拆分多行
        lines = text.splitlines()
        for line in lines:
            self.line_count += 1
            line_number_str = f"{self.line_count:4d} "  # 行号 + 空格
            start = self.text_ctrl.GetLastPosition()
            # 先插入行号
            self.text_ctrl.AppendText(line_number_str)
            end = self.text_ctrl.GetLastPosition()
            self.text_ctrl.SetStyle(
                start, end, wx.TextAttr(wx.Colour(255, 255, 255))
            )  # 白色

            # 再插入日志内容
            start = self.text_ctrl.GetLastPosition()
            self.text_ctrl.AppendText(line + "\n")
            end = self.text_ctrl.GetLastPosition()
            self.text_ctrl.SetStyle(start, end, wx.TextAttr(wx.Colour(*color_tuple)))

    def _append(self, msg):
        pos = 0
        text_len = len(msg)
        while pos < text_len:
            match = self.ANSI_TRUECOLOR_FG.search(msg, pos)
            if match:
                start, end = match.span()
                # 获取 RGB
                r, g, b = map(int, match.groups())
                fg_color = (r, g, b)
                # 找重置位置
                reset_pos = msg.find(self.ANSI_RESET, end)
                if reset_pos == -1:
                    reset_pos = text_len
                self._append_text(msg[end:reset_pos], fg_color)
                pos = reset_pos + len(self.ANSI_RESET)
            else:
                # 没有 ANSI，按级别颜色
                self._append_text(msg[pos:], (0, 0, 0))
                break

    def _append_with_attr(self, text, attr):
        if not text:
            return
        start = self.text_ctrl.GetLastPosition()
        self.text_ctrl.AppendText(text)
        end = self.text_ctrl.GetLastPosition()
        self.text_ctrl.SetStyle(start, end, attr)
        self.text_ctrl.Update()

    def _apply_ansi_codes(self, attr, codes):
        new_attr = wx.TextAttr(
            attr.GetTextColour(), attr.GetBackgroundColour(), attr.GetFont()
        )
        it = iter(codes)

        for code in it:
            if not code.isdigit():
                continue
            c = int(code)

            if c == 0:  # reset
                new_attr = wx.TextAttr(
                    self.default_attr.GetTextColour(),
                    self.default_attr.GetBackgroundColour(),
                    self.default_attr.GetFont(),
                )
            elif c == 1:  # bold
                font = new_attr.GetFont() or wx.Font(
                    10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
                )
                font.SetWeight(wx.FONTWEIGHT_BOLD)
                new_attr.SetFont(font)
            elif 30 <= c <= 37:
                new_attr.SetTextColour(self._ansi_16_color(c - 30))
            elif 40 <= c <= 47:
                new_attr.SetBackgroundColour(self._ansi_16_color(c - 40))
            elif c in (38, 48):  # TrueColor / 256色
                try:
                    mode = next(it)
                    if mode == "2":  # TrueColor
                        r, g, b = int(next(it)), int(next(it)), int(next(it))
                        color = wx.Colour(r, g, b)
                    elif mode == "5":  # 256色
                        idx = int(next(it))
                        color = self._ansi_256_color(idx)
                    else:
                        continue

                    if c == 38:
                        new_attr.SetTextColour(color)
                    else:
                        new_attr.SetBackgroundColour(color)
                except StopIteration:
                    pass
        return new_attr

    def _ansi_16_color(self, idx):
        """简单的 16 色映射"""
        table = [
            wx.BLACK,
            wx.RED,
            wx.GREEN,
            wx.YELLOW,
            wx.BLUE,
            wx.CYAN,
            wx.LIGHT_GREY,
            wx.WHITE,
        ]
        return table[idx % len(table)]

    def _ansi_256_color(self, idx):
        """简单的 256 色映射，按灰度 fallback"""
        return wx.Colour(idx, idx, idx)

    def _apply_ansi_codes(self, attr, codes):
        """解析 ANSI 颜色码，返回新的 wx.TextAttr"""
        new_attr = wx.TextAttr(
            attr.GetTextColour(), attr.GetBackgroundColour(), attr.GetFont()
        )
        it = iter(codes)

        for code in it:
            if not code.isdigit():
                continue
            c = int(code)

            if c == 0:  # reset
                new_attr = wx.TextAttr(
                    self.default_attr.GetTextColour(),
                    self.default_attr.GetBackgroundColour(),
                    self.default_attr.GetFont(),
                )
            elif c == 1:  # bold
                font = new_attr.GetFont() or wx.Font(
                    10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
                )
                font.SetWeight(wx.FONTWEIGHT_BOLD)
                new_attr.SetFont(font)
            elif 30 <= c <= 37:
                new_attr.SetTextColour(self._ansi_16_color(c - 30))
            elif 40 <= c <= 47:
                new_attr.SetBackgroundColour(self._ansi_16_color(c - 40))
            elif c in (38, 48):  # TrueColor / 256 色
                try:
                    mode = next(it)
                    if mode == "2":  # TrueColor
                        r, g, b = int(next(it)), int(next(it)), int(next(it))
                        color = wx.Colour(r, g, b)
                    elif mode == "5":  # 256 色
                        idx = int(next(it))
                        color = self._ansi_256_color(idx)
                    else:
                        continue

                    if c == 38:
                        new_attr.SetTextColour(color)
                    else:
                        new_attr.SetBackgroundColour(color)
                except StopIteration:
                    pass
        return new_attr

    # -------- 颜色映射辅助 --------

    def _ansi_256_color(self, idx):
        if idx < 16:
            return self._ansi_16_color(idx % 8)
        elif 16 <= idx <= 231:
            idx -= 16
            r = (idx // 36) % 6 * 51
            g = (idx // 6) % 6 * 51
            b = idx % 6 * 51
            return wx.Colour(r, g, b)
        elif 232 <= idx <= 255:
            gray = (idx - 232) * 10 + 8
            return wx.Colour(gray, gray, gray)
        return wx.Colour(255, 255, 255)

    def _ansi_16_color(self, idx):
        table = [
            wx.Colour(0, 0, 0),  # 黑
            wx.Colour(128, 0, 0),  # 红
            wx.Colour(0, 128, 0),  # 绿
            wx.Colour(128, 128, 0),  # 黄
            wx.Colour(0, 0, 128),  # 蓝
            wx.Colour(128, 0, 128),  # 品红
            wx.Colour(0, 128, 128),  # 青
            wx.Colour(192, 192, 192),  # 白（灰）
        ]
        return table[idx % 8]


# endregion
