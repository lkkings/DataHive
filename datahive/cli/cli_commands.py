import re
import sys

import click
from typing import Optional, Union, Any
import multiprocessing as mp

from loguru import logger

import datahive
from datahive import helps
from datahive.script import unzip
from datahive.script import diff
from datahive.utils.async_util import run_async_func


# 处理帮助信息
def handle_help(
        ctx: click.Context,
        param: Union[click.Option, click.Parameter],
        value: Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return
    helps.main()
    ctx.exit()


# 处理版本号
def handle_version(
        ctx: click.Context,
        param: Union[click.Option, click.Parameter],
        value: Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"Version {datahive.__version__}")
    ctx.exit()


# 处理debug
def handle_debug(
        ctx: click.Context,
        param: Union[click.Option, click.Parameter],
        value: Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return
    from rich.traceback import install
    install()
    logger.remove(0)
    logger.add(sys.stdout, level="value")
    logger.debug("开启调试模式 (Debug mode on)")


# 主命令
@click.group(name='dh')
@click.option(
    "--help",
    "-h",
    "help",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=handle_help,
)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=handle_version,
)
@click.option(
    "--debug",
    "-d",
    type=click.Choice(["DEBUG", "INFO", "ERROR", "WARNING"]),
    is_eager=True,
    expose_value=False,
    callback=handle_debug,
)
@click.pass_context
def main(ctx) -> None:
    pass


@main.command(
    "unzip",
    help="解压文件的命令行工具\n\n"
         "INPUT_FILE: 输入文件的路径\n"
         "OUTPUT_FILE: 输出文件的路径"
)
@click.argument(
    "input_file",
    type=click.Path(exists=True),
    nargs=1,
    required=False,
)
@click.argument(
    "output_file",
    type=click.Path(exists=False),
    nargs=1,
    required=False
)
@click.option(
    "--task_list",
    type=click.Path(exists=True),
    nargs=1,
    required=False
)
@click.option(
    "--max_workers",
    "-P",
    type=int,
    default=mp.cpu_count() * 4,
    required=False
)
@click.pass_context
@run_async_func
async def unzip_command(ctx, input_file: str, output_file: Optional[str], task_list: Optional[str], max_workers: int) -> None:
    if task_list:
        await unzip.batch_run(task_list, max_workers)
    else:
        await unzip.run(input_file, output_file)


@main.command(
    "diff",
    help="字符串差异比对的命令行工具\n\n"
)
@click.option('-f1', '--file1', type=click.Path(exists=True), help="原始文件路径")
@click.option('-f2', '--file2', type=click.Path(exists=True), help="新文件路径")
@click.option('-t1', '--text1', type=str, help="原始文本")
@click.option('-t2', '--text2', type=str, help="新文本")
@click.pass_context
def diff_command(ctx, file1: Optional[str], file2: Optional[str], text1: Optional[str], text2: Optional[str]):
    diff.run(file1, file2, text1, text2)


@main.command(
    "look",
    help="文本查看的命令行工具\n\n"
)
@click.argument(
    "input_file",
    type=click.Path(exists=True),
    nargs=1,
    required=True,
)
@click.option('-re', '--regx', type=str, help="匹配正则表达式")
@click.pass_context
def look_command(ctx, input_file: str, regx: Optional[str]):
    pass


if __name__ == "__main__":
    main()
