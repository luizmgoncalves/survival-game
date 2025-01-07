import time

class Scheduler:
    def __init__(self):
        self.tasks = []

    def schedule(self, func, args, time_to_trigger):
        """
        Schedules a function to be executed after the given time_to_trigger in seconds.

        :param func: The function to execute.
        :param args: A tuple of arguments to pass to the function.
        :param time_to_trigger: Time in seconds after which the function will be executed.
        """
        trigger_time = time.time() + time_to_trigger
        self.tasks.append((trigger_time, func, args))

    def update(self, delta_time):
        """
        Updates the scheduler and executes any due tasks.

        :param delta_time: The time elapsed since the last update in seconds.
        """
        current_time = time.time()
        for task in self.tasks[:]:
            trigger_time, func, args = task
            if current_time >= trigger_time:
                func(*args)
                self.tasks.remove(task)

SCHEDULER = Scheduler()

if __name__ == "__main__":
    # Example usage
    def say_hello(name):
        print(f"Hello, {name}!")

    def add_numbers(a, b):
        print(f"The sum of {a} and {b} is {a + b}.")

    scheduler = Scheduler()

    # Schedule tasks
    scheduler.schedule(say_hello, ("Alice",), 2)  # Will trigger in 2 seconds
    scheduler.schedule(add_numbers, (5, 7), 5)   # Will trigger in 5 seconds

    # Simulate a main loop
    start_time = time.time()
    while scheduler.tasks:
        elapsed_time = time.time() - start_time
        scheduler.update(elapsed_time)
        time.sleep(0.1)
