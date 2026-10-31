"""允许 ``python -m paiban`` 直接调用命令行。"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
