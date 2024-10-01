import time
from multiprocessing import Process, Queue


def fun1(queue):
    while True:
        if not queue.empty():  # Check if there's any input
            user_input = queue.get()
            print(f"Received input: {user_input}")

        # Simulate continuous task in the background
        print("fun1 running...")
        time.sleep(1)  # Simulating a task that runs continuously


def get_input(queue):
    while True:
        user_input = input("Enter something: ")  # Main process handles input
        queue.put(user_input)  # Send input to the queue for fun1 to handle


if __name__ == "__main__":
    try:
        queue = Queue()  # Shared queue for communication

        # Start the background process (fun1) that runs continuously
        p1 = Process(target=fun1, args=(queue,))
        p1.start()

        # Handle input in the main process and send it to fun1 via the queue
        get_input(queue)

        p1.join()

    except KeyboardInterrupt:
        print("Stopping the processes...")
        p1.terminate()  # Gracefully stop the background process
        p1.join()  # Ensure process is terminated
