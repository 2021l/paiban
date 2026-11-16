# paiban · 中文排版

> 中文文档里那些多余的、缺失的空格，交给它对齐。

[![CI](https://github.com/2021l/paiban/actions/workflows/ci.yml/badge.svg)](https://github.com/2021l/paiban/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/2021l/paiban.svg)](https://github.com/2021l/paiban/releases/latest)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

paiban 是一个零依赖的 Python 小工具，做的事很窄：在中英文之间补上该有的空格，
清掉全角标点旁边多余的空白，删掉行尾空格。除此之外不动你的文字。

```text
开始使用Python编写第一个程序只需要三行代码。
            ↓
开始使用 Python 编写第一个程序只需要三行代码。
```

## 装上

三种方式，挑一个就行。

只想收拾一段文字，打开[在线演示](https://2021l.github.io/paiban/)，粘贴即可。

Windows 上不想装 Python，到 [Releases](https://github.com/2021l/paiban/releases/latest)
下载 `paiban.exe`，双击就是图形界面。单个 exe 约 12 MB，没做代码签名，
首次运行 Windows 可能提示「已保护你的电脑」，点「更多信息 → 仍要运行」。

要批量改文件或者接进 CI：

```bash
git clone https://github.com/2021l/paiban.git
cd paiban
pip install -e .
```

不想安装也能跑：`PYTHONPATH=src python -m paiban README.md`

## 用起来

```bash
paiban README.md          # 改完打印到终端，原文件不动
paiban -i docs/*.md       # 就地改写，可以给多个文件
paiban --diff README.md   # 只看差异，不写盘
cat a.md | paiban         # 从标准输入读
paiban --check docs/      # 只检查，有改动时退出码 1
```

`--check` 适合放进 CI，谁改坏了排版就过不去。

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

### 图形界面

```bash
paiban --gui
```

左边输入、右边输出，顶部那排开关就是上面这些选项，底部能打开文件、保存结果、复制输出，
`Ctrl+Enter` 等同于「排版」。

exe 双击打开的就是这个界面。把文件拖到图标上是命令行模式，窗口会留住结果方便看；
在终端里带参数调用则和 `paiban` 命令完全一样。

## 当库用

```python
from paiban import fix

fix("使用Python编写")   # '使用 Python 编写'
fix("第3章", digits=False)   # '第3章'
fix("「 引号 」")        # '「引号」'
```

选项都是关键字参数，默认全开：

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

`fix` 是幂等的，`fix(fix(s)) == fix(s)`，重复跑不会把文档越改越乱，
`--check` 在已经排好版的仓库里也一直是通过的。

## 规则

它只做几乎不可能出错的改动，宁可少改，也不猜你的意思。

| 规则 | 输入 | 输出 |
| --- | --- | --- |
| 中西文之间补空格 | `使用Python编写` | `使用 Python 编写` |
| 中文与数字之间补空格 | `第3章` | `第 3 章` |
| 合并汉字之间的空格 | `中 文 排 版` | `中文排版` |
| 闭合标点前不留空格 | `你好 ，世界` | `你好，世界` |
| 开启标点后不留空格 | `（ 说明 ）` | `（说明）` |
| 删除行尾空白 | `第一行␠␠␠` | `第一行` |

反过来，这些它不做：繁简转换、替换标点风格、重排段落、碰全角字母和数字。

## 会跳过的地方

代码和链接不该被排版规则碰，所以这些区域原样保留：

- 围栏代码块 ` ``` ` 和 `~~~`，未闭合时一直保护到文末
- 行内代码 `` `code` ``
- 裸链接 `https://…` 和 `<https://…>` 自动链接
- Markdown 链接与图片的地址部分 `](…)`，链接文字照常处理

```markdown
使用`print()`输出    →  原样不动，不会变成 "使用 `print()` 输出"
```

真要连代码一起处理，加 `--no-protect`。

## 编码与换行

按 UTF-8 读写，自动识别并保留 BOM，CRLF 和 LF 都原样保留。
`-i` 只在内容真的变了才写盘，不会无谓地刷新修改时间。

## 开发

```bash
pip install -e ".[dev]"
python -m pytest
```

测试只依赖标准库里的 `unittest`，装了 `pytest` 也能直接跑。

自己打包 exe（Windows，需要先装 PyInstaller）：

```powershell
python -m pip install pyinstaller
.\packaging\build_exe.ps1
```

产物在 `dist\paiban.exe`。推 `v*` 标签时 CI 也会自动构建并挂到 Release 上，
见 `.github/workflows/release-exe.yml`。

## 许可证

[MIT](LICENSE)
