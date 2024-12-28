from time import time


class Debug:
    def __init__(self):
        self._timers = {}
        self._statistics = {}

    def start_timer(self, name: str):
        """Start a timer for a given name."""
        self._timers[name] = time()

    def stop_timer(self, name: str):
        """Stop the timer for the given name and update statistics."""
        start_time = self._timers.get(name)
        if start_time is None:
            print(f"Timer '{name}' not found.")
            return None

        elapsed_time = time() - start_time
        min_time, max_time, total_time, count = self._statistics.get(name, (float("inf"), 0, 0, 0))

        # Update statistics
        min_time = min(min_time, elapsed_time)
        max_time = max(max_time, elapsed_time)
        total_time += elapsed_time
        count += 1

        self._statistics[name] = (min_time, max_time, total_time, count)

        return elapsed_time

    def show_statistics(self):
        """Display the statistics for all timers."""
        print("Timer Statistics:")
        for name, (min_time, max_time, total_time, count) in self._statistics.items():
            mean_time = total_time / count if count > 0 else 0
            print(f"  {name}:")
            print(f"    Min time: {min_time * 1000:.2f} ms")
            print(f"    Max time: {max_time * 1000:.2f} ms")
            print(f"    Mean time: {mean_time * 1000:.2f} ms")
