from .game_actor import GameActor
from images.image_loader import IMAGE_LOADER
import pygame
import commons

class Player(GameActor):
    def __init__(self):
        """
        Initialize the Player with default attributes and load sprites using an ImageLoader.

        :param IMAGE_LOADER: An instance of the ImageLoader class to load images.
        """
        # Default player settings
        position = commons.PLAYER_START_POSITION  # Starting position
        size     = commons.PLAYER_SIZE            # Default size
        life     = commons.PLAYER_LIFE            # Default life points
        max_vel  = commons.PLAYER_MAX_VEL         # Default maximum velocity

        # Load sprites using the ImageLoader
        walking_sprites_right = [
            IMAGE_LOADER.get_image("player_walk_right_1"),
            IMAGE_LOADER.get_image("player_walk_right_2"),
            IMAGE_LOADER.get_image("player_walk_right_3"),
            IMAGE_LOADER.get_image("player_walk_right_4")
        ]
        running_sprites_right = [
            IMAGE_LOADER.get_image("player_run_right_1"),
            IMAGE_LOADER.get_image("player_run_right_2"),
            IMAGE_LOADER.get_image("player_run_right_3"),
            IMAGE_LOADER.get_image("player_run_right_4")
        ]
        idle_sprites_right = [
            IMAGE_LOADER.get_image("player_idle_right_1"),
            IMAGE_LOADER.get_image("player_idle_right_2"),
            IMAGE_LOADER.get_image("player_idle_right_3"),
            IMAGE_LOADER.get_image("player_idle_right_4")
        ]
        jumping_sprites_right = [
            IMAGE_LOADER.get_image("player_jump_right_1"),
            IMAGE_LOADER.get_image("player_jump_right_2"),
            IMAGE_LOADER.get_image("player_jump_right_3"),
            IMAGE_LOADER.get_image("player_jump_right_4")
        ]

        # Call the parent constructor with these defaults
        super().__init__(position, size, life, max_vel, walking_sprites_right,
                         running_sprites_right, idle_sprites_right, jumping_sprites_right)

    def handle_input(self, keys):
        """
        Handle player-specific input for movement, jumping, and attacking.
        :param keys: Dictionary of keys being pressed (from pygame.key.get_pressed()).
        """
        if keys[pygame.K_LEFT]:
            self.walk_left()
        elif keys[pygame.K_RIGHT]:
            self.walk_right()
        elif keys[pygame.K_UP] and not self.jumping:
            self.jump()
        elif keys[pygame.K_SPACE]:
            self.attack()
        else:
            self.velocity.x = 0  # Stop horizontal movement if no key is pressed
