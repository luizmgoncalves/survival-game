from time import time


class Debug:
    _timers = {}
    _statistics = {}

    @classmethod
    def start_timer(cls, name: str):
        """Start a timer for a given name."""
        cls._timers[name] = time()

    @classmethod
    def stop_timer(cls, name: str):
        """Stop the timer for the given name and update statistics."""
        start_time = cls._timers.get(name)
        if start_time is None:
            print(f"Timer '{name}' not found.")
            return None

        elapsed_time = time() - start_time
        min_time, max_time, total_time, count = cls._statistics.get(name, (float("inf"), 0, 0, 0))

        # Update statistics
        min_time = min(min_time, elapsed_time)
        max_time = max(max_time, elapsed_time)
        total_time += elapsed_time
        count += 1

        cls._statistics[name] = (min_time, max_time, total_time, count)

        return elapsed_time

    @classmethod
    def show_statistics(cls):
        """Display the statistics for all timers."""
        print("Timer Statistics:")
        for name, (min_time, max_time, total_time, count) in cls._statistics.items():
            mean_time = total_time / count if count > 0 else 0
            print(f"  {name}:")
            print(f"    Min time: {min_time * 1000:.2f} ms")
            print(f"    Max time: {max_time * 1000:.2f} ms")
            print(f"    Mean time: {mean_time * 1000:.2f} ms")
