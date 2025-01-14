import pygame
from .page import Page
from database.world import World
from rendering.render_manager import RenderManager
from physics.physics_manager import PhysicsManager
from physics.player import Player
import commons
from images.image_loader import IMAGE_LOADER
from rendering.render_manager import RenderManager
from database.world import World
from physics.player import Player
from physics.physics_manager import PhysicsManager
from physics.bullet import Arrow, Axe
from database.world_elements.block_metadata_loader import BLOCK_METADATA
from images.image_loader import IMAGE_LOADER
from database.world_loader import WORLD_LOADER
from database.world_elements.static_elements_manager import S_ELEMENT_METADATA_LOADER
from database.world_elements.item_metadata import ITEM_METADATA
from rendering.color_filter import ColorFilter
from rendering.background import BackLayer
import commons
from pygame.math import Vector2 as v2

class GamePage(Page):
    def __init__(self):
        """
        Initialize the GamePage with essential managers for world, rendering, and physics.
        """
        super().__init__()
        self.running = False
        self.clock = pygame.time.Clock()
        self.world = None
        self.player = None
        self.render_manager = None
        self.physics_manager = None
        self.color_filter = None
        self.back = None
        self.back1 = None

    def reset(self, world_name, *args, **kwargs):
        """
        Reset the game state with a new world or initial setup.
        """
        if not world_name:
            return

        pygame.init()
        BLOCK_METADATA.init()
        S_ELEMENT_METADATA_LOADER.init()
        ITEM_METADATA.init()
        IMAGE_LOADER.init()

        self.running = True
        self.world_name = world_name

        # Initialize world, player, and managers
        self.world = World(self.world_name)
        world_data = WORLD_LOADER.get_world(world_name)
        player_data = self.world.db_interface.load_player_location(self.world.world_id)

        if player_data:
            self.player = Player(position=player_data, kills=world_data['kills'], deaths=world_data['deaths'])
        else:
            self.player = Player()

        commons.CURRENT_POSITION = pygame.Vector2(self.player.rect.center) - pygame.Vector2(commons.WIDTH, commons.HEIGHT * 0.6) / 2
        self.render_manager = RenderManager(commons.CURRENT_POSITION)
        self.physics_manager = PhysicsManager(self.player, [], [], [], [])

        self.world.db_interface.load_inventory(self.world.world_id, self.player.inventory)
        self.render_manager.update_chunks(self.world)

        self.color_filter = ColorFilter(commons.DAY_DURATION)
        self.back = BackLayer("SKY", 0.04)
        self.back1 = BackLayer("MOUNTAIN", 0.09, -0.1)

    def resize(self, display_size):
        """
        Adjust the game page elements and background based on the new screen size.
        """
        if not self.back:
            return
        
        self.back.resize()
        self.back1.resize()

    def handle_events(self, event):
        """
        Handle user inputs specific to game actions and interactions.
        """
        if event.type == pygame.QUIT:
            self.running = False
            self.save()
            self.go_to_worlds_page()
        elif event.type == pygame.WINDOWRESIZED:
            self.resize(pygame.display.get_window_size())
        elif event.type == commons.RENDER_MANAGER_INIT:
            self.render_manager.initializing = True
        elif event.type == commons.ITEM_DROP_EVENT:
            self.physics_manager.spawn_item(event.item, event.pos)
        elif event.type == commons.THROWING:
            if event.dict.get("enemy", False):
                self.physics_manager.enemy_throw(event.throwable, event.pos)
        elif event.type == commons.S_ELEMENT_BROKEN:
            self.render_manager._update_static_elements()
        elif event.type == commons.ITEM_COLLECT_EVENT:
            print(f"Item {ITEM_METADATA.get_name_by_id(event.item)} collected")
        elif event.type == pygame.MOUSEWHEEL:
            self.player.inventory.scroll(event.y)
        elif event.type == pygame.KEYDOWN:
            if event.unicode.isnumeric():
                self.player.inventory.selected = int(event.unicode) - 1
            if event.key == pygame.K_ESCAPE:
                self.running = False
                self.save()
                self.go_to_worlds_page()
    
    def go_to_worlds_page(self):
        """
        Action to trigger a custom event that changes the page to the WorldsPage.
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'worlds_page'}))

    def update(self, delta_time):
        """
        Update the game state, including world state, physics, and player input.
        """
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        if mouse_pressed[2]:
            quant, item = self.player.inventory.get_slot(self.player.inventory.selected)
            if item != -1:
                block_name = ITEM_METADATA.get_property_by_id(item, "block_name")
                if block_name:
                    block = BLOCK_METADATA.get_id_by_name(block_name)
                    if block:
                        self.player.inventory.pick_item(self.world.put(
                            v2(pygame.mouse.get_pos()) + commons.CURRENT_POSITION,
                            v2(10, 10), int(block), quant, self.player,
                            keys[pygame.K_LSHIFT]
                        ))

        if mouse_pressed[0]:
            mouse_pos = pygame.mouse.get_pos()
            mouse_rect = pygame.Rect(0, 0, 10, 10)
            mouse_rect.center = v2(mouse_pos) + commons.CURRENT_POSITION
            self.world.mine(mouse_rect.topleft, mouse_rect.size, 50, delta_time)

        self.world.update_world_state(delta_time)
        self.render_manager.update_chunks(self.world)
        self.player.handle_input(keys)
        self.physics_manager.update(delta_time, self.world)

        commons.CURRENT_POSITION = pygame.Vector2(self.player.rect.center) - pygame.Vector2(commons.WIDTH, commons.HEIGHT) / 2
        self.render_manager.update_position((commons.CURRENT_POSITION[0], commons.CURRENT_POSITION[1]))

    def draw(self, screen):
        """
        Draw all game elements on the screen.
        """
        delta_time = self.clock.tick(50) / 1000
        color = self.color_filter.get_color(delta_time)

        self.back.update(-commons.CURRENT_POSITION.x, delta_time)
        self.back1.update(-commons.CURRENT_POSITION.x, delta_time)

        self.back.draw(screen, color)
        self.back1.draw(screen, color)

        self.render_manager.render_all(screen, self.physics_manager.get_renderable_elements(), self.player)
        pygame.display.update()
    
    def save(self):
        """
        Main game loop.
        """
        self.world.db_interface.save_player_location(self.world.world_id, self.player.rect.x, self.player.rect.y, self.player.deaths, self.player.kills)
        self.world.db_interface.save_inventory(self.world.world_id, self.player.inventory)
        self.world.save_all_data()
        self.world.db_interface.save_score(self.world_name, self.player.kills, self.player.deaths)
