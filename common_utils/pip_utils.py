import importlib.util
import sys
import os
import inspect


class PipUtils:
    @staticmethod
    def load_module(name, rel_path):
        """
        动态加载Python模块的工具函数。

        该函数支持在打包环境和开发环境下动态加载Python模块文件。它会根据运行环境自动判断
        正确的基础路径，并使用Python的importlib机制来加载模块。加载后的模块会被添加到
        sys.modules中，使其可以被其他代码import。

        Args:
            name (str): 模块别名，例如 "auto_packager"
            rel_path (str): 相对路径，例如 "02.自动录屏截屏打包/auto_packager.py"

        Returns:
            module: 加载完成的模块对象

        Example:
            auto_packager = PipUtils.load_module(
                "auto_packager", "02.自动录屏截屏打包/auto_packager.py"
            )
        """

        # 检查是否在打包环境中运行
        if getattr(sys, "frozen", False):
            # 打包后 exe
            base_path = sys._MEIPASS
        else:
            # 调试环境
            base_path = os.path.abspath(".")  # 当前项目根目录

        # 构建模块文件的完整路径
        file_path = os.path.join(base_path, rel_path)

        # 从文件路径创建模块规范对象
        spec = importlib.util.spec_from_file_location(name, file_path)

        # 根据规范创建新的模块对象
        module = importlib.util.module_from_spec(spec)

        # 将模块添加到sys.modules中以便能够被import语句引用
        sys.modules[name] = module

        # 执行模块代码
        spec.loader.exec_module(module)

        # 返回加载好的模块对象
        return module

    @staticmethod
    def get_base_path():
        """
        获取当前脚本的基础路径。

        该方法会根据脚本是否在打包环境中运行，返回不同的基础路径。
        如果在打包环境中运行（如使用pyinstaller打包），则返回sys._MEIPASS；
        如果在调试环境中运行，则返回当前脚本所在目录的绝对路径。

        Returns:
            str: 当前脚本的基础路径
        """
        # 检查是否在打包环境中运行
        if getattr(sys, "frozen", False):
            # 打包后的 exe，__file__ 指向 exe 路径
            return os.path.dirname(sys.executable)
        else:
            # 调试环境
            return os.path.dirname(
                os.path.abspath(inspect.stack()[1].filename)
            )  # 调用者所在目录
