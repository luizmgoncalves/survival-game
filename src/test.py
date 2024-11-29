import pygame
from rendering.render_manager import RenderManager
from database.world import World
from physics.moving_element import CollidableMovingElement
from physics.physics_manager import PhysicsManager
from database.world_elements.block_metadata_loader import BLOCK_METADATA
from images.image_loader import IMAGE_LOADER
import commons
import math
import numpy as np
import os

def main():
    pygame.init()
    BLOCK_METADATA.init()
    #print(BLOCK_METADATA.metadata)
    
    # Screen dimensions
    commons.WIDTH, commons.HEIGHT = 1600, 900
    screen = pygame.display.set_mode((commons.WIDTH, commons.HEIGHT))
    pygame.display.set_caption("Render Manager Demo")
    IMAGE_LOADER.init()

    print(BLOCK_METADATA.get_name_by_id(0))

    # Constants
    #commons.CHUNK_SIZE_PIXELS = 256
    #commons.BLOCK_SIZE = 16
    commons.STARTING_POSITION = [-30, -30]
    commons.COLOR_KEY = (0, 0, 0)

    # Initialize RenderManager and mock world
    
    world = World('name')

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    pedra = CollidableMovingElement(commons.STARTING_POSITION, (commons.BLOCK_SIZE, commons.BLOCK_SIZE))
    commons.STARTING_POSITION = pygame.Vector2(pedra.rect.center ) - pygame.Vector2(commons.WIDTH, commons.HEIGHT)/2
    render_manager = RenderManager(commons.STARTING_POSITION, commons.COLOR_KEY)

    physics_manager = PhysicsManager(None, [], [], [], [pedra])

    print(world.load_chunk(0, 0).blocks_grid[0])
    print(np.vectorize(lambda x: bin(x)[2:].zfill(4))(world.load_chunk(0, 0).edges_matrix[0]))

    delta_time = 1/60

    while running:
        delta_time = clock.tick(50) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update logic (e.g., moving elements, position changes)
        render_manager.update_position((commons.STARTING_POSITION[0], commons.STARTING_POSITION[1]))

        # Update chunks
        render_manager.update_chunks(world)

        
        #for line in render_manager.chunk_matrix:
        #    #for chunk in line:
        #    #   (chunk.collidable_grid, end='-')
        #    #print()
        #print("\n-------\n")
        #os.system("clear")
        

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            pedra.velocity.x = -300
        if keys[pygame.K_RIGHT]: 
            pedra.velocity.x = 300
        if keys[pygame.K_UP]:
            
            pedra.velocity.y = -500
        if keys[pygame.K_DOWN]:
            pedra.velocity.y = 500
        if keys[pygame.K_k]:
            pedra.velocity.y = -70
        if keys[pygame.K_ESCAPE]:
            break
        
        pedra.velocity.x *= 0.8



        x_dist = math.ceil(pedra.velocity.x * delta_time)
        y_dist = math.ceil(pedra.velocity.y * delta_time)
        blocks = world.get_collision_blocks_around(pedra.rect.center, (x_dist, y_dist))
        

        physics_manager.update(delta_time, world)

        # Render everything
        screen.fill((200, 200, 200))  # Background color
        commons.STARTING_POSITION = pygame.Vector2(pedra.rect.center ) - pygame.Vector2(commons.WIDTH, commons.HEIGHT)/2
        render_manager.render_all(screen)
        #pygame.draw.rect(screen, (0, 255, 0), mouse_rect)

        #for block in blocks:
        #    block.center -= pygame.Vector2(commons.STARTING_POSITION) 
        #    pygame.draw.rect(screen, (0, 100, 100), block)
        
        pygame.draw.rect(screen, (10, 10, 10), ((pedra.rect.topleft[0] - commons.STARTING_POSITION[0], pedra.rect.topleft[1] - commons.STARTING_POSITION[1]), pedra.rect.size))

        pygame.display.update()

        # Limit frame rate

    pygame.quit()

if __name__ == "__main__":
    main()