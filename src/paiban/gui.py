"""paiban 的图形界面。

只用标准库 tkinter，打包成 .exe 之后双击就能用：
左边粘文本，点「排版」，右边看结果。
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import __version__
from .core import fix

SAMPLE = """paiban是一个零依赖的中文排版工具，它会把「使用Python编写」修正成「使用 Python 编写」。

第3章介绍这些规则 ： 中西文加空格、合并 汉字 之间 的空格、清理（ 标点 ）两侧空白。
行尾的多余空格会被删掉。

代码和链接原样保留：
```python
使用Python编写第一行
```
执行`git status`，再看 https://example.com/path?a=1 。
"""

# (fix() 的关键字参数, 界面上的名字)
OPTIONS = (
    ("space", "中西文空格"),
    ("digits", "数字空格"),
    ("cjk_spaces", "汉字间空格"),
    ("punctuation", "标点清理"),
    ("trailing", "行尾空白"),
    ("protect", "保护代码/链接"),
)

FILE_TYPES = (("文本文件", "*.md *.txt *.rst"), ("所有文件", "*.*"))


class App(tk.Tk):
    """主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.title(f"paiban {__version__} · 中文排版")
        self.geometry("1040x660")
        self.minsize(760, 500)

        self.flags = {key: tk.BooleanVar(value=True) for key, _ in OPTIONS}
        self._build()

        self.bind("<Control-Return>", self.render)
        self.src.insert("1.0", SAMPLE)
        self.render()

    # ---------------------------------------------------------------- 布局

    def _build(self) -> None:
        toolbar = ttk.Frame(self, padding=(10, 8))
        toolbar.pack(fill="x")

        for key, label in OPTIONS:
            ttk.Checkbutton(
                toolbar, text=label, variable=self.flags[key], command=self.render
            ).pack(side="left", padx=(0, 12))

        ttk.Button(toolbar, text="排版 (Ctrl+Enter)", command=self.render).pack(side="right")

        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        self.src = self._panel(panes, "输入")
        self.dst = self._panel(panes, "输出")

        footer = ttk.Frame(self, padding=(10, 6))
        footer.pack(fill="x")

        ttk.Button(footer, text="打开文件", command=self.open_file).pack(side="left")
        ttk.Button(footer, text="保存结果", command=self.save_file).pack(side="left", padx=6)
        ttk.Button(footer, text="载入示例", command=self.load_sample).pack(side="left")
        ttk.Button(footer, text="清空", command=self.clear).pack(side="left", padx=6)
        ttk.Button(footer, text="复制结果", command=self.copy_result).pack(side="left")

        self.status = ttk.Label(footer, text="")
        self.status.pack(side="right")

    def _panel(self, parent: ttk.PanedWindow, title: str) -> tk.Text:
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=title).pack(anchor="w", pady=(0, 4))

        holder = ttk.Frame(frame)
        holder.pack(fill="both", expand=True)

        text = tk.Text(holder, wrap="word", undo=True, font=("Consolas", 10), padx=6, pady=6)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        parent.add(frame, weight=1)
        return text

    # ---------------------------------------------------------------- 行为

    def options(self) -> dict:
        return {key: flag.get() for key, flag in self.flags.items()}

    def render(self, event=None) -> None:
        source = self.src.get("1.0", "end-1c")
        result = fix(source, **self.options())
        self.dst.delete("1.0", "end")
        self.dst.insert("1.0", result)
        self.status.configure(text="没有改动" if result == source else "已修正")

    def load_sample(self) -> None:
        self.src.delete("1.0", "end")
        self.src.insert("1.0", SAMPLE)
        self.render()

    def clear(self) -> None:
        self.src.delete("1.0", "end")
        self.dst.delete("1.0", "end")
        self.status.configure(text="")
        self.src.focus_set()

    def copy_result(self) -> None:
        result = self.dst.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(result)
        self.status.configure(text="已复制到剪贴板")

    def open_file(self) -> None:
        path = filedialog.askopenfilename(title="打开文本", filetypes=FILE_TYPES)
        if not path:
            return
        try:
            data = Path(path).read_text(encoding="utf-8-sig")
        except OSError as exc:
            messagebox.showerror("打开失败", str(exc))
            return
        self.src.delete("1.0", "end")
        self.src.insert("1.0", data)
        self.render()
        self.status.configure(text=f"已打开 {Path(path).name}")

    def save_file(self) -> None:
        path = filedialog.asksaveasfilename(
            title="保存结果", defaultextension=".md", filetypes=FILE_TYPES
        )
        if not path:
            return
        try:
            Path(path).write_text(self.dst.get("1.0", "end-1c"), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("保存失败", str(exc))
            return
        self.status.configure(text=f"已保存 {Path(path).name}")


def run() -> None:
    """启动图形界面。"""
    App().mainloop()
