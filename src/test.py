import pygame
from rendering.render_manager import RenderManager
from database.world import World
from physics.moving_element import MovingElement
from database.world_elements.block_metadata_loader import BLOCK_METADATA
import commons
import os

def main():
    pygame.init()
    BLOCK_METADATA.init()
    #print(BLOCK_METADATA.metadata)
    
    # Screen dimensions
    SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Render Manager Demo")

    # Constants
    #commons.CHUNK_SIZE_PIXELS = 256
    #commons.BLOCK_SIZE = 16
    commons.STARTING_POSITION = [-30, -30]
    commons.COLOR_KEY = (0, 0, 0)

    # Initialize RenderManager and mock world
    render_manager = RenderManager(commons.STARTING_POSITION, commons.COLOR_KEY)
    world = World('name')

    # Main game loop
    clock = pygame.time.Clock()
    running = True

   #print(world.load_chunk(0, 0).blocks_grid)

    while running:
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
            commons.STARTING_POSITION[0] -= 5
        if keys[pygame.K_RIGHT]: 
            commons.STARTING_POSITION[0] += 5
        if keys[pygame.K_UP]:
            commons.STARTING_POSITION[1] -= 5
        if keys[pygame.K_DOWN]:
            commons.STARTING_POSITION[1] += 5

        

        # Render everything
        screen.fill((100, 100, 100))  # Background color
        render_manager.render_all(screen)
        pygame.display.update()

        # Limit frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
