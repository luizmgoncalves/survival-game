import pygame
from .page import Page
from database.world import World
from rendering.render_manager import RenderManager
from physics.physics_manager import PhysicsManager
from physics.player import Player
import commons
from images.image_loader import IMAGE_LOADER

class GamePage(Page):
    def __init__(self):
        """
        Initialize the GamePage with essential managers for world, rendering, and physics.
        """
        super().__init__()
    
    def reset(self):
        player = Player()

        # Initialize managers for world, rendering, and physics
        self.world_manager =   World(commons.WORLD_SELECTED)
        self.render_manager =  RenderManager(commons.PLAYER_START_POSITION)
        self.physics_manager = PhysicsManager(player, [], [], [], [])

        # Set up background image or color if needed
        self._bg_image = IMAGE_LOADER.get_image("WALLPAPER")
        self.bg_image = self._bg_image

        # For holding any entities or game objects
        self.entities = []

        # Initial setup of game state, load the world, etc.
        self.world_manager.load_all_chunks()
        self.resize(pygame.display.get_window_size())

    def resize(self, display_size):
        """
        Adjust the game page elements and background based on the new screen size.
        """
        scale_x, scale_y = display_size[0] / commons.WIDTH, display_size[1] / commons.HEIGHT
        self.bg_image = pygame.transform.scale(self._bg_image, display_size).convert()

        # Adjust manager scales if they depend on display size
        self.render_manager.resize(scale_x, scale_y)

    def handle_events(self, event):
        """
        Handle user inputs specific to game actions and interactions.
        """
        if event.type == pygame.QUIT:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif event.type == pygame.KEYDOWN:
            pass 
            #self.world_manager.handle_keydown(event.key)
            #self.physics_manager.handle_keydown(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pass 
            #self.world_manager.handle_mouse_click(event.pos)

    def update(self, delta_time):
        """
        Update the game state, including world state, physics, and entity positions.
        """
        # Update world state and entities
        self.world_manager.update(delta_time)
        self.physics_manager.update(self.entities, delta_time)

        # Update entity animations, positions, or effects
        for entity in self.entities:
            entity.update(delta_time)

    def draw(self, screen):
        """
        Draw all game elements on the screen.
        """
        screen.blit(self.bg_image, (0, 0))  # Draw the scaled background image
        
        # Use the render manager to draw entities and environment
        self.render_manager.draw_background(screen, self.world_manager)
        self.render_manager.draw_entities(screen, self.entities)
        
        pygame.display.flip()
