# File path: render_manager.py

import pygame
import commons
from database.world_elements.block_metadata_loader import BLOCK_METADATA
from database.world_elements.chunk import Chunk
import numpy as np
from pygame.math import Vector2 as V2


class RenderManager:
    """
    A manager class responsible for handling the rendering of a 3x3 chunk matrix and moving elements.
    """

    def __init__(self, current_position, color_key):
        """
        Initialize the RenderManager with a starting position and color key for transparency.

        :param current_position: Tuple[int, int], starting position (x, y) in world coordinates.
        :param color_key: Tuple[int, int, int], RGB value for transparency in surfaces.
        """
        self.current_position = current_position
        self.current_chunk_position = self.get_chunk_position()
        self.initializing = True
        self.color_key = color_key
        self.chunk_matrix = np.matrix([[None for _ in range(3)] for _ in range(3)])
        self.surface_matrix = np.matrix([[self.create_surface() for _ in range(3)] for _ in range(3)])
        self.moving_elements = []
    
    def get_chunk_position(self):
        return int((self.current_position[0] + commons.WIDTH /2) // commons.CHUNK_SIZE_PIXELS), int((self.current_position[1]+ commons.HEIGHT /2) // commons.CHUNK_SIZE_PIXELS)

    def create_surface(self):
        """
        Creates a new surface for rendering a single chunk with the specified color key.

        :return: pygame.Surface, a new surface instance.
        """
        surface = pygame.Surface((commons.CHUNK_SIZE_PIXELS, commons.CHUNK_SIZE_PIXELS)).convert()
        surface.set_colorkey(self.color_key)
        return surface

    def update_chunks(self, world):
        """
        Updates the 3x3 chunk matrix based on the current position in the world.
        This function loads new chunks if necessary.

        :param world: The game world object that provides chunk-loading functionality.
        """
        if self.current_chunk_position != (new_pos := self.get_chunk_position()):
            print("new chunk")
            dif = pygame.Vector2(new_pos) - pygame.Vector2(self.current_chunk_position)
            #print(dif)
            self.current_chunk_position = new_pos

            if dif.x:
                if dif.x > 0:
                    #print(np.vectorize(id)(self.surface_matrix))
                    buff = self.surface_matrix[:, 0].copy()
                    self.surface_matrix[:, 0] = self.surface_matrix[:, 1]
                    self.surface_matrix[:, 1] = self.surface_matrix[:, 2]
                    self.surface_matrix[:, 2] = buff
                    #print(np.vectorize(id)(self.surface_matrix))
                    self.chunk_matrix[:, 0] = self.chunk_matrix[:, 1]
                    self.chunk_matrix[:, 1] = self.chunk_matrix[:, 2]

                    
                    chunk_x = self.chunk_matrix[0, 2].pos.x + 1
                    for i in range(3):
                        chunk_y = self.chunk_matrix[0, 0].pos.y + i 
                        self.chunk_matrix[i, 2] = world.load_chunk(chunk_x, chunk_y)
                        self.chunk_matrix[i, 2].has_changes = True
                else:
                    buff = self.surface_matrix[:, 2].copy()
                    self.surface_matrix[:, 2] = self.surface_matrix[:, 1]
                    self.surface_matrix[:, 1] = self.surface_matrix[:, 0]
                    self.surface_matrix[:, 0] = buff
                    
                    self.chunk_matrix[:, 2] = self.chunk_matrix[:, 1]
                    self.chunk_matrix[:, 1] = self.chunk_matrix[:, 0]

                    chunk_x = self.chunk_matrix[0, 0].pos.x - 1
                    for i in range(3):
                        chunk_y = self.chunk_matrix[0, 0].pos.y + i 
                        self.chunk_matrix[i, 0] = world.load_chunk(chunk_x, chunk_y)
                        self.chunk_matrix[i, 0].has_changes = True
            if dif.y:
                if dif.y > 0:
                    buff = self.surface_matrix[0, :].copy()
                    self.surface_matrix[0, :] = self.surface_matrix[1, :]
                    self.surface_matrix[1, :] = self.surface_matrix[2, :]
                    self.surface_matrix[2, :] = buff
                    #print(np.vectorize(id)(self.surface_matrix))
                    self.chunk_matrix[0, :] = self.chunk_matrix[1, :]
                    self.chunk_matrix[1, :] = self.chunk_matrix[2, :]


                    chunk_y = self.chunk_matrix[2, 0].pos.y + 1

                    for j in range(3):
                        chunk_x = self.chunk_matrix[2, 0].pos.x + j 
                        self.chunk_matrix[2, j] = world.load_chunk(chunk_x, chunk_y)
                        self.chunk_matrix[2, j].has_changes = True
                else:
                    buff = self.surface_matrix[2, :].copy()
                    self.surface_matrix[2, :] = self.surface_matrix[1, :]
                    self.surface_matrix[1, :] = self.surface_matrix[0, :]
                    self.surface_matrix[0, :] = buff
                    #print(np.vectorize(id)(self.surface_matrix))
                    self.chunk_matrix[2, :] = self.chunk_matrix[1, :]
                    self.chunk_matrix[1, :] = self.chunk_matrix[0, :]


                    chunk_y = self.chunk_matrix[0, 0].pos.y - 1

                    for j in range(3):
                        chunk_x = self.chunk_matrix[0, 0].pos.x + j 
                        self.chunk_matrix[0, j] = world.load_chunk(chunk_x, chunk_y)
                        self.chunk_matrix[0, j].has_changes = True

        if self.initializing:
            self.initializing = False

            self.current_chunk_position = self.get_chunk_position()
            
            for i in range(3):
                for j in range(3):
                    chunk_x = self.current_chunk_position[0] + (j - 1)
                    chunk_y = self.current_chunk_position[1] + (i - 1)
                    self.chunk_matrix[i, j] = world.load_chunk(chunk_x, chunk_y)
                    self.chunk_matrix[i, j].has_changes = True

    def render_chunks(self, screen):
        """
        Renders the 3x3 chunk matrix onto the screen.

        :param screen: pygame.Surface, the main game display.
        """
        for i in range(3):
            for j in range(3):
                chunk_surface = self.surface_matrix[i, j]
                chunk_data = self.chunk_matrix[i, j]

                # Calculate chunk position relative to the current position
                #chunk_x = (j - 1) * commons.CHUNK_SIZE_PIXELS - (self.current_position[0])
                #chunk_y = (i - 1) * commons.CHUNK_SIZE_PIXELS - (self.current_position[1])

                chunk_x = chunk_data.pos.x * commons.CHUNK_SIZE_PIXELS - (self.current_position[0]) #+ commons.WIDTH /2
                chunk_y = chunk_data.pos.y * commons.CHUNK_SIZE_PIXELS - (self.current_position[1]) #+ commons.HEIGHT /2

                self.render_single_chunk(chunk_surface, chunk_data)
                screen.blit(chunk_surface, (chunk_x, chunk_y))

    def render_single_chunk(self, surface, chunk: Chunk):
        """
        Renders a single chunk onto a given surface.

        :param surface: pygame.Surface, the surface to draw on.
        :param chunk: Chunk, the chunk object containing blocks and elements to render.
        """
        if chunk is None or not chunk.has_changes:
            return  # Skip rendering if chunk is not loaded.

        surface.fill(self.color_key)  # Clear surface with transparent background.

        #off = 10
        #pygame.draw.rect(surface, (0, 100, 0), (off/2, off/2, commons.CHUNK_SIZE_PIXELS-off, commons.CHUNK_SIZE_PIXELS-off))

        # Render the blocks in the chunk
        for x in range(chunk.blocks_grid.shape[1]):
            for y in range(chunk.blocks_grid.shape[2]):
                for layer in range(chunk.blocks_grid.shape[0]):
                    block = chunk.blocks_grid[layer, y, x]
                    edge = chunk.edges_matrix[layer, y, x]
                    if block:  # Skip empty blocks
                        block_color = BLOCK_METADATA.get_property_by_id(block, "color")
                        ##print(f"Analisando {BLOCK_METADATA.get_name_by_id(block)}, cor: {block_color}")

                        if edge == 0b1001:
                            p = V2(x * commons.BLOCK_SIZE, y * commons.BLOCK_SIZE)
                            block_poligon = [p, p+V2(0, commons.BLOCK_SIZE), p+V2(commons.BLOCK_SIZE, commons.BLOCK_SIZE)]
                            pygame.draw.polygon(surface, block_color, block_poligon)
                        elif edge == 0b0011:
                            p = V2(x * commons.BLOCK_SIZE, y * commons.BLOCK_SIZE)
                            block_poligon = [p+V2(commons.BLOCK_SIZE, 0), p+V2(0, commons.BLOCK_SIZE), p+V2(commons.BLOCK_SIZE, commons.BLOCK_SIZE)]
                            pygame.draw.polygon(surface, block_color, block_poligon)
                        else:
                            block_rect = pygame.Rect(
                                x * commons.BLOCK_SIZE,
                                y * commons.BLOCK_SIZE,
                                commons.BLOCK_SIZE,
                                commons.BLOCK_SIZE
                            )
                            pygame.draw.rect(surface, block_color, block_rect)

        # Render static world elements
        for element in chunk.world_elements:
            screen_position = (
                element.position.x,
                element.position.y
            )
            surface.blit(element.image, screen_position)

        # Flag that the chunk has been rendered
        chunk.has_changes = False


    def render_moving_elements(self, screen):
        """
        Renders all moving elements onto the screen relative to the current position.

        :param screen: pygame.Surface, the main game display.
        """
        for element in self.moving_elements:
            # Adjust element's position based on the current position
            relative_x = element.position[0] - self.current_position[0]
            relative_y = element.position[1] - self.current_position[1]

            screen.blit(element.sprite, (relative_x, relative_y))

    def render_all(self, screen):
        """
        Renders the entire scene, including chunks and moving elements.

        :param screen: pygame.Surface, the main game display.
        """
        self.render_chunks(screen)
        self.render_moving_elements(screen)

    def add_moving_element(self, element):
        """
        Adds a new moving element to the render manager.

        :param element: MovingElement, a sprite object to be rendered.
        """
        self.moving_elements.append(element)

    def update_position(self, new_position):
        """
        Updates the current position and reloads chunks if necessary.

        :param new_position: Tuple[int, int], the new position (x, y) in world coordinates.
        """
        self.current_position = new_position
