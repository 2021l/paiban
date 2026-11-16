"""图形界面的可用性检查；没有显示环境时自动跳过。"""

import unittest


class GuiTest(unittest.TestCase):
    def test_module_imports(self):
        try:
            import paiban.gui  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            self.skipTest(f"缺少 tkinter：{exc}")

    def test_window_builds(self):
        try:
            import tkinter
        except ImportError as exc:  # pragma: no cover
            self.skipTest(f"缺少 tkinter：{exc}")

        from paiban.gui import App

        try:
            app = App()
        except tkinter.TclError as exc:  # pragma: no cover
            self.skipTest(f"没有可用显示：{exc}")

        try:
            app.withdraw()
            app.update_idletasks()
            self.assertIn("paiban", app.title())
            self.assertEqual(len(app.options()), 6)
            self.assertTrue(app.src.get("1.0", "end-1c"))
        finally:
            app.destroy()

    def test_render_applies_rules(self):
        try:
            import tkinter
        except ImportError as exc:  # pragma: no cover
            self.skipTest(f"缺少 tkinter：{exc}")

        from paiban.gui import App

        try:
            app = App()
        except tkinter.TclError as exc:  # pragma: no cover
            self.skipTest(f"没有可用显示：{exc}")

        try:
            app.withdraw()
            app.src.delete("1.0", "end")
            app.src.insert("1.0", "使用Python编写")
            app.render()
            self.assertEqual(app.dst.get("1.0", "end-1c"), "使用 Python 编写")
            self.assertEqual(app.status.cget("text"), "已修正")
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
