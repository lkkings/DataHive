# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2025/3/2 19:11
@Author     : lkkings
@FileName:  : diff.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import difflib
from pathlib import Path
from typing import Optional

from rich.text import Text

from datahive.cli.cli_console import console
from datahive.cli.cli_view import Viewer


def _char_diff(old_line, new_line):
    """生成字符级差异标记（返回旧行和新行的Text对象）"""
    text_old = Text()
    text_new = Text()
    sm = difflib.SequenceMatcher(None, old_line, new_line)

    for opcode in sm.get_opcodes():
        tag, i1, i2, j1, j2 = opcode
        old_part = old_line[i1:i2]
        new_part = new_line[j1:j2]

        if tag == 'equal':
            text_old.append(old_part)
            text_new.append(new_part)
        elif tag == 'delete':
            text_old.append(old_part, style="red")
        elif tag == 'insert':
            text_new.append(new_part, style="green")
        elif tag == 'replace':
            text_old.append(old_part, style="red")
            text_new.append(new_part, style="green")

    return text_old, text_new


def _generate_diff_lines(text1, text2):
    """生成带行号和字符差异的文本行"""
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    line_count = min(len(lines1), len(lines2))
    diff_lines = []

    for i in range(line_count):
        # 生成行号标签
        line_no = Text(f"{i + 1:4} ", style="bold cyan")

        # 生成字符级差异
        old_line, new_line = _char_diff(lines1[i], lines2[i])

        # 构建对比行
        line = Text()
        line.append(line_no)
        line.append(old_line)
        line.append(" → ", style="bold yellow")
        line.append(new_line)

        diff_lines.append(line)

    return diff_lines


def run(file1: Optional[str], file2: Optional[str], text1: Optional[str], text2: Optional[str]):
    try:
        # 输入验证
        if (file1 or file2) and (text1 or text2):
            raise Exception("不能同时使用文件和文本输入")
        # 读取输入
        if file1 and file2:
            text1 = Path(file1).read_text(encoding='utf-8')
            text2 = Path(file2).read_text(encoding='utf-8')
        elif text1 and text2:
            text1 = text1.replace('\\n', '\n')
            text2 = text2.replace('\\n', '\n')
        else:
            raise Exception("需要提供两个输入源")
        lines = _generate_diff_lines(text1, text2)
        with Viewer(title="差异对比") as viewer:
            viewer.add_lines(lines)
    except Exception as e:
        console.print_error(str(e))
