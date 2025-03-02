# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2025/2/22 22:20
@Author     : lkkings
@FileName:  : base_extraction.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import asyncio
from concurrent.futures import ProcessPoolExecutor

import aiofiles
from aiopath import AsyncPath
from typing import Optional

from datahive.cli.cli_console import progress, console
from datahive.script.extraction import factory
from datahive.utils.async_util import run_new_loop


async def _read_task_list(task_list):
    if not task_list.endswith('.task'):
        raise ValueError('任务列表应为 "*.task" 格式')
    arg_list = []
    async with aiofiles.open(task_list, 'r', encoding='utf-8') as f:
        index = 0
        try:
            while True:
                line = await f.readline()
                if not line:
                    break
                index += 1
                arg = line.split('|')
                if len(arg) == 1 and arg[0].strip():
                    _input_file = AsyncPath(arg[0].strip())
                    if not _input_file.is_absolute():
                        raise Exception(f'路径必须为绝对路径 -> {_input_file}')
                    if not await _input_file.exists():
                        raise FileNotFoundError(f'文件不存在 -> {_input_file}')
                    arg_list.append((_input_file, None))
                elif len(arg) == 2 and arg[0].strip():
                    _input_file = AsyncPath(arg[0].strip())
                    if not await _input_file.exists():
                        raise FileNotFoundError(f'文件不存在 -> {_input_file}')
                    _output_file = AsyncPath(arg[1].strip())
                    if not _output_file.is_absolute():
                        raise Exception(f'路径必须为绝对路径 -> {_output_file}')
                    arg_list.append((_input_file, _output_file))
                else:
                    raise Exception(f'格式错误，应为 INPUT_FILE|OUTPUT_FILE')
        except Exception as e:
            raise FileExistsError(f'第{index}行存在错误:{e}')
    return arg_list


async def _extract(input_file: str, output_file: Optional[str]):
    async def onsuccess(input_path: AsyncPath, total):
        progress.add_task(f"解压{input_path.name}", total)

    async def onupdate(input_path: AsyncPath, f: str):
        progress.update(f"解压{input_path.name}")

    input_file = AsyncPath(input_file)
    input_file = await input_file.absolute()
    if output_file is None:
        output_file = input_file.with_suffix('')
    output_file = AsyncPath(output_file)
    output_file = await output_file.absolute()
    file_extension = ''.join(input_file.suffixes)
    extraction = factory.get_strategy(file_extension)
    extraction.onsuccess = onsuccess
    extraction.onupdate = onupdate
    await extraction.extract(input_file, output_file)


async def run(input_file: str, output_file: Optional[str]):
    progress.start()
    try:
        await _extract(input_file, output_file)
    except Exception as e:
        console.print_error(str(e))
    finally:
        progress.stop()


async def batch_run(task_list: str, max_workers: int):
    try:
        args = await _read_task_list(task_list)
        assert len(args) > 0, f'未发现任务 -> {task_list}'
    except Exception as e:
        console.print_error(str(e))
        return
    progress.start()
    try:
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            for input_file, output_file in args:
                loop.run_in_executor(pool, run_new_loop, _extract, input_file, output_file)
    except Exception as e:
        console.print_error(str(e))
    finally:
        progress.stop()


if __name__ == '__main__':
    pass
