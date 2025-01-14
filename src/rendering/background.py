import pygame
import commons
from images.image_loader import IMAGE_LOADER

class BackLayer:
    def __init__(self, image_name, factor=1, y_offset: int=0, color_key=(0, 0, 0)):
        self.image = pygame.Surface((commons.WIDTH, commons.HEIGHT))
        self.image.fill(color_key)
        self.image.set_colorkey(color_key)

        self.bimage = IMAGE_LOADER.get_image(image_name)
        self.image.blit(self.bimage, (0, commons.HEIGHT - self.bimage.get_height()- y_offset))

        self.factor = factor
        self.width = self.bimage.get_width()
        self.pos_x = 0

        self.elapsed_time = 0      # Timer to track elapsed time
        self.tinted_image = None  # Stores the last painted image

    def update(self, x: int, delta_time: float):
        self.pos_x = int(x * self.factor)

        # Update the elapsed time
        self.elapsed_time += delta_time

    def repaint(self, blended_color):
        """Repaints the image with the given color and stores it as the last painted frame."""
        self.tinted_image = self.image.copy()
        # Apply the blended color
        self.tinted_image.fill(blended_color, special_flags=pygame.BLEND_MULT)

    def draw(self, screen, blended_color):
        # Repaint every 2 seconds
        if self.elapsed_time >= 0.5 or self.tinted_image is None:
            self.repaint(blended_color)
            self.elapsed_time = 0  # Reset the timer

        # Blit the last painted image
        pos_x = self.pos_x % commons.WIDTH

        screen.blit(self.tinted_image, (pos_x - self.width, 0))
        screen.blit(self.tinted_image, (pos_x, 0))
