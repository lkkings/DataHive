# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2025/3/2 21:30
@Author     : lkkings
@FileName:  : cli_view.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
from typing import List, Optional

from pynput import keyboard
from rich.box import ROUNDED
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


class Viewer:

    def __init__(self, title: str):
        self._console: Console = Console()
        self._scroll_offset: int = 0
        self._lines: List[Text] = []
        self._running: bool = True
        self._page_size: int = self._console.height - 6  # 保留边框空间
        self._title: str = title
        self._listener: Optional[keyboard.Listener] = None

    def __enter__(self):
        self._listener = keyboard.Listener(on_press=self.on_press)
        self._listener.start()
        return self

    def add_lines(self, lines: List[Text]):
        self._lines.extend(lines)

    def __exit__(self, exc_type, exc_val, exc_tb):
        with Live(console=self._console, refresh_per_second=30) as live:
            while self._running:
                live.update(self.render())
        self._listener.stop()
        return False

    def on_press(self, key):
        try:
            if key == keyboard.Key.up:
                self._scroll_offset = max(0, self._scroll_offset - 1)
            elif key == keyboard.Key.down:
                self._scroll_offset = min(
                    len(self._lines) - self._page_size,
                    self._scroll_offset + 1
                )
            elif key == keyboard.Key.page_up:
                self._scroll_offset = max(0, self._scroll_offset - self._page_size)
            elif key == keyboard.Key.page_down:
                self._scroll_offset = min(
                    len(self._lines) - self._page_size,
                    self._scroll_offset + self._page_size
                )
            elif key == keyboard.Key.esc:
                self._running = False
                return False
        except AttributeError:
            pass

    def render(self):
        content = Text()
        start = self._scroll_offset
        end = start + self._page_size

        for line in self._lines[start:end]:
            content.append(line)
            content.append("\n")

        # 构建状态栏信息
        info = Text.from_markup(
            f" [cyan]行 {start + 1}-{min(end, len(self._lines))}[/] "
            f"[green]总行数: {len(self._lines)}[/] "
            "[yellow]↑/↓ 滚动 [/][magenta]PgUp/PgDn 翻页[/][red] ESC 退出[/]"
        )

        return Panel(
            content,
            title=f"[bold]{self._title}[/]",
            subtitle=info,
            border_style="blue",
            box=ROUNDED,
            padding=(1, 2)
        )
