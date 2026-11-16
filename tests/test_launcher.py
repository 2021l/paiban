"""可执行文件入口的分支逻辑测试（双击 vs 命令行）。"""

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

LAUNCHER = Path(__file__).resolve().parents[1] / "packaging" / "paiban_win.py"


def _load():
    spec = importlib.util.spec_from_file_location("paiban_win_launcher", LAUNCHER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LauncherTest(unittest.TestCase):
    def setUp(self):
        self.mod = _load()

    def _decide(self, argv, isatty, own_console):
        with mock.patch.object(self.mod.sys, "argv", argv), mock.patch.object(
            self.mod.sys.stdin, "isatty", return_value=isatty
        ), mock.patch.object(self.mod, "_attached_to_own_console", return_value=own_console):
            return self.mod._should_open_gui()

    def test_double_click_opens_gui(self):
        self.assertTrue(self._decide(["paiban.exe"], True, True))

    def test_piped_stdin_stays_cli(self):
        self.assertFalse(self._decide(["paiban.exe"], False, True))

    def test_arguments_stay_cli(self):
        self.assertFalse(self._decide(["paiban.exe", "a.md"], True, True))

    def test_run_from_terminal_stays_cli(self):
        self.assertFalse(self._decide(["paiban.exe"], True, False))


if __name__ == "__main__":
    unittest.main()
