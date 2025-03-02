# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2025/3/2 22:08
@Author     : lkkings
@FileName:  : look.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import re
from pathlib import Path
from typing import Optional

from rich.text import Text

from datahive.cli.cli_console import console
from datahive.cli.cli_view import Viewer



def _generate_regx_lines(text, regx):
    """生成带行号和字符差异的文本行"""
    lines = text.splitlines()
    regx_lines = []
    if regx:
        pattern = re.compile(regx)
        for line in lines:
            matches = pattern.findall(line)
            if len(matches) > 0:
                line_container = Text()
                line_no = Text(f"{len(regx_lines) + 1:4} ", style="bold cyan")
                line_container.append(line_no)
                index = 0
                for match in matches:
                    match_text = match[match.start():match.end()]
                    line.append(Text(line[index:match.start()]))
                    index += match.start()
                    for i in range(1, len(match.groups()) + 1):
                        pass


def look(input_file: str, regx: Optional[str]):
    try:
        # TODO: 完成文本正则表达式匹配查看
        pass
        # text = Path(input_file).read_text("utf-8")
        # lines = _generate_regx_lines(text, regx)
        # with Viewer(title="差异对比") as viewer:
        #     viewer.add_lines(lines)
    except Exception as e:
        console.print_error(str(e))
