# common_utils/__init__.py
# 作用是将包含它的目录标识为包（package），从而支持模块导入
# 它可以是空的，也可以包含初始化逻辑。


from .logger_setup import setup_logger
from .file_utils import FileUtils
from .wx_utils import WxUtils
from .pip_utils import PipUtils



# 自动生成__all__列表，包含所有显式导入的名称
__all__ = [name for name in locals() if not name.startswith("_") and name != "name"]


# 依赖如下

# pip install logging colorama wcwidth requests wxPython

# logging
# 安装：pip install logging
# 作用：用于记录日志，包括调试、信息、警告、错误等级别
# 示例：
# import logging
# logging.basicConfig(level=logging.DEBUG)
# logging.debug("This is a debug message")

# colorama
# 安装：pip install colorama
# 作用：用于在Windows终端中添加颜色和样式
# 示例：
# import colorama
# from colorama import Fore, Back, Style
# colorama.init()
# print(Fore.RED + 'This is red text' + Style.RESET_ALL)
# print(Back.GREEN + 'This has a green background' + Style.RESET_ALL)
# print('This is normal text')

# wcwidth
# 安装：pip install wcwidth
# 作用：用于计算字符串的终端宽度，考虑了终端中的特殊字符宽度，如全角字符。
# 示例：
# import wcwidth
# text = "你好，世界！"
# width = wcwidth.wcswidth(text)
# print(width)  # 输出 12，考虑了中文字符的宽度

# requests
# 安装：pip install requests
# 作用：用于发送HTTP请求
# 示例：
# import requests
# response = requests.get('https://api.github.com')
# print(response.status_code)  # 输出 200
# print(response.json())  # 输出 JSON 格式的响应内容

# wxPython
# 安装：pip install wxPython
# 作用：用于创建图形用户界面（GUI）
