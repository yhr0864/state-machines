import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()


def decorator_parallel_executor(func):
    """Decorator to execute a function in a thread."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Submit the function to the shared executor
        future = executor.submit(func, *args, **kwargs)
        return future

    return wrapper


async def sub_func_1():
    await asyncio.sleep(2)
    print("sub_func_1 finished")


async def sub_func_2():
    await asyncio.sleep(3)
    print("sub_func_2 finished")


async def main_func_1():
    """Main async function with subtasks."""
    print("Starting main_func_1")
    start_time = asyncio.get_event_loop().time()

    # Run sub-functions concurrently
    async with asyncio.TaskGroup() as tg:
        tg.create_task(sub_func_1())
        tg.create_task(sub_func_2())

    elapsed_time = asyncio.get_event_loop().time() - start_time
    print(f"main_func_1 finished in {elapsed_time:.2f} seconds")


@decorator_parallel_executor
def main_func_2():
    """Main blocking function."""
    print("Starting main_func_2")
    import time

    time.sleep(4)
    print("main_func_2 finished")


if __name__ == "__main__":
    overall_start_time = asyncio.get_event_loop().time()

    # Run async main_func_1 in the event loop
    asyncio.run(main_func_1())

    # Run main_func_2 in a separate thread
    main_func_2()

    overall_elapsed_time = asyncio.get_event_loop().time() - overall_start_time
    print(f"Total execution time: {overall_elapsed_time:.2f} seconds")
