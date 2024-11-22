from pygame.sprite import DirtySprite, LayeredUpdates
from pygame.font import SysFont
from pygame.rect import Rect
from pygame.color import Color
from pygame.surface import Surface

import pygame

class Label(DirtySprite):
    def __init__(self, 
                 text: str, 
                 x: int, y: int, 
                 width=700, height=90, 
                 font_name='game', 
                 font_size=90, 
                 text_color=Color(255, 255, 255), 
                 bg_color=Color(0, 0, 0, 0),
                 bg_image: Surface = None,
                 scale_x=1.0, scale_y=1.0):
        """
        Initialize the Label with text, position, dimensions, font, and optional background.
        """
        
        super().__init__()
        
        # Text and style settings
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.font = SysFont(font_name, font_size)

        # Static sprite settings
        self.base_rect = Rect(0, 0, width, height)
        self.base_rect.center = (x, y)
        
        self.base_image = Surface((width, height), pygame.SRCALPHA).convert_alpha()

        # Background image handling
        self.bg_image = None
        if bg_image:
            self.bg_image = pygame.transform.smoothscale(bg_image, (width, height)).convert_alpha()
        
        # Scaling factors for resizing
        self.scale_factor = (scale_x, scale_y)

        # Initialize display image and rectangle
        self.image = self.base_image.copy()
        self.rect = self.base_rect.copy()
    
    def render(self):
        """Render the label's background and text, applying scaling if needed."""
        
        # Clear base image and set background
        if self.bg_image:
            self.base_image.fill((0, 0, 0, 0))  # Clear for image background
            self.base_image.blit(self.bg_image, (0, 0))
        else:
            self.base_image.fill(self.bg_color)
        
        # Render and center the text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=[dim / 2 for dim in self.base_rect.size])
        self.base_image.blit(text_surface, text_rect)
        
        # Scale the image based on the scaling factor
        self.image = pygame.transform.smoothscale_by(self.base_image, self.scale_factor)

    def resize(self, scale_x, scale_y):
        """Update the label's scaling factors and adjust the rectangle size and position."""
        
        self.scale_factor = (scale_x, scale_y)
        
        # Scale the base rectangle and update position
        self.rect = self.base_rect.scale_by(scale_x, scale_y)
        self.rect.topleft = (self.base_rect.x * scale_x, self.base_rect.y * scale_y)
    
    def set_pos(self, x, y):
        self.base_rect.centerx = x
        self.base_rect.centery = y
        self.rect.topleft = (self.base_rect.x * self.scale_factor[0], self.base_rect.y * self.scale_factor[1])
    
    def move(self, x_offset, y_offset):
        self.base_rect.x += x_offset
        self.base_rect.y += y_offset
        self.rect.topleft = (self.base_rect.x * self.scale_factor[0], self.base_rect.y * self.scale_factor[1])
