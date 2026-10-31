# paiban · 中文排版

> 一条命令，把中文文档里那些看着别扭的空格修好。

[![CI](https://github.com/2021l/paiban/actions/workflows/ci.yml/badge.svg)](https://github.com/2021l/paiban/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

`paiban`（排版）是一个零依赖的 Python 小工具：它扫描 Markdown、纯文本或任何 UTF-8 文件，
在中英文之间补上该有的空格，顺手清掉全角标点旁边多出来的空白。
它同时是一个库，可以嵌进你自己的构建流程里。

## 它解决什么问题

中文和英文挤在一起可读性很差：

```text
开始使用Python编写第一个程序只需要三行代码。
```

排好版之后：

```text
开始使用 Python 编写第一个程序只需要三行代码。
```

这类问题人眼很容易漏掉，量大时更是改不胜改。`paiban` 把它变成一条命令。

## 安装

仓库还没有发布到 PyPI，从源码安装即可：

```bash
git clone https://github.com/2021l/paiban.git
cd paiban
pip install -e .
```

只想用一次，不安装也行，把 `src` 加进路径即可：

```bash
PYTHONPATH=src python -m paiban README.md
```

## 命令行

```bash
# 修正后输出到终端，原文件不动
paiban README.md

# 就地改写，可以一次给多个文件
paiban -i docs/*.md

# 只看差异，不写文件
paiban --diff README.md

# 从标准输入读
cat a.md | paiban
```

把检查放进 CI，谁改坏了排版谁就过不了：

```bash
paiban --check docs/   # 有文件需要修正时列出文件名，退出码 1
```

常用开关：

| 开关 | 作用 |
| --- | --- |
| `-i, --in-place` | 就地改写文件 |
| `--check` | 只检查，有改动则退出码 1 |
| `--diff` | 输出 unified diff |
| `--no-space` | 不处理中西文之间的空格 |
| `--no-digits` | 数字两侧不加空格（`第3章` 保持原样） |
| `--no-cjk-spaces` | 不合并汉字之间的空格 |
| `--no-punctuation` | 不清理全角标点两侧的空白 |
| `--keep-trailing` | 保留行尾空白 |
| `--no-protect` | 不保护代码块与链接（有风险，一般别用） |

退出码：`0` 正常，`1` 检查发现待修正内容，`2` 读写文件出错。

## 作为库使用

```python
from paiban import fix

fix("使用Python编写")
# '使用 Python 编写'

fix("第3章", digits=False)
# '第3章'

fix("「 引号 」")
# '「引号」'
```

所有选项都是关键字参数，默认全开：

```python
fix(
    text,
    space=True,        # 中文与拉丁字母之间补空格
    digits=True,       # 数字也参与（第3章 -> 第 3 章）
    cjk_spaces=True,   # 合并汉字之间的空格
    punctuation=True,  # 清理全角标点两侧空格
    trailing=True,     # 删除行尾空白
    protect=True,      # 保护代码块、行内代码、URL、链接地址
)
```

`fix` 是幂等的：`fix(fix(s)) == fix(s)`。所以重复跑不会把文档搞乱，
`--check` 在已经排好版的仓库里也永远是绿的。

## 规则

`paiban` 刻意只做几乎不可能出错的改动，宁可少改，也不猜你的意图。

| 规则 | 输入 | 输出 |
| --- | --- | --- |
| 中西文之间补空格 | `使用Python编写` | `使用 Python 编写` |
| 中文与数字之间补空格 | `第3章` | `第 3 章` |
| 合并汉字之间的空格 | `中 文 排 版` | `中文排版` |
| 闭合标点前不留空格 | `你好 ，世界` | `你好，世界` |
| 开启标点后不留空格 | `（ 说明 ）` | `（说明）` |
| 删除行尾空白 | `第一行␠␠␠` | `第一行` |

它**不**会做的事情，同样重要：不做繁简转换、不替换标点风格、不调整段落换行、
不碰全角字母和数字、不动任何你不让它动的地方。

## 保护区域

排版规则天然会误伤代码和链接，所以下面这些区域会被原样跳过：

- 围栏代码块 ` ``` ` 和 `~~~`（未闭合时一直保护到文末）
- 行内代码 `` `code` ``
- `https://…` 形式的裸链接与 `<https://…>` 自动链接
- Markdown 链接和图片的地址部分 `](…)`，链接文字照常处理

```markdown
使用`print()`输出    →  原样保留，不会变成 "使用 `print()` 输出"
```

如果你确实需要连代码一起处理，再加 `--no-protect`。

## 编码与换行

按 UTF-8 读写，自动识别并保留 BOM；CRLF 和 LF 换行都原样保留。
使用 `-i` 时只有内容真的变了才会写盘，不会无谓地刷新修改时间。

## 开发

```bash
pip install -e ".[dev]"
python -m pytest            # 跑测试
python -m pytest -q         # 安静模式
```

测试只依赖标准库里的 `unittest`，装了 `pytest` 也能直接跑。

## 许可证

[MIT](LICENSE)
