# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2025/3/1 21:31
@Author     : lkkings
@FileName:  : async_util.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import asyncio
from typing import List, Callable, Any
from functools import wraps

from loguru import logger


def async_with_timeout(timeout: float):
    """
    修饰器：为异步函数添加超时功能。

    :param timeout: 超时时间（秒）
    :return: 修饰后的函数
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout)
            except asyncio.TimeoutError:
                raise asyncio.TimeoutError(f"任务超时，超过 {timeout} 秒")

        return wrapper

    return decorator


def async_with_concurrency(max_concurrency: int = 5):
    """
    修饰器：为异步函数添加并发控制功能。

    :param max_concurrency: 最大并发数
    :return: 修饰后的函数
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def async_with_retry(retries: int = 3, delay: float = 1):
    """
    修饰器：为异步函数添加重试功能。

    :param retries: 最大重试次数
    :param delay: 每次重试的延迟时间（秒）
    :return: 修饰后的函数
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries - 1:
                        raise e
                    await asyncio.sleep(delay)
                    logger.debug(f"重试中... ({attempt + 1}/{retries})")

        return wrapper

    return decorator


def async_logger(func):
    """
    修饰器：为异步函数添加日志记录功能。
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = asyncio.get_event_loop().time()
        logger.debug(f"开始执行: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            end_time = asyncio.get_event_loop().time()
            logger.debug(f"执行完成: {func.__name__}, 耗时: {end_time - start_time:.2f} 秒")
            return result
        except Exception as e:
            logger.debug(f"执行失败: {func.__name__}, 错误: {e}")
            raise

    return wrapper


def run_async_func(func):
    """
    修饰器：为异步函数添加日志记录功能。
    """
    if not asyncio.iscoroutinefunction(func):
        raise Exception(f'{func.__name__} i不是一个异步函数')

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = asyncio.run(func(*args, **kwargs))
        return result

    return wrapper


def run_new_loop(func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(func(*args, **kwargs))
    except Exception as e:
        logger.debug(f"捕获异常: {e}")
        raise
    finally:
        loop.close()
        asyncio.set_event_loop(None)


if __name__ == '__main__':
    # 示例使用
    @async_logger
    @async_with_retry(retries=3, delay=1)
    @async_with_timeout(timeout=2)
    async def example_task():
        await asyncio.sleep(1)
        return "任务完成"


    @async_logger
    @async_with_concurrency(max_concurrency=2)
    async def example_concurrent_task(task_id: int):
        await asyncio.sleep(1)
        return f"任务 {task_id} 完成"


    async def main():
        # 示例 1: 超时和重试
        try:
            result = await example_task()
            print(result)
        except Exception as e:
            print(f"任务失败: {e}")

        # 示例 2: 并发控制
        tasks = [example_concurrent_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        print(results)


    # 运行主函数
    asyncio.run(main())
