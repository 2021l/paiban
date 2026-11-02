"use strict";

// 与 tests/test_core.py 对应的 JS 平价测试：
// 保证 docs/paiban.js 与 src/paiban/core.py 行为一致。
// 运行：node --test tests/engine.test.cjs

const test = require("node:test");
const assert = require("node:assert/strict");
const { fix } = require("../docs/paiban.js");

test("中西文加空格", () => {
  assert.equal(fix("使用Python编写"), "使用 Python 编写");
  assert.equal(fix("我用VS Code写代码"), "我用 VS Code 写代码");
  assert.equal(fix("使用Python", { space: false }), "使用Python");
  assert.equal(fix("中文排版"), "中文排版");
  assert.equal(fix("hello world"), "hello world");
  assert.equal(fix(""), "");
});

test("数字", () => {
  assert.equal(fix("第3章"), "第 3 章");
  assert.equal(fix("第3章", { digits: false }), "第3章");
  assert.equal(fix("第3章用Python", { digits: false }), "第3章用 Python");
});

test("汉字间空格", () => {
  assert.equal(fix("中 文 排 版"), "中文排版");
  assert.equal(fix("中文 Python 中文"), "中文 Python 中文");
  assert.equal(fix("中 文", { cjkSpaces: false }), "中 文");
});

test("标点", () => {
  assert.equal(fix("你好 ，世界 ！"), "你好，世界！");
  assert.equal(fix("「 引号 」"), "「引号」");
  assert.equal(fix("（ 说明 ）"), "（说明）");
  assert.equal(fix("如下 ：甲 、乙"), "如下：甲、乙");
  assert.equal(fix("paiban · 中文排版"), "paiban · 中文排版");
  assert.equal(fix("你好 ，世界", { punctuation: false }), "你好 ，世界");
});

test("行尾空白", () => {
  assert.equal(fix("第一行   \n第二行\t\n"), "第一行\n第二行\n");
  assert.equal(fix("中文   \r\nEnglish   \r\n"), "中文\r\nEnglish\r\n");
  assert.equal(fix("结尾   "), "结尾");
  assert.equal(fix("第一行   \n", { trailing: false }), "第一行   \n");
});

test("保护区域", () => {
  const fenced = "```python\n使用Python   \n```\n";
  assert.equal(fix(fenced), fenced);
  const tilde = "~~~\n第3章\n~~~\n";
  assert.equal(fix(tilde), tilde);
  const unclosed = "说明\n\n```\n使用Python\n";
  assert.equal(fix(unclosed), unclosed);
  const url = "https://example.com/path?a=1&b=2";
  assert.equal(fix(`见站点${url}`), `见站点${url}`);
  assert.equal(fix("<https://example.com/a-b>"), "<https://example.com/a-b>");
  assert.equal(fix("详见[文档](https://example.com/a-b)"), "详见[文档](https://example.com/a-b)");
  assert.equal(fix("执行`git status`命令"), "执行`git status`命令");
  assert.equal(fix("`code`中间English`code`"), "`code`中间 English`code`");
  assert.equal(fix("中文   `code`"), "中文   `code`");
  assert.equal(fix("`a中文`", { protect: false }), "`a 中文`");
});

test("幂等", () => {
  const cases = [
    "使用Python编写",
    "第3章 用 VS Code 写代码",
    "「 引号 」和（ 括号 ）",
    "```\n使用Python   \n```\n中 文",
    "见https://example.com结尾",
    "第一行   \n第二行\t\n",
    "A中B3C",
    ""
  ];
  for (const c of cases) {
    const once = fix(c);
    assert.equal(fix(once), once, `不幂等：${JSON.stringify(c)}`);
  }
});
