from .game_actor import GameActor
from rendering.animation import Animation
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

        # Load animations using the ImageLoader
        w_right = Animation([f"PLAYER_WALKING_{i}" for i in range(8)], 0.1, False)  # Walking right
        w_left = Animation([f"PLAYER_WALKING_{i}.FLIPED_X" for i in range(8)], 0.1, False)  # Walking left

        idle_right = Animation([f"PLAYER_IDLE_{i}" for i in range(15)], 0.1, True)  # Idle right
        idle_left = Animation([f"PLAYER_IDLE_{i}.FLIPED_X" for i in range(15)], 0.1, True)  # Idle left

        run_right = Animation([f"PLAYER_RUNNING_{i}" for i in range(6)], 0.08, False)  # Running right
        run_left = Animation([f"PLAYER_RUNNING_{i}.FLIPED_X" for i in range(6)], 0.08, False)  # Running left

        jump_right = Animation([f"PLAYER_JUMPING_{i}" for i in range(5)], 0.12, True)  # Jumping right
        jump_left = Animation([f"PLAYER_JUMPING_{i}.FLIPED_X" for i in range(5)], 0.12, True)  # Jumping left

        attack_right = Animation([f"PLAYER_ATTACK_{i}" for i in range(10)], 0.07, True)  # Attacking right
        attack_left = Animation([f"PLAYER_ATTACK_{i}.FLIPED_X" for i in range(10)], 0.07, True)  # Attacking left


        # Call the parent constructor with these defaults
        super().__init__(position, size, life, max_vel, 
                         w_right, w_left, 
                         w_right, w_left, 
                         idle_right, idle_left, 
                         w_right, w_left,
                         w_right, w_left)

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
