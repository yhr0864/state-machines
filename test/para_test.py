import functools
from concurrent.futures import ThreadPoolExecutor
import time

# Global thread pool
executor = ThreadPoolExecutor()


def decorator_parallel_executor(func):
    """Decorator to execute a function in a thread."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Submit the function to the shared executor
        future = executor.submit(func, *args, **kwargs)
        return future

    return wrapper


@decorator_parallel_executor
def sub_func_1():
    """Simulates a sub-function with a delay."""
    print("sub_func_1 started")
    time.sleep(2)
    print("sub_func_1 finished")


@decorator_parallel_executor
def sub_func_2():
    """Simulates another sub-function with a delay."""
    print("sub_func_2 started")
    time.sleep(2)
    print("sub_func_2 finished")


@decorator_parallel_executor
def example_function_main():
    """Main function 1 that runs subtasks."""
    print("main 1 started")
    start_time = time.time()

    # Start sub-functions
    future1 = sub_func_1()
    future2 = sub_func_2()

    # Wait for sub-functions to complete
    future1.result()
    future2.result()

    print("main 1 doing additional work")
    time.sleep(2)  # Simulate more work
    elapsed_time = time.time() - start_time
    print(f"main 1 finished in {elapsed_time:.2f} seconds")


@decorator_parallel_executor
def example_function_main2():
    """Main function 2 with its own task."""
    print("main 2 started")
    time.sleep(4)
    print("main 2 finished")


if __name__ == "__main__":
    start_time = time.time()

    # Run both main functions in parallel
    main1_future = example_function_main()
    main2_future = example_function_main2()

    # Wait for both main functions to complete
    main1_future.result()
    main2_future.result()

    total_elapsed_time = time.time() - start_time
    print(f"Total execution time: {total_elapsed_time:.2f} seconds")

    # Shutdown the executor gracefully
    executor.shutdown()
