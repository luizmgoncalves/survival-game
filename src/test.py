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
    commons.WIDTH, commons.HEIGHT = 1600, 900
    screen = pygame.display.set_mode((commons.WIDTH, commons.HEIGHT))
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


        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        mouse_rect = pygame.Rect((0, 0), (100, 100))
        mouse_rect.center = mouse_pos
        
        print(int((render_manager.current_position[0] + commons.WIDTH/2) / commons.CHUNK_SIZE_PIXELS), int((render_manager.current_position[1] + commons.HEIGHT/2) / commons.CHUNK_SIZE_PIXELS))
        print(int((mouse_pos.x + commons.WIDTH/2) / commons.CHUNK_SIZE_PIXELS), int((mouse_pos.y + commons.HEIGHT/2) / commons.CHUNK_SIZE_PIXELS))


        # Render everything
        screen.fill((100, 100, 100))  # Background color
        render_manager.render_all(screen)
        pygame.draw.rect(screen, (0, 255, 0), mouse_rect)
        pygame.display.update()

        # Limit frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
