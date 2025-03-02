# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2025/3/2 14:39
@Author     : lkkings
@FileName:  : share_meory_util.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import json
import threading
from typing import Optional, Any
import multiprocessing.shared_memory as shm


class SharedMemoryDict(dict):
    def __init__(self, name: str, size: int = 1024, create: bool = False, initial_data: Optional[dict] = None):
        """
        初始化共享内存字典

        :param name: 共享内存的名称
        :param size: 共享内存的大小（字节）
        :param create: 是否创建新的共享内存
        :param initial_data: 初始数据（仅当 create=True 时有效）
        """
        self._shm_name = name
        self._shm_size = size
        self._lock = threading.Lock()  # 用于线程安全的锁

        if create:
            try:
                # 创建共享内存
                self._shm = shm.SharedMemory(name=name, create=create, size=size)
                if initial_data is not None:
                    self._save_to_shm(initial_data)  # 初始化数据
            except FileExistsError:
                self._shm = shm.SharedMemory(name=name)
        else:
            # 附加到现有的共享内存
            self._shm = shm.SharedMemory(name=name)

        # 从共享内存加载数据
        self._load_from_shm()

    def _load_from_shm(self):
        """从共享内存加载数据到字典"""
        with self._lock:  # 加锁确保线程安全
            try:
                data = json.loads(bytes(self._shm.buf[:]).rstrip(b'\0').decode('utf8'))
            except json.JSONDecodeError:
                data = {}
            super().update(data)

    def _save_to_shm(self, data: Optional[dict] = None):
        """将字典数据保存到共享内存"""
        with self._lock:  # 加锁确保线程安全
            if data is None:
                data = self
            serialized_data = json.dumps(data).encode('utf-8')
            if len(serialized_data) > self._shm_size:
                raise ValueError("数据大小超过共享内存容量")
            self._shm.buf[:len(serialized_data)] = serialized_data

    def __getitem__(self, key: Any) -> Any:
        """重写 __getitem__，确保每次访问都从共享内存加载最新数据"""
        self._load_from_shm()
        return super().__getitem__(key)

    def __setitem__(self, key: Any, value: Any):
        """重写 __setitem__，确保修改同步到共享内存"""
        super().__setitem__(key, value)
        self._save_to_shm()

    def __delitem__(self, key: Any):
        """重写 __delitem__，确保修改同步到共享内存"""
        super().__delitem__(key)
        self._save_to_shm()

    def update(self, *args, **kwargs):
        """重写 update，确保修改同步到共享内存"""
        super().update(*args, **kwargs)
        self._save_to_shm()

    def close(self):
        """关闭共享内存"""
        self._shm.close()

    def unlink(self):
        """释放共享内存"""
        self._shm.unlink()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时关闭共享内存"""
        self.close()
