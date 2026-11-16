"""Windows 可执行文件的入口。

打包成 ``paiban.exe`` 之后：

- 双击：打开图形界面
- 把文件拖到图标上：命令行模式处理该文件（窗口会停留，方便看结果）
- 在终端里带参数调用：和 ``paiban`` 命令完全一样
"""

from __future__ import annotations

import sys


def _attached_to_own_console() -> bool:
    """判断当前进程是不是双击启动的（独占一个新控制台）。

    从终端运行时，控制台里至少还挂着 shell，进程数 > 1；
    双击 exe 时 Windows 会新建一个只有它自己的控制台。
    """
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        pids = (ctypes.c_uint * 8)()
        return kernel32.GetConsoleProcessList(pids, 8) == 1
    except Exception:
        return False


def _should_open_gui() -> bool:
    """只有「双击图标」这一种情况开界面。

    条件是同时满足：没有命令行参数、标准输入是终端（不是管道/重定向）、
    且当前进程独占一个新控制台（从终端调用时控制台里还挂着 shell）。
    这样 ``echo 文本 | paiban.exe`` 仍然走命令行。
    """
    return len(sys.argv) == 1 and sys.stdin.isatty() and _attached_to_own_console()


def main() -> int:
    if _should_open_gui():
        from paiban.gui import run

        run()
        return 0

    from paiban.cli import main as cli_main

    code = cli_main()

    if _attached_to_own_console() and sys.stdin.isatty():
        try:
            input("\n按回车键退出…")
        except EOFError:
            pass
    return code


if __name__ == "__main__":
    sys.exit(main())
