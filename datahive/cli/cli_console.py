import json
import shutil
import struct
import threading
import time
from pathlib import Path
import shutil
import multiprocessing.shared_memory as shm

import psutil
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.console import Console
from rich.progress import (
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    ProgressColumn, Progress,
)
from rich.style import Style
from rich.text import Text

from datahive.utils.share_meory_util import SharedMemoryDict

HACK_STYLE = Style(color="#00ff00", bgcolor="#000000", bold=True)
HACK_BAR_STYLE = Style(color="#00ff00", bgcolor="#000000")
HACK_TEXT_STYLE = Style(color="#00ff00", bold=True)

FONT_MAX_LENGTH = shutil.get_terminal_size().columns // 5


def get_system_status():
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    return (
        f"内存: {memory.percent}% | "
        f"CPU: {cpu_percent}%"
    )


class StateColumn(ProgressColumn):
    """根据任务状态显示图标（✅ 成功 / ❌ 失败）"""

    def render(self, task) -> str:
        state = task.fields.get("state", "running")
        if state == "success":
            return "[bold green]✅  [/]"
        elif state == "warning":
            return "[bold yellow]⚠️  [/]"
        elif state == "failed":
            return "[bold red]❌  [/]"
        else:
            return "[bold yellow]⌛  [/]"  # 默认显示加载中


# 定义任务结构
# 假设任务名称最大长度为 20 个字符（20 bytes），完成量和总量各为 4 字节整数
TASK_NAME_MAX_LENGTH = 20
TASK_STRUCT_FORMAT = f"{TASK_NAME_MAX_LENGTH}sii"  # 20s: 字符串, i: 整数, i: 整数
TASK_STRUCT_SIZE = struct.calcsize(TASK_STRUCT_FORMAT)


class ProgressManager(threading.Thread):
    __slots__ = (
        "_progress",
        "_layout",
        "_console",
        "_running",
        "_title",
        "_util",
        "_shm_dict_key",
        "_shm_dict",
        "_refresh_per_second"
    )

    def __init__(self, title: str = "任务进度UI", util="it", refresh_per_second=0.2):
        super().__init__()
        self._progress = Progress(
            StateColumn(),
            TextColumn("[bold green]{task.description:<" + f"{FONT_MAX_LENGTH}" + "}", style=HACK_TEXT_STYLE),
            BarColumn(
                bar_width=None,
                complete_style=HACK_BAR_STYLE,
                finished_style=HACK_BAR_STYLE,
            ),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%", style=HACK_TEXT_STYLE),
            TextColumn("•", style=HACK_TEXT_STYLE),
            TextColumn("[bold green]ETA", style=HACK_TEXT_STYLE),
            TimeRemainingColumn(),
            TextColumn("{task.fields[speed]}", style=HACK_TEXT_STYLE),
            expand=True,
        )
        self._layout = Layout()
        self._console = Console()
        self._running = False
        self._title = title
        self._util = util
        self._refresh_per_second = refresh_per_second
        self._shm_dict_key = f"task_shm_dict"
        self._shm_dict = SharedMemoryDict(self._shm_dict_key, size=1024, create=True, initial_data={})

    def stop(self):
        self._running = False
        self.join()
        self._shm_dict.unlink()

    def _make_layout(self):
        # 创建布局
        self._layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3),
        )
        self._layout["header"].update(
            Panel(
                Text(self._title, justify="center", style="bold green"),
                style=HACK_STYLE,
            )
        )
        self._layout["main"].update(self._progress)
        self._layout["footer"].update(
            Panel(
                Text(get_system_status(), justify="center", style="green"),
                style=HACK_STYLE,
            )
        )

    def add_task(self, task_name: str, total: int):
        with SharedMemoryDict(self._shm_dict_key, size=1024) as write_shm_dict:
            write_shm_dict[task_name] = {
                "total": total,
                "completed": 0,
                "state": "running"
            }

    def update(self, task_name: str, advance: int = 1):
        with SharedMemoryDict(self._shm_dict_key, size=1024) as write_shm_dict:
            task = write_shm_dict[task_name].copy()
            task["completed"] = task["completed"]+ advance
            write_shm_dict[task_name] = task

    def failed(self, task_name: str):
        with SharedMemoryDict(self._shm_dict_key, size=1024) as write_shm_dict:
            task = write_shm_dict[task_name].copy()
            task["state"] = "failed"
            write_shm_dict[task_name] = task

    def run(self):
        self._running = True
        self._make_layout()
        task_ids = {}
        task_states = {}
        task_time = {}

        def _flash(is_end=False):
            with SharedMemoryDict(self._shm_dict_key, size=1024) as read_shm_dict:
                for task_name, _task in read_shm_dict.items():
                    task = _task.copy()
                    now_time = time.time()
                    completed = task["completed"]
                    total = task["total"]
                    if task_name not in task_ids:
                        task_id = self._progress.add_task(
                            task_name,
                            total=total,
                            speed=f"速度: 0 {self._util}/s",
                        )
                        task_ids[task_name] = task_id
                    else:
                        task_id = task_ids[task_name]
                        speed = (completed - task_states[task_name]) / (now_time - task_time[task_name])
                        self._progress.update(
                            task_id,
                            completed=completed,
                            speed=f"速度: {speed:0.2f} {self._util}/s"
                        )
                    task_states[task_name] = completed
                    task_time[task_name] = now_time
                    if completed == total:
                        self._progress.update(
                            task_id,
                            state="success"
                        )
                    if task['state'] == "failed":
                        self._progress.update(
                            task_id,
                            state="failed"
                        )
                    if is_end and total != completed:
                        self._progress.update(
                            task_id,
                            state="warning"
                        )

            self._layout["footer"].update(
                Panel(
                    Text(get_system_status(), justify="center", style="green"),
                    style=HACK_STYLE,
                )
            )

        with Live(self._layout, console=self._console, refresh_per_second=self._refresh_per_second) as live:
            while self._running:
                _flash(is_end=False)
                time.sleep(self._refresh_per_second)
            _flash(is_end=True)


class RichConsoleManager:
    """
    主控制台管理类 (Main console management class)
    """

    def __init__(self):
        self._console = Console()

    @property
    def rich_prompt(self) -> Prompt:
        return Prompt()

    def print_error(self, message: str):
        error_text = Text(f"❌ {message}", style="bold red")
        self._console.print(Panel(error_text, title="错误", border_style="red"))

    # 输出成功信息
    def print_success(self, message):
        success_text = Text(f"✅ {message}", style="bold green")
        self._console.print(Panel(success_text, title="成功", border_style="green"))

    def print_json(self, json_data: str):
        try:
            json.loads(json_data)
        except json.JSONDecodeError:
            self.print_error("JSON 格式错误")
        else:
            self._console.print_json(json_data)


console = RichConsoleManager()
progress = ProgressManager()
