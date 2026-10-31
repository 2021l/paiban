"""paiban 的命令行入口。"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

from . import __version__
from .core import fix

PROG = "paiban"
_BOM = b"\xef\xbb\xbf"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="中文排版自动修正：中西文加空格、清理全角标点两侧空格、去掉行尾空白。",
        epilog=(
            "示例：\n"
            "  paiban README.md            修正后输出到终端\n"
            "  paiban -i docs/*.md         就地改写\n"
            "  paiban --check docs/        在 CI 里检查（有改动则退出码 1）\n"
            "  cat a.md | paiban           从标准输入读取\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="要处理的文件；省略或写 - 时从标准输入读取",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-i", "--in-place", action="store_true", help="直接改写文件")
    mode.add_argument(
        "--check",
        action="store_true",
        help="只检查：有文件需要修正时列出文件名并以状态码 1 退出",
    )
    mode.add_argument("--diff", action="store_true", help="输出 unified diff")

    parser.add_argument("--no-space", action="store_true", help="不处理中西文之间的空格")
    parser.add_argument(
        "--no-digits", action="store_true", help="数字两侧不加空格（第3章 保持原样）"
    )
    parser.add_argument("--no-cjk-spaces", action="store_true", help="不合并汉字之间的空格")
    parser.add_argument("--no-punctuation", action="store_true", help="不清理全角标点两侧空格")
    parser.add_argument("--keep-trailing", action="store_true", help="保留行尾空白")
    parser.add_argument(
        "--no-protect", action="store_true", help="不保护代码块与 URL（可能改坏示例代码）"
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _fix(text: str, args: argparse.Namespace) -> str:
    return fix(
        text,
        space=not args.no_space,
        digits=not args.no_digits,
        cjk_spaces=not args.no_cjk_spaces,
        punctuation=not args.no_punctuation,
        trailing=not args.keep_trailing,
        protect=not args.no_protect,
    )


def _read_stdin() -> tuple:
    data = sys.stdin.buffer.read()
    return data.decode("utf-8-sig"), data.startswith(_BOM)


def _read_file(path: Path) -> tuple:
    raw = path.read_bytes()
    return raw.decode("utf-8-sig"), raw.startswith(_BOM)


def _write_file(path: Path, text: str, bom: bool) -> None:
    path.write_bytes((_BOM if bom else b"") + text.encode("utf-8"))


def _emit(text: str) -> None:
    """把结果写出去，尽量按 UTF-8，避免 Windows 控制台编码告警。"""
    buffer = getattr(sys.stdout, "buffer", None)
    if buffer is None:
        sys.stdout.write(text)
    else:
        buffer.write(text.encode("utf-8"))
        buffer.flush()


def _emit_diff(original: str, updated: str, name: str) -> None:
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile=f"{name} (原始)",
        tofile=f"{name} (修正后)",
    )
    for line in diff:
        _emit(line if line.endswith("\n") else line + "\n")


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    targets = args.files or ["-"]

    if args.in_place and "-" in targets:
        parser.error("--in-place 需要指定具体文件，不能用于标准输入")

    failed = False
    changed = []

    for name in targets:
        if name == "-":
            original, bom = _read_stdin()
            updated = _fix(original, args)
            if args.check:
                if updated != original:
                    changed.append("-")
            elif args.diff:
                _emit_diff(original, updated, "-")
            else:
                _emit(updated)
            continue

        path = Path(name)
        try:
            original, bom = _read_file(path)
        except OSError as exc:
            print(f"{PROG}: 无法读取 {name}：{exc}", file=sys.stderr)
            failed = True
            continue

        updated = _fix(original, args)

        if args.check:
            if updated != original:
                changed.append(name)
        elif args.diff:
            _emit_diff(original, updated, name)
        elif args.in_place:
            if updated != original:
                try:
                    _write_file(path, updated, bom)
                except OSError as exc:
                    print(f"{PROG}: 无法写入 {name}：{exc}", file=sys.stderr)
                    failed = True
        else:
            _emit(updated)

    if args.check:
        for name in changed:
            print(name)
        return 1 if changed else (2 if failed else 0)

    return 2 if failed else 0
