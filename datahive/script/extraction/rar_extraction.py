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
import threading

import rarfile

import aiofiles
from aiopath import AsyncPath
from asyncio_pool import AioPool

from datahive.script.extraction.base_extraction import ExtractionStrategy


class RarExtractionStrategy(ExtractionStrategy):
    support_types = [".rar"]

    async def extract_file(self, rar_file: rarfile.RarFile, file_info: rarfile.RarInfo,
                           input_dir: AsyncPath, output_dir: AsyncPath):
        target_path = output_dir / file_info.filename
        if await target_path.exists():
            await self.onupdate(input_dir, str(target_path))
            return
        if file_info.is_dir():
            await target_path.mkdir(exist_ok=True, parents=True)
            await self.onupdate(input_dir, str(target_path))
        else:
            data = await self.read_file_data(rar_file, file_info)
            if data:
                await target_path.parent.mkdir(exist_ok=True, parents=True)
                async with aiofiles.open(target_path, 'wb') as f:
                    await f.write(data)
                await self.onupdate(input_dir, str(target_path))

    async def read_file_data(self, rar_file: rarfile.RarFile, file_info: rarfile.RarInfo):
        def read_file():
            try:
                with rar_file.open(file_info) as f:
                    data = f.read()
                return data
            except:
                return None

        return await asyncio.to_thread(read_file)

    async def extract(self, input_file: AsyncPath, output_file: AsyncPath):
        with rarfile.RarFile(input_file) as rar_file:
            info_list = rar_file.infolist()
            if self.onsuccess:
                await self.onsuccess(input_file, len(info_list))
            await output_file.mkdir(exist_ok=True, parents=True)
            async with AioPool(size=mp.cpu_count() * 10) as pool:
                for file_info in info_list:
                    # 提交任务到池中
                    await pool.spawn(self.extract_file(rar_file, file_info, input_file, output_file))

