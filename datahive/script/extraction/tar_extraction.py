# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2025/3/2 1:30
@Author     : lkkings
@FileName:  : zip_extraction.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import asyncio
import multiprocessing as mp
import tarfile
import threading

import aiofiles
from aiopath import AsyncPath
from asyncio_pool import AioPool

from datahive.script.extraction.base_extraction import ExtractionStrategy


class TarExtractionStrategy(ExtractionStrategy):
    support_types = [".tar.bz2", ".tar.xz"]

    def __init__(self):

        super().__init__()
        self.lock = threading.Lock()

    async def extract_file(self, tar_file: tarfile.TarFile, file_info: tarfile.TarInfo,
                           input_dir: AsyncPath, output_dir: AsyncPath):
        target_path = output_dir / file_info.name
        if await target_path.exists():
            await self.onupdate(input_dir, str(target_path))
            return
        if file_info.isdir():
            await target_path.mkdir(exist_ok=True, parents=True)
            await self.onupdate(input_dir, str(target_path))
        else:
            data = await self.read_file_data(tar_file, file_info)
            if data:
                await target_path.parent.mkdir(exist_ok=True, parents=True)
                async with aiofiles.open(target_path, 'wb') as f:
                    await f.write(data)
                await self.onupdate(input_dir, str(target_path))

    async def read_file_data(self, tar_file: tarfile.TarFile, file_info: tarfile.TarInfo):
        def read_file():
            with self.lock:
                try:
                    with tar_file.extractfile(file_info) as file:
                        data = file.read()
                        return data
                except:
                    return None


        return await asyncio.to_thread(read_file)

    async def extract(self, input_file: AsyncPath, output_file: AsyncPath):
        with tarfile.open(input_file, 'r:*') as tar_file:
            info_list = tar_file.getmembers()
            if self.onsuccess:
                await self.onsuccess(input_file, len(info_list))
            await output_file.mkdir(exist_ok=True, parents=True)
            async with AioPool(size=mp.cpu_count() * 10) as pool:
                for file_info in info_list:
                    # 提交任务到池中
                    await pool.spawn(self.extract_file(tar_file, file_info, input_file, output_file))


class TarGzExtractionStrategy(TarExtractionStrategy):
    support_types = [".tar.gz"]

    async def extract(self, input_file: AsyncPath, output_file: AsyncPath):
        output_file = output_file.with_suffix('')
        with tarfile.open(input_file, 'r:gz') as tar_file:
            info_list = tar_file.getmembers()
            await self.onsuccess(input_file, len(info_list))
            await output_file.mkdir(exist_ok=True, parents=True)
            async with AioPool(size=mp.cpu_count() * 10) as pool:
                for file_info in info_list:
                    # 提交任务到池中
                    await pool.spawn(self.extract_file(tar_file, file_info, input_file, output_file))
