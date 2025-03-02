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
import zipfile

import aiofiles
from aiopath import AsyncPath
from asyncio_pool import AioPool

from datahive.script.extraction.base_extraction import ExtractionStrategy


class ZipExtractionStrategy(ExtractionStrategy):
    support_types = [".zip"]

    async def extract_file(self, zip_file: zipfile.ZipFile, file_info: zipfile.ZipInfo,
                           input_dir: AsyncPath, output_dir: AsyncPath):
        target_path = output_dir / file_info.filename
        if await target_path.exists():
            await self.onupdate(input_dir, str(target_path))
            return
        # 如果目标路径是目录，则创建目录
        if file_info.is_dir():
            await target_path.mkdir(exist_ok=True, parents=True)
            await self.onupdate(input_dir, str(target_path))
        else:

            # 异步写入文件
            data = await self.read_file_data(zip_file, file_info)
            if data is None:
                return
            await target_path.parent.mkdir(exist_ok=True, parents=True)
            async with aiofiles.open(target_path, 'wb') as f:
                await f.write(data)
            await self.onupdate(input_dir, str(target_path))

    async def read_file_data(self, zip_file:zipfile.ZipFile, file_info:zipfile.ZipInfo):
        def read_file():
            try:
                with zip_file.open(file_info) as zf:
                    data = zf.read()
                return data
            except:
                return None

        return await asyncio.to_thread(read_file)

    async def extract(self, input_file: AsyncPath, output_file: AsyncPath):
        with zipfile.ZipFile(input_file) as zip_file:
            info_list = zip_file.infolist()
            await self.onsuccess(input_file, len(info_list))
            await output_file.mkdir(exist_ok=True, parents=True)
            async with AioPool(size=mp.cpu_count() * 10) as pool:
                for file_info in info_list:
                    # 提交任务到池中
                    await pool.spawn(self.extract_file(zip_file, file_info, input_file, output_file))


if __name__ == '__main__':
    from datahive.cli.cli_console import progress


    async def onsuccess(input_path: AsyncPath, total):
        progress.add_task(f"解压{input_path.name}", total)


    async def onupdate(input_path: AsyncPath, f: str):
        progress.update(f"解压{input_path.name}")
        await asyncio.sleep(2)


    async def main():
        zip_ext = ZipExtractionStrategy()
        zip_ext.onsuccess = onsuccess
        zip_ext.onupdate = onupdate
        input_path = AsyncPath(r"C:\Users\28938\Downloads\qBittorrent Enhanced Edition v4.5.3.10.zip")
        output_path = AsyncPath(r"D:\Project\Python\DataHive\Test2")
        await zip_ext.extract(input_path, output_path)


    progress.start()
    asyncio.run(main())
    progress.stop()
