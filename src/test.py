import pygame
from rendering.render_manager import RenderManager
from database.world import World
from physics.moving_element import CollidableMovingElement
from physics.player import Player
from physics.physics_manager import PhysicsManager
from physics.bullet import Arrow, Axe
from database.world_elements.block_metadata_loader import BLOCK_METADATA
from images.image_loader import IMAGE_LOADER
from database.world_loader import WORLD_LOADER
from database.world_elements.static_elements_manager import S_ELEMENT_METADATA_LOADER
from database.world_elements.item_metadata import ITEM_METADATA
from physics.enemy import ENEMY_MANAGER
from utils.debug import Debug
from rendering.color_filter import ColorFilter
from rendering.background import BackLayer
import commons
import math
from pygame.math import Vector2 as v2
import numpy as np
import random
import os


debug = Debug()
 
def game(screen, world_name):
    pygame.init()
    BLOCK_METADATA.init()
    S_ELEMENT_METADATA_LOADER.init()
    ITEM_METADATA.init()
    
    IMAGE_LOADER.init()

    #print(BLOCK_METADATA.get_name_by_id(0))

    # Initialize RenderManager and mock world

    color_filter = ColorFilter(commons.DAY_DURATION)
    back = BackLayer("SKY", 0.04)
    back1 = BackLayer("MOUNTAIN", 0.09, -0.1)
    
    world = World(world_name)

    world_data = WORLD_LOADER.get_world(world_name)
    start_pos = world.db_interface.load_player_location(world.world_id)
    if start_pos:
        player = Player(position=start_pos, kills=world_data['kills'], deaths=world_data['deaths'])
    else:
        player = Player()

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    

    WORLD_LOADER.load_inventory(world.world_id, player.inventory)

    commons.CURRENT_POSITION = pygame.Vector2(player.rect.center ) - pygame.Vector2(commons.WIDTH, commons.HEIGHT*0.6)/2
    render_manager = RenderManager(commons.CURRENT_POSITION)

    physics_manager = PhysicsManager(player, [], [], [], [])

    render_manager.update_chunks(world)


    while running:
        delta_time = clock.tick(50) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.WINDOWRESIZED:
                commons.WIDTH, commons.HEIGHT = pygame.display.get_window_size()
                back.resize()
                back1.resize()
            
            if event.type == commons.RENDER_MANAGER_INIT:
                render_manager.initializing = True
            
            if event.type == commons.ITEM_DROP_EVENT:
                physics_manager.spawn_item(event.item, event.pos)

            if event.type == commons.THROWING:
                if event.dict.get("enemy", False):
                    physics_manager.enemy_throw(event.throwable, event.pos)
            
            if event.type == commons.S_ELEMENT_BROKEN:
                render_manager._update_static_elements()
            
            if event.type == commons.ITEM_COLLECT_EVENT:
                print(f"Item {ITEM_METADATA.get_name_by_id(event.item)} colected")
            
            if event.type == pygame.MOUSEWHEEL:
                player.inventory.scroll(event.y)
            
                    
            
            if event.type == pygame.KEYDOWN:
                if event.unicode.isnumeric():
                    player.inventory.selected = int(event.unicode)-1
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        keys = pygame.key.get_pressed()

        mouse_pressed = pygame.mouse.get_pressed()



        if mouse_pressed[2]:
            quant, item = player.inventory.get_slot(player.inventory.selected)
            if item != -1:
                block_name = ITEM_METADATA.get_property_by_id(item, "block_name")
                if block_name:
                    block = BLOCK_METADATA.get_id_by_name(block_name)
                    if block:
                        player.inventory.pick_item(world.put(v2(pygame.mouse.get_pos()) + commons.CURRENT_POSITION, v2(10, 10), int(block), quant, player, keys[pygame.K_LSHIFT]))
        
        if mouse_pressed[0]:
            debug.start_timer("mining")
            mouse_pos = pygame.mouse.get_pos()
            mouse_rect = pygame.Rect(0, 0, 10, 10)
            mouse_rect.center = v2(mouse_pos) + commons.CURRENT_POSITION 
            world.mine(mouse_rect.topleft, mouse_rect.size, 50, delta_time)
            
        world.update_world_state(delta_time)
        render_manager.update_chunks(world)

        player.handle_input(keys)

        physics_manager.update(delta_time, world)

        commons.CURRENT_POSITION = pygame.Vector2(player.rect.center ) - pygame.Vector2(commons.WIDTH, commons.HEIGHT)/2

        # Update logic (e.g., moving elements, position changes)
        render_manager.update_position((commons.CURRENT_POSITION[0], commons.CURRENT_POSITION[1]))


        # Render everything
        color = color_filter.get_color(delta_time)
        back.update(-commons.CURRENT_POSITION.x, delta_time)
        back1.update(-commons.CURRENT_POSITION.x, delta_time)

        back.draw(screen, color)
        back1.draw(screen, color)

        render_manager.render_all(screen, physics_manager.get_renderable_elements(), player)

        pygame.display.update()

        # Limit frame rate

    world.db_interface.save_player_location(world.world_id, player.rect.x, player.rect.y)
    world.db_interface.save_inventory(world.world_id, player.inventory)
    world.save_all_data()
    
    debug.show_statistics()

if __name__ == "__main__":
    screen = pygame.display.set_mode((commons.WIDTH, commons.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Render Manager Demo")
    
    game(screen, 'h')

    exit()
