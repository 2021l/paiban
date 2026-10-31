"""核心规则测试。"""

import unittest

from paiban import fix


class TestSpacing(unittest.TestCase):
    def test_latin_both_sides(self):
        self.assertEqual(fix("使用Python编写"), "使用 Python 编写")

    def test_around_word_with_space(self):
        self.assertEqual(fix("我用VS Code写代码"), "我用 VS Code 写代码")

    def test_digits_by_default(self):
        self.assertEqual(fix("第3章"), "第 3 章")

    def test_digits_can_be_disabled(self):
        self.assertEqual(fix("第3章", digits=False), "第3章")

    def test_digits_disabled_still_handles_letters(self):
        self.assertEqual(fix("第3章用Python", digits=False), "第3章用 Python")

    def test_space_rule_can_be_disabled(self):
        self.assertEqual(fix("使用Python", space=False), "使用Python")

    def test_pure_chinese_untouched(self):
        self.assertEqual(fix("中文排版"), "中文排版")

    def test_pure_ascii_untouched(self):
        self.assertEqual(fix("hello world"), "hello world")

    def test_empty_string(self):
        self.assertEqual(fix(""), "")


class TestCjkSpaces(unittest.TestCase):
    def test_collapses_spaces_between_chinese(self):
        self.assertEqual(fix("中 文 排 版"), "中文排版")

    def test_keeps_space_around_latin(self):
        self.assertEqual(fix("中文 Python 中文"), "中文 Python 中文")

    def test_can_be_disabled(self):
        self.assertEqual(fix("中 文", cjk_spaces=False), "中 文")


class TestPunctuation(unittest.TestCase):
    def test_space_before_closer(self):
        self.assertEqual(fix("你好 ，世界 ！"), "你好，世界！")

    def test_space_after_opener(self):
        self.assertEqual(fix("「 引号 」"), "「引号」")

    def test_brackets(self):
        self.assertEqual(fix("（ 说明 ）"), "（说明）")

    def test_colon_and_enumeration_comma(self):
        self.assertEqual(fix("如下 ：甲 、乙"), "如下：甲、乙")

    def test_interpunct_keeps_its_spaces(self):
        self.assertEqual(fix("paiban · 中文排版"), "paiban · 中文排版")

    def test_can_be_disabled(self):
        self.assertEqual(fix("你好 ，世界", punctuation=False), "你好 ，世界")


class TestTrailing(unittest.TestCase):
    def test_trailing_spaces_removed(self):
        self.assertEqual(fix("第一行   \n第二行\t\n"), "第一行\n第二行\n")

    def test_last_line_without_newline(self):
        self.assertEqual(fix("结尾   "), "结尾")

    def test_crlf_preserved(self):
        self.assertEqual(fix("中文   \r\nEnglish   \r\n"), "中文\r\nEnglish\r\n")

    def test_can_be_disabled(self):
        self.assertEqual(fix("第一行   \n", trailing=False), "第一行   \n")


class TestProtection(unittest.TestCase):
    def test_inline_code_untouched(self):
        self.assertEqual(fix("执行`git status`命令"), "执行`git status`命令")

    def test_fenced_block_untouched(self):
        source = "```python\n使用Python   \n```\n"
        self.assertEqual(fix(source), source)

    def test_tilde_fence_untouched(self):
        source = "~~~\n第3章\n~~~\n"
        self.assertEqual(fix(source), source)

    def test_unclosed_fence_protects_to_end(self):
        source = "说明\n\n```\n使用Python\n"
        self.assertEqual(fix(source), source)

    def test_url_untouched(self):
        url = "https://example.com/path?a=1&b=2"
        self.assertEqual(fix(f"见站点{url}"), f"见站点{url}")

    def test_autolink_untouched(self):
        self.assertEqual(fix("<https://example.com/a-b>"), "<https://example.com/a-b>")

    def test_markdown_link_destination_untouched(self):
        source = "详见[文档](https://example.com/a-b)"
        self.assertEqual(fix(source), source)

    def test_text_between_code_is_processed(self):
        self.assertEqual(fix("`code`中间English`code`"), "`code`中间 English`code`")

    def test_protection_can_be_disabled(self):
        self.assertEqual(fix("`a中文`", protect=False), "`a 中文`")

    def test_trailing_space_not_eaten_before_inline_code(self):
        self.assertEqual(fix("中文   `code`"), "中文   `code`")


class TestIdempotent(unittest.TestCase):
    CASES = [
        "使用Python编写",
        "第3章 用 VS Code 写代码",
        "「 引号 」和（ 括号 ）",
        "```\n使用Python   \n```\n中 文",
        "见https://example.com结尾",
        "第一行   \n第二行\t\n",
        "A中B3C",
        "",
    ]

    def test_fix_twice_equals_once(self):
        for case in self.CASES:
            once = fix(case)
            self.assertEqual(fix(once), once, msg=f"不幂等：{case!r}")


if __name__ == "__main__":
    unittest.main()
