import random
import pygame
import json
from .game_actor import GameActor
from images.image_loader import IMAGE_LOADER


class Enemy(GameActor):
    def __init__(self, config_file):
        """
        Initialize an enemy with attributes and animations loaded from a configuration JSON.

        :param config_file: Path to the JSON file containing enemy configuration.
        """
        # Load configuration
        with open(config_file, 'r') as file:
            config = json.load(file)
        
        position = tuple(config["position"])
        size = tuple(config["size"])
        life = config["life"]
        max_vel = config["max_velocity"]
        
        # Load animations from the sprite sheet
        sprite_sheet_path = config["sprite_sheet"]
        animations = config["animations"]

        walking_sprites_right = self._load_sprites(sprite_sheet_path, animations["walking"]["right"])
        running_sprites_right = self._load_sprites(sprite_sheet_path, animations["running"]["right"])
        idle_sprites_right = self._load_sprites(sprite_sheet_path, animations["idle"]["right"])
        jumping_sprites_right = self._load_sprites(sprite_sheet_path, animations["jumping"]["right"])
        died_sprites = self._load_sprites(sprite_sheet_path, animations["died"]["all"])

        # Call parent constructor
        super().__init__(position, size, life, max_vel, walking_sprites_right,
                         running_sprites_right, idle_sprites_right, jumping_sprites_right)

        self.died_sprites = iter(died_sprites)
        self.is_dying = False  # Whether the enemy is in the death animation
        self.dying_timer = 0  # Timer for death animation

    def _load_sprites(self, sprite_sheet_path, frames):
        """
        Load a list of sprites from a sprite sheet using frame coordinates.

        :param sprite_sheet_path: Path to the sprite sheet image.
        :param frames: List of dictionaries with 'x', 'y', 'width', and 'height' for each frame.
        :return: List of pygame.Surface objects.
        """
        sprite_sheet = IMAGE_LOADER.get_image(sprite_sheet_path)
        sprites = []
        for frame in frames:
            x, y, width, height = frame["x"], frame["y"], frame["width"], frame["height"]
            rect = pygame.Rect(x, y, width, height)
            sprite = sprite_sheet.subsurface(rect)
            sprites.append(sprite)
        return sprites

    def take_damage(self, amount):
        """
        Apply damage to the enemy.

        :param amount: The amount of damage to apply.
        """
        if not self.is_dying:
            self.life -= amount
            if self.life <= 0:
                self.start_dying()

    def start_dying(self):
        """
        Start the death animation for the enemy.
        """
        self.is_dying = True
        self.dying_timer = 0
        self.image = next(self.died_sprites, None)  # Start death animation

    def update_behavior(self, delta_time, player_position):
        """
        Update the enemy's behavior or death animation.

        :param delta_time: Time step for the update.
        :param player_position: Position of the player.
        """
        if self.is_dying:
            self.dying_timer += delta_time
            if self.dying_timer >= 0.1:  # Change frame every 0.1 seconds
                self.image = next(self.died_sprites, None)
                self.dying_timer = 0
            if self.image is None:  # Death animation is complete
                self.kill()
        else:
            # Example behavior: chase player
            if self.rect.centerx < player_position[0]:
                self.walk_right()
            elif self.rect.centerx > player_position[0]:
                self.walk_left()
            else:
                self.velocity.x = 0  # Stop when aligned with player

        # Call parent update for movement and animations
        super().update(delta_time)

    def is_dead(self):
        """
        Check if the enemy has completed its death animation.

        :return: True if the enemy is dead and can be removed, False otherwise.
        """
        return self.image is None and self.is_dying


class EnemyManager:
    """
    Manages the creation and spawning of enemies in the game.
    """
    def __init__(self, config_files, spawn_interval):
        """
        Initialize the EnemyManager.

        :param config_files: List of paths to enemy configuration files.
        :param spawn_interval: Time (in milliseconds) between enemy spawns.
        """
        self.config_files = config_files  # List of JSON files for enemies
        self.spawn_interval = spawn_interval
        self.last_spawn_time = 0
        self.enemies = []  # List of active enemies

    def update(self, current_time, delta_time, player_position):
        """
        Update the enemy manager and spawn new enemies if needed.

        :param current_time: Current game time in milliseconds.
        :param delta_time: Time elapsed since the last frame.
        :param player_position: Position of the player (for enemy behavior).
        """
        # Check if it's time to spawn a new enemy
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.spawn_enemy()
            self.last_spawn_time = current_time

        # Update all active enemies and remove the dead ones
        self.enemies = [enemy for enemy in self.enemies if not enemy.is_dead()]
        for enemy in self.enemies:
            enemy.update_behavior(delta_time, player_position)

    def spawn_enemy(self):
        """
        Spawn a new enemy randomly chosen from the available configuration files.
        """
        config_file = random.choice(self.config_files)
        new_enemy = Enemy(config_file)
        self.enemies.append(new_enemy)

    def draw(self, screen):
        """
        Draw all active enemies on the screen.

        :param screen: The game screen (pygame.Surface).
        """
        for enemy in self.enemies:
            screen.blit(enemy.image, enemy.rect.topleft)
