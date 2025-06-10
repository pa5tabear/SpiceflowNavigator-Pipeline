import asyncio
from collections.abc import Awaitable, Callable

async def run_task(task: Callable[[], Awaitable[None]]) -> None:
    await task()

async def run_sequential(tasks: list[Callable[[], Awaitable[None]]]) -> None:
    for task in tasks:
        await run_task(task)

async def run_parallel(tasks: list[Callable[[], Awaitable[None]]]) -> None:
    await asyncio.gather(*(run_task(t) for t in tasks))
