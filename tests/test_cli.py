"""命令行行为测试。"""

import io
import shutil
import tempfile
import unittest
import uuid
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from paiban.cli import main


def _scratch_dir() -> Path:
    """建一个空的测试目录。

    这里刻意不用 ``tempfile.mkdtemp``：它以 ``0o700`` 创建目录，而在部分
    Windows 受限环境（沙箱、被收紧的 ACL）里，用 0700 建出来的目录随后
    反而不可写。用默认权限建目录最稳。
    """
    path = Path(tempfile.gettempdir()) / f"paiban-test-{uuid.uuid4().hex[:12]}"
    path.mkdir()
    return path


class CliTest(unittest.TestCase):
    def setUp(self):
        self.dir = _scratch_dir()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _file(self, name, text):
        path = self.dir / name
        path.write_bytes(text.encode("utf-8"))
        return path

    def test_stdout_mode(self):
        path = self._file("a.md", "使用Python")
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([str(path)])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), "使用 Python")

    def test_in_place(self):
        path = self._file("a.md", "第3章\n")
        with redirect_stdout(io.StringIO()):
            code = main(["-i", str(path)])
        self.assertEqual(code, 0)
        self.assertEqual(path.read_bytes().decode("utf-8"), "第 3 章\n")

    def test_in_place_is_noop_when_clean(self):
        path = self._file("a.md", "已经排好版了\n")
        before = path.stat().st_mtime_ns
        with redirect_stdout(io.StringIO()):
            code = main(["-i", str(path)])
        self.assertEqual(code, 0)
        self.assertEqual(path.read_bytes().decode("utf-8"), "已经排好版了\n")
        self.assertEqual(path.stat().st_mtime_ns, before)

    def test_check_reports_dirty_file(self):
        path = self._file("a.md", "使用Python\n")
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--check", str(path)])
        self.assertEqual(code, 1)
        self.assertIn("a.md", out.getvalue())

    def test_check_passes_when_clean(self):
        path = self._file("a.md", "使用 Python\n")
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--check", str(path)])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), "")

    def test_diff_mode(self):
        path = self._file("a.md", "使用Python\n")
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--diff", str(path)])
        self.assertEqual(code, 0)
        self.assertIn("-使用Python", out.getvalue())
        self.assertIn("+使用 Python", out.getvalue())

    def test_missing_file_returns_2(self):
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            code = main([str(self.dir / "nope.md")])
        self.assertEqual(code, 2)
        self.assertIn("无法读取", err.getvalue())

    def test_bom_is_preserved(self):
        path = self.dir / "b.md"
        path.write_bytes(b"\xef\xbb\xbf" + "使用Python".encode("utf-8"))
        with redirect_stdout(io.StringIO()):
            main(["-i", str(path)])
        data = path.read_bytes()
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(data[3:].decode("utf-8"), "使用 Python")

    def test_option_passthrough(self):
        path = self._file("a.md", "第3章")
        out = io.StringIO()
        with redirect_stdout(out):
            main([str(path), "--no-digits"])
        self.assertEqual(out.getvalue(), "第3章")

    def test_in_place_rejects_stdin(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["-i", "-"])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
