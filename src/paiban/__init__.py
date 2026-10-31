"""paiban —— 中文排版自动修正。

快速上手::

    from paiban import fix

    fix("使用Python编写")
    # => "使用 Python 编写"
"""

from __future__ import annotations

from .core import fix

__version__ = "0.1.0"
__all__ = ["fix", "__version__"]
