# src/pages/page.py
from abc import ABC, abstractmethod
import pygame

class Page(ABC):
    def __init__(self):
        pass

    def opened(self):
        """Update the page when it is open."""
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the state of the page.
        """
        pass

    @abstractmethod
    def handle_events(self, event):
        """Handle events specific to the page (e.g., button clicks)."""
        pass

    @abstractmethod
    def update(self):
        """Update the page's state (e.g., animations, user inputs)."""
        pass

    @abstractmethod
    def draw(self, screen):
        """Draw the page elements on the screen."""
        pass
