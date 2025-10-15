"""
日期: 2024-03-21
功能描述:
- 实现了一个基于wxPython的GUI模板程序
- 提供了文件选择、文件夹选择、文本输入等基础控件
- 支持配置文件保存和读取功能
- 包含日志显示面板
- 界面采用左右分栏设计，左侧为操作区，右侧为日志显示区
"""

import sys
import os
import wx
import json
import requests
import traceback
import time
import asyncio
from urllib.parse import quote
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
import aiohttp


# 将项目的根目录添加到 Python 的模块搜索路径中
# 即当前py文件所在目录，的上一级目录
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common_utils import setup_logger, WxUtils, PipUtils

logger = setup_logger()


class MainFrame(wx.Frame):
    """
    主窗口类，继承自wx.Frame
    用于创建软著可运行打包工具的主界面
    """

    def __init__(self):
        """
        初始化主窗口
        设置窗口标题、大小，并初始化必要的变量和控件
        """
        super().__init__(parent=None, title="重返未来1999图片下载", size=(1300, 800))
        # 配置文件路径（放到当前目录）
        self.config_path = os.path.join(
            PipUtils.get_base_path(), "Reverse_1999_image_download.cfg"
        )
        logger.info(f"配置文件路径：{self.config_path}")
        self.config = wx.FileConfig(localFilename=self.config_path)

        # 初始化wx工具类
        self.wx_utils = WxUtils(self, config=self.config, row_height=40)

        # 创建主面板
        self.panel = wx.Panel(self)
        self.init_ui()

        # 窗口居中显示
        self.Center()

    def init_ui(self):
        """
        初始化用户界面
        创建并布局所有控件
        """
        # 整体水平布局
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 创建左侧面板（参数设置区）
        left_panel = wx.Panel(self.panel, style=wx.BORDER_NONE)
        left_panel.SetMinSize(wx.Size(465, -1))  # 设置左侧固定宽度
        left_panel.SetBackgroundColour(wx.Colour(250, 250, 250))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_panel.SetSizer(left_sizer)

        # 内容部分再套一层 sizer
        content_sizer = wx.BoxSizer(wx.VERTICAL)

        rows = [
            {"title": "接口地址：", "config_key": "api_url"},
            {"title": "起始页码：", "config_key": "start_page"},
            {"title": "每页数量：", "config_key": "page_size"},
        ]
        for row in rows:
            self.wx_utils.create_text_ctrl(
                parent=left_panel,
                sizer=content_sizer,
                row=row,
            )

        # 创建目录选择控件
        rows = [
            {"title": "图片保存路径：", "config_key": "download_dir"},
        ]
        self.wx_utils.create_folder_ctrls(
            sizer=content_sizer, parent=left_panel, rows=rows
        )

        # 创建文件选择控件
        rows = [
            {
                "title": "谷歌浏览器路径：",
                "config_key": "browser_path",
                "suffixs": "exe",
            },
        ]
        self.wx_utils.create_file_ctrls(
            sizer=content_sizer, parent=left_panel, rows=rows
        )

        # 将内容添加到左侧面板
        left_sizer.Add(content_sizer, 1, wx.EXPAND)

        # 创建运行按钮
        self.wx_utils.create_run_btns(
            sizer=left_sizer,
            parent=left_panel,
            btn_group=[
                {
                    "title": "开始下载",
                    "name": "start_run",
                    "event": self.on_start_run,
                }
            ],
        )
        left_panel.SetSizer(left_sizer)

        # 创建右侧面板（日志显示区）
        right_panel = wx.Panel(self.panel, style=wx.BORDER_NONE)
        right_panel.SetBackgroundColour(wx.Colour(47, 54, 60))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        # 添加日志控件
        self.wx_utils.create_log_ctrls(panel=right_panel, main_sizer=right_sizer)
        right_panel.SetSizer(right_sizer)

        # 添加左右面板到主布局
        main_sizer.Add(left_panel, 0, wx.EXPAND)  # 左侧不拉伸
        main_sizer.Add(right_panel, 1, wx.EXPAND)  # 右侧自适应拉伸

        self.panel.SetSizer(main_sizer)
        self.panel.Layout()

    # region 事件处理函数

    @WxUtils.run_in_thread
    def on_start_run(self, event):
        """
        开始打包按钮的点击事件处理函数
        在新线程中执行打包操作
        """
        btn = self.wx_utils.get_btn_ctrl(name="start_run")
        if getattr(btn, "_disabled_simulate", False):
            logger.error("请不要重复点击按钮")
            return

        self.wx_utils.toggle_btn(label="运行中...", btn=btn)
        try:
            asyncio.run(self.run_time())

        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"运行失败: {str(e)}\n详细错误信息:\n{error_info}")
        finally:
            self.wx_utils.toggle_btn(label="开始运行", btn=btn)

    # endregion

    # region 功能函数

    async def run_time(self):
        """
        处理的核心函数
        """
        async with aiohttp.ClientSession() as session:
            text = self.wx_utils.get_text_ctrl(name="api_url")
            api_url = text.GetValue()
            text = self.wx_utils.get_text_ctrl(name="start_page")
            start_page = int(text.GetValue())
            text = self.wx_utils.get_text_ctrl(name="page_size")
            page_size = int(text.GetValue())
            text = self.wx_utils.get_text_ctrl(name="download_dir")
            download_dir = text.GetValue()
            text = self.wx_utils.get_text_ctrl(name="browser_path")
            browser_path = text.GetValue()

            count = 0
            async with async_playwright() as p:
                while True:
                    page_data, total = await self.fetch_page(
                        api_url, session, start_page, page_size
                    )
                    # 结束下载条件：没有更多数据
                    if not page_data:
                        logger.info(f"下载完成，共下载 {count} 张图片")
                        break

                    for item in page_data:
                        image_url = item["pictureUrl"]
                        # 拼接图片保存路径
                        output_path = os.path.join(
                            download_dir, f"{os.path.basename(image_url)}"
                        )
                        count += 1
                        logger.info(f"开始下载第 {count} 张图片")
                        start_time = time.time()
                        success = await self.download_image(
                            p, browser_path, image_url, output_path
                        )
                        elapsed = time.time() - start_time
                        logger.info(f"第 {count} 张图片下载耗时：{elapsed:.2f}s")
                        if not success:
                            logger.error(f"⚠️ 下载失败: {image_url}")
                        else:
                            # 计算文件大小（MB）
                            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                            logger.success(
                                f"✅ 下载成功，使用 {elapsed:.2f}s，文件大小：{file_size_mb:.2f} MB"
                            )

                    start_page += 1

    async def fetch_page(self, api_url, session, page_num, page_size):
        payload = {"current": page_num, "pageSize": page_size}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; ImageDownloader/1.0)",
        }
        async with session.post(
            api_url, json=payload, headers=headers, timeout=20
        ) as resp:
            data = await resp.json()
            page_data = data["data"]["pageData"]
            total = data["data"]["total"]
            return page_data, total

    async def download_image(self, playwright, browser_path, url, save_path):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # 检查文件是否已存在
        if os.path.exists(save_path):
            logger.warning(f"文件已存在，跳过下载: {save_path}")
            return True

        browser = await playwright.chromium.launch(
            headless=True, executable_path=browser_path
        )
        page = await browser.new_page()
        # 设置 Referer 防止 CDN 防盗链
        await page.set_extra_http_headers(
            {"Referer": "https://re.bluepoch.com/activity/official/websites/picture"}
        )
        try:
            await page.goto(url, timeout=30000)
            # fetch + arrayBuffer 下载图片
            img_bytes = await page.evaluate(
                f"""
                async () => {{
                    const res = await fetch("{url}");
                    const buf = await res.arrayBuffer();
                    return Array.from(new Uint8Array(buf));
                }}
            """
            )
            with open(save_path, "wb") as f:
                f.write(bytes(img_bytes))
        except PlaywrightTimeoutError:
            logger.warning(f"⚠️ 下载超时: {url}")
            await browser.close()
            return False
        await browser.close()
        return True

    # endregion


if __name__ == "__main__":
    app = wx.App(False)
    MainFrame().Show()
    app.MainLoop()
