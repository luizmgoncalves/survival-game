from typing import List


class Animation:
    def __init__(self, frame_names: List[str], update_interval: float, run_once: bool = False):
        """
        Initialize the animation with frame names and update interval.

        :param frame_names: List of frame names (strings).
        :param update_interval: Time in seconds between frame updates.
        :param run_once: Whether the animation should stop on the last frame.
        """
        self.frame_names     : List[str] = frame_names
        self.update_interval : float = update_interval
        self.run_once        : bool = run_once
        self.current_index   : int   = 0
        self.elapsed_time    : float = 0.0
        self.completed       : bool  = False  # Tracks if the animation has completed when run_once is True

    def update(self, delta_time: float) -> None:
        """
        Update the animation frame based on the elapsed time.

        :param delta_time: Time passed since the last update call (in seconds).
        """
        if self.run_once and self.completed:
            return  # Do not update if animation is complete

        self.elapsed_time += delta_time

        if self.elapsed_time >= self.update_interval:
            self.elapsed_time -= self.update_interval
            self.current_index += 1

            if self.current_index >= len(self.frame_names):
                if self.run_once:
                    self.current_index = len(self.frame_names) - 1  # Stay on the last frame
                    self.completed = True
                else:
                    self.current_index = 0  # Loop back to the first frame

    def reset(self) -> None:
        """
        Reset the animation to its initial state and reload frames.

        :return: Index reset to the initial state (0).
        """
        self.current_index = 0
        self.elapsed_time = 0.0
        self.completed = False
        return self.current_index

    def get_current_frame(self) -> str:
        """
        Get the current frame of the animation.

        :return: Current pygame.Surface object.
        """
        return self.frame_names[self.current_index]
