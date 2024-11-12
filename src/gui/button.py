from pygame.math import Vector2 as V2
from pygame.surface import Surface
from pygame import Color
import pygame

from .label import Label

BUTTONS_PATH: str = './game_images/gui/buttons/'

class Button(Label):
    def __init__(self, 
                 text: str, 
                 x: int, y: int, 
                 width=500, height=100,
                 font_size=50, 
                 text_color=Color(255, 255, 255), 
                 bg_color=Color(0, 0, 0, 100),
                 hover_bg_color=Color(0, 0, 0, 200),
                 default_bg_image: Surface = None,
                 hover_bg_image_path: str = '',
                 default_bg_image_path: str = '',
                 on_click: callable = lambda: None,
                 click_args: list = []):
        """
        Initializes the Button with text, dimensions, font, colors, and optional images.
        """
        
        # Load background images if specified
        if default_bg_image_path:
            # Load images for default and hover states
            self.default_bg_image = pygame.image.load(BUTTONS_PATH + default_bg_image_path).convert_alpha()
            self.hover_bg_image = pygame.image.load(BUTTONS_PATH + hover_bg_image_path).convert_alpha()
            
            # Get button dimensions from the image if specified
            image_rect = self.default_bg_image.get_rect()
            button_width, button_height = image_rect.w, image_rect.h
        else:
            # Use specified dimensions if no image is provided
            button_width, button_height = width, height

        # Initialize the Label with either an image or color as background
        super().__init__(
            text=text, 
            x=x, y=y,
            width=button_width, height=button_height,
            font_size=font_size,
            text_color=text_color,
            bg_color=bg_color,
            bg_image=self.default_bg_image if default_bg_image_path else default_bg_image
        )

        # Set background colors for default and hover states
        self.default_bg_color = bg_color
        self.hover_bg_color = hover_bg_color

        # Selection and click behavior
        self.is_hovered = False
        self.on_click = lambda: on_click(*click_args)  # Set action with optional arguments



    def press(self):
        """Execute the assigned action for the button."""
        self.on_click()

    def select(self):
        """Apply hover state to the button."""
        if not self.is_hovered:
            self.is_hovered = True
            
            # Update background based on whether an image or color is used
            if self.bg_image:
                self.bg_image = self.hover_bg_image
            else:
                self.bg_color = self.hover_bg_color
            
            # Re-render to apply changes
            self.render()

    def unselect(self):
        """Revert to the default button state."""
        if self.is_hovered:
            self.is_hovered = False
            
            # Reset background to default image or color
            if self.bg_image:
                self.bg_image = self.default_bg_image
            else:
                self.bg_color = self.default_bg_color
            
            # Re-render to apply changes
            self.render()