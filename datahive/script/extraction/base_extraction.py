# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2025/3/2 1:27
@Author     : lkkings
@FileName:  : base_extraction.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
from abc import abstractmethod, ABC
from typing import Callable, Awaitable, Optional

from aiopath import AsyncPath

async def async_empty_fun(*args,**kwargs):
    pass
class ExtractionStrategy(ABC):
    support_types = []

    def __init__(self):
        self.file_count = 0
        self.onsuccess: Optional[Callable[[AsyncPath, int], Awaitable[None]]] = async_empty_fun
        self.onupdate: Optional[Callable[[AsyncPath, str], Awaitable[None]]] = async_empty_fun

    @abstractmethod
    async def extract(self, input_file: AsyncPath, output_file: AsyncPath) -> None:
        raise NotImplementedError
