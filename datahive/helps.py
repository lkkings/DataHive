# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/10/14 20:37
@Author     : lkkings
@FileName:  : helps.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import importlib

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import datahive


def main() -> None:
    # 真彩
    console = Console(color_system="truecolor")
    console.print(f"\n:rocket: [bold]datahive {datahive.__version__} :rocket:", justify="center")
    console.print(f"\n[i]{datahive.__description_cn__}", justify="center")
    console.print(f"[i]{datahive.__description_en__}", justify="center")
    console.print(f"[i]GitHub {datahive.__repourl__}\n", justify="center")

    # 使用方法
    table = Table.grid(padding=1, pad_edge=True)
    table.add_column("Usage", no_wrap=True, justify="left", style="bold")
    console.print(
        Panel(table, border_style="bold", title="使用方法 | Usage", title_align="left")
    )

    # 应用列表
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("参数", no_wrap=True, justify="left", style="bold")
    table.add_column("描述", no_wrap=True, style="bold")
    table.add_column("状态", no_wrap=True, justify="left", style="bold")
    table.add_row("unzip", "解压文件的命令行工具", "🧪")
    table.add_row("diff", "字符串差异比对的命令行工具", "🧪")
    table.add_row("look", "文本查看的命令行工具", "💻")

    table.add_row(
        "Issues❓", "[link=https://github.com/lkkings/DataHive/issues]Click Here[/]"
    ),
    table.add_row(
        "Document📕", "[link=]Click Here[/]"
    )
    console.print(
        Panel(
            table,
            border_style="bold",
            title="datahive",
            title_align="left",
            subtitle="欢迎提交PR适配更多网站或添加功能",
        )
    )


if __name__ == "__main__":
    main()
