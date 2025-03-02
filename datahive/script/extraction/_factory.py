# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2025/3/2 5:13
@Author     : lkkings
@FileName:  : _factory.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import importlib
import inspect
import os
from pathlib import Path
from typing import Dict, Type, List

from datahive.script.extraction.base_extraction import ExtractionStrategy


def import_strategy() -> List[ExtractionStrategy]:
    folder_path = Path(__file__).parent.resolve()
    instances = []
    for file_path in folder_path.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
        module_name = file_path.stem
        module = importlib.import_module(f"datahive.script.extraction.{module_name}")

        # 获取模块中的所有类
        classes = [cls for name, cls in inspect.getmembers(module, inspect.isclass)]
        # 筛选出 base_class 的子类
        for cls in classes:
            if issubclass(cls, ExtractionStrategy) and cls != ExtractionStrategy:
                instances.append(cls())
    return instances


# ------------------------------
# 策略工厂类：管理解压策略的注册与获取
# ------------------------------
class ExtractionStrategyFactory:
    """解压策略工厂，支持动态注册新格式"""

    def __init__(self):
        self._strategies: List[ExtractionStrategy] = []

    @property
    def strategies(self):
        if len(self._strategies) == 0:
            self._strategies = import_strategy()
        return self._strategies

    def get_strategy(self, file_extension: str) -> ExtractionStrategy:
        """根据文件扩展名获取解压策略"""
        for strategy in self.strategies:
            for support_type in strategy.support_types:
                if file_extension.endswith(support_type):
                    return strategy
        raise ValueError(f"不支持的文件类型: {file_extension}")


factory = ExtractionStrategyFactory()
