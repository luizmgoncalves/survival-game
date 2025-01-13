import pygame
from rendering.render_manager import RenderManager
from database.world import World
from physics.moving_element import CollidableMovingElement
from physics.player import Player
from physics.physics_manager import PhysicsManager
from database.world_elements.block_metadata_loader import BLOCK_METADATA
from images.image_loader import IMAGE_LOADER
from database.world_loader import WORLD_LOADER
from database.world_elements.static_elements_manager import S_ELEMENT_METADATA_LOADER
from database.world_elements.item_metadata import ITEM_METADATA
from physics.enemy import ENEMY_MANAGER
from utils.debug import Debug
import commons
import math
from pygame.math import Vector2 as v2
import numpy as np
import random
import os


debug = Debug()

def main():
    pygame.init()
    BLOCK_METADATA.init()
    S_ELEMENT_METADATA_LOADER.init()
    ITEM_METADATA.init()
    
    
    # Screen dimensions
    commons.WIDTH, commons.HEIGHT = 1920, 1080
    screen = pygame.display.set_mode((commons.WIDTH, commons.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Render Manager Demo")
    IMAGE_LOADER.init()

    #print(BLOCK_METADATA.get_name_by_id(0))

    # Initialize RenderManager and mock world
    
    world = World('h')

    
    start_pos = world.db_interface.load_player_location(world.world_id) 
    start_pos = start_pos if start_pos is not None else commons.DEFAULT_START_PLAYER_POSITION

    commons.COLOR_KEY = (0, 0, 0)

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    player = Player(start_pos)

    WORLD_LOADER.load_inventory(world.world_id, player.inventory)

    commons.CURRENT_POSITION = pygame.Vector2(player.rect.center ) - pygame.Vector2(commons.WIDTH, commons.HEIGHT)/2
    render_manager = RenderManager(commons.CURRENT_POSITION, commons.COLOR_KEY)

    new_enemy = ENEMY_MANAGER.spawn_enemy()
    new_enemy.position.y = -1000
    new_enemy.rect.y = -1000
    
    print(new_enemy.current_animation)

    physics_manager = PhysicsManager(player, [], [new_enemy], [], [])

    render_manager.update_chunks(world)

    render_manager.render_all(screen, physics_manager.get_renderable_elements(), player)

    delta_time = 1/60

    while running:
        delta_time = clock.tick(50) / 1000

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == commons.RENDER_MANAGER_INIT:
                render_manager.initializing = True
            
            if event.type == commons.ITEM_DROP_EVENT:
                physics_manager.spawn_item(event.item, event.pos)
            
            if event.type == commons.S_ELEMENT_BROKEN:
                render_manager._update_static_elements()
            
            if event.type == commons.ITEM_COLLECT_EVENT:
                print(f"Item {ITEM_METADATA.get_name_by_id(event.item)} colected")
            
            if event.type == pygame.MOUSEWHEEL:
                player.inventory.scroll(event.y)
            
                    
            
            if event.type == pygame.KEYDOWN:
                if event.unicode.isnumeric():
                    player.inventory.selected = int(event.unicode)-1
        
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
            debug.stop_timer("mining")
        
        world.update_world_state(delta_time)
        render_manager.update_chunks(world)

        if keys[pygame.K_ESCAPE]:
            break
        if keys[pygame.K_y]:
            new_enemy.jump()
        if keys[pygame.K_g]:
            new_enemy.walk_left()
        if keys[pygame.K_j]:
            new_enemy.walk_right()
        if keys[pygame.K_v]:
            new_enemy.attack()

        new_enemy.update_ai(player)
        
        player.handle_input(keys)

        physics_manager.update(delta_time, world)

        commons.CURRENT_POSITION = pygame.Vector2(player.rect.center ) - pygame.Vector2(commons.WIDTH, commons.HEIGHT)/2

        # Update logic (e.g., moving elements, position changes)
        render_manager.update_position((commons.CURRENT_POSITION[0], commons.CURRENT_POSITION[1]))

        # Render everything
        
        screen.fill((200, 200, 200))  # Background color
        render_manager.render_all(screen, physics_manager.get_renderable_elements(), player)

        pygame.display.update()

        # Limit frame rate

    world.db_interface.save_player_location(world.world_id, player.rect.x, player.rect.y)
    world.db_interface.save_inventory(world.world_id, player.inventory)
    world.save_all_data()
    pygame.quit()
    
    #debug.show_statistics()

if __name__ == "__main__":
    main()

    exit()
