"""paiban 的核心排版规则。

设计原则只有一条：只做「读起来更舒服、且几乎不可能出错」的改动。

因此所有规则都是幂等的（对已经排好版的文本再跑一遍不会有变化），
并且代码块、行内代码、URL、Markdown 链接地址一律原样保留。
"""

from __future__ import annotations

import re

__all__ = ["fix", "CJK"]

# --------------------------------------------------------------------------
# 字符类
# --------------------------------------------------------------------------

# 汉字、假名、谚文等「全角文字」的码位范围。
_CJK_CLASS = (
    "\u3040-\u30ff"  # 平假名 / 片假名
    "\u3400-\u4dbf"  # 汉字扩展 A
    "\u4e00-\u9fff"  # 汉字基本区
    "\uf900-\ufaff"  # 兼容汉字
    "\uac00-\ud7af"  # 谚文音节
)
CJK = f"[{_CJK_CLASS}]"

# 全角闭合标点：它前面不该有空格。
# 注意不要把间隔号 ``·`` 列进来——它是分隔符，``paiban · 中文`` 两侧的空格是有意的。
_CLOSERS = "，。！？；：、）》」』】〕〉”’…"
# 全角开启标点：它后面不该有空格
_OPENERS = "（《「『【〔〈“‘"

# --------------------------------------------------------------------------
# 规则（只在「非保护区域」上运行）
# --------------------------------------------------------------------------

_RE_SPACE_BEFORE_CLOSER = re.compile(rf"[ \t]+(?=[{re.escape(_CLOSERS)}])")
_RE_SPACE_AFTER_OPENER = re.compile(rf"(?<=[{re.escape(_OPENERS)}])[ \t]+")
_RE_SPACES_BETWEEN_CJK = re.compile(rf"(?<={CJK})[ \t]+(?={CJK})")

# 中文 ↔ 拉丁字母 / 数字
_RE_CJK_THEN_ALNUM = re.compile(rf"(?<={CJK})(?=[A-Za-z0-9])")
_RE_ALNUM_THEN_CJK = re.compile(rf"(?<=[A-Za-z0-9])(?={CJK})")
_RE_CJK_THEN_ALPHA = re.compile(rf"(?<={CJK})(?=[A-Za-z])")
_RE_ALPHA_THEN_CJK = re.compile(rf"(?<=[A-Za-z])(?={CJK})")

# 行尾空白：能确定处于「真实行尾」时才删
_RE_TRAILING_EOL = re.compile(r"[ \t]+(?=\r\n|\r|\n)")
_RE_TRAILING_TAIL = re.compile(r"[ \t]+$")

# --------------------------------------------------------------------------
# 保护区域
# --------------------------------------------------------------------------

# 围栏代码块。未闭合时一直保护到文末（``\Z`` 分支）。
_RE_FENCED = re.compile(
    r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})[^\n]*\n"
    r".*?"
    r"(?:^[ \t]{0,3}(?P=fence)[^\n]*$|\Z)",
    re.MULTILINE | re.DOTALL,
)
# 行内代码
_RE_INLINE_CODE = re.compile(r"`[^`\n]*`")
# <https://…> 形式的自动链接
_RE_AUTOLINK = re.compile(r"<https?://[^>\s]+>")
# 裸 URL
_RE_URL = re.compile(r"https?://[^\s<>`\"']+")
# Markdown 链接 / 图片的地址部分，只保护 ``](…)``，链接文字照常处理
_RE_LINK_DEST = re.compile(r"\]\([^)\n]*\)")

_PROTECTORS = (
    _RE_FENCED,
    _RE_INLINE_CODE,
    _RE_AUTOLINK,
    _RE_URL,
    _RE_LINK_DEST,
)


def _protected_spans(text: str) -> list:
    """返回 ``(start, end)`` 列表，已排序并合并重叠部分。"""
    spans = []
    for pattern in _PROTECTORS:
        for match in pattern.finditer(text):
            spans.append((match.start(), match.end()))
    if not spans:
        return []
    spans.sort()
    merged = [list(spans[0])]
    for start, end in spans[1:]:
        if start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1][1] = end
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


# --------------------------------------------------------------------------
# 单段处理
# --------------------------------------------------------------------------

def _apply(
    segment: str,
    *,
    space: bool,
    digits: bool,
    cjk_spaces: bool,
    punctuation: bool,
    trailing: bool,
    at_line_end: bool,
) -> str:
    if not segment:
        return segment

    text = segment

    if space:
        if digits:
            text = _RE_CJK_THEN_ALNUM.sub(" ", text)
            text = _RE_ALNUM_THEN_CJK.sub(" ", text)
        else:
            text = _RE_CJK_THEN_ALPHA.sub(" ", text)
            text = _RE_ALPHA_THEN_CJK.sub(" ", text)

    if cjk_spaces:
        text = _RE_SPACES_BETWEEN_CJK.sub("", text)

    if punctuation:
        text = _RE_SPACE_BEFORE_CLOSER.sub("", text)
        text = _RE_SPACE_AFTER_OPENER.sub("", text)

    if trailing:
        text = _RE_TRAILING_EOL.sub("", text)
        if at_line_end:
            text = _RE_TRAILING_TAIL.sub("", text)

    return text


# --------------------------------------------------------------------------
# 公开接口
# --------------------------------------------------------------------------

def fix(
    text: str,
    *,
    space: bool = True,
    digits: bool = True,
    cjk_spaces: bool = True,
    punctuation: bool = True,
    trailing: bool = True,
    protect: bool = True,
) -> str:
    """修正一段文本的中文排版。

    参数（全部可选，默认全开）:

    ``space``
        在中文与拉丁字母之间补一个空格：``使用Python`` -> ``使用 Python``。
    ``digits``
        是否也处理数字：``第3章`` -> ``第 3 章``。设为 ``False`` 时数字不动。
    ``cjk_spaces``
        去掉两个汉字之间多余的空格：``中 文`` -> ``中文``。
    ``punctuation``
        去掉全角标点两侧的空格：``你好 ，世界`` -> ``你好，世界``。
    ``trailing``
        删除行尾多余的空格与制表符。
    ``protect``
        是否保护代码块、行内代码、URL 与链接地址（默认保护）。

    该函数是幂等的：``fix(fix(s)) == fix(s)``。
    """
    if not text:
        return text

    kwargs = dict(
        space=space,
        digits=digits,
        cjk_spaces=cjk_spaces,
        punctuation=punctuation,
        trailing=trailing,
    )

    if not protect:
        return _apply(text, at_line_end=True, **kwargs)

    spans = _protected_spans(text)
    if not spans:
        return _apply(text, at_line_end=True, **kwargs)

    out = []
    cursor = 0
    for start, end in spans:
        if start > cursor:
            # 只有保护区正好从行首开始时，前一段的末尾空白才算「行尾空白」；
            # 否则那些空格处于行中间（例如行内代码前面），必须保留。
            at_line_end = start >= len(text) or text[start] in "\r\n"
            out.append(_apply(text[cursor:start], at_line_end=at_line_end, **kwargs))
        out.append(text[start:end])
        cursor = end
    if cursor < len(text):
        out.append(_apply(text[cursor:], at_line_end=True, **kwargs))
    return "".join(out)
