# File path: render_manager.py

import pygame
import commons
from database.world_elements.block_metadata_loader import BLOCK_METADATA
from images.image_loader import IMAGE_LOADER
from database.world_elements.static_elements_manager import S_ELEMENT_METADATA_LOADER
from database.world_elements.chunk import Chunk
from physics.moving_element import MovingElement
import numpy as np
from typing import List
from pygame.math import Vector2 as v2
from threading import Thread


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
        self.current_static_elements = []
        self.initializing = True
        self.color_key = commons.BLOCK_MASK_COLOR
        self.chunk_matrix = np.matrix([[None for _ in range(3)] for _ in range(3)])
        self.surface_matrix = np.matrix([[self.create_surface() for _ in range(3)] for _ in range(3)])
        self.moving_elements = []
    
    def get_chunk_position(self):
        return int((self.current_position[0] + commons.WIDTH /2) // commons.CHUNK_SIZE_PIXELS), int((self.current_position[1]+ commons.HEIGHT /2) // commons.CHUNK_SIZE_PIXELS)

    def _update_static_elements(self):

        self.current_static_elements.clear()

        for i in range(3):
            for j in range(3):
                stc_el  = self.chunk_matrix[i, j].world_elements
                self.current_static_elements.extend(stc_el)

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
            
            dif = pygame.Vector2(new_pos) - pygame.Vector2(self.current_chunk_position)

            self.current_chunk_position = new_pos

            if dif.x:
                if dif.x > 0:
                    buff = self.surface_matrix[:, 0].copy()
                    self.surface_matrix[:, 0] = self.surface_matrix[:, 1]
                    self.surface_matrix[:, 1] = self.surface_matrix[:, 2]
                    self.surface_matrix[:, 2] = buff
                    self.chunk_matrix[:, 0] = self.chunk_matrix[:, 1]
                    self.chunk_matrix[:, 1] = self.chunk_matrix[:, 2]

                    
                    chunk_x = self.chunk_matrix[0, 2].pos.x + 1
                    for i in range(3):
                        chunk_y = self.chunk_matrix[0, 0].pos.y + i 
                        self.chunk_matrix[i, 2] = world.load_chunk(chunk_x, chunk_y)
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
            if dif.y:
                if dif.y > 0:
                    buff = self.surface_matrix[0, :].copy()
                    self.surface_matrix[0, :] = self.surface_matrix[1, :]
                    self.surface_matrix[1, :] = self.surface_matrix[2, :]
                    self.surface_matrix[2, :] = buff
                    self.chunk_matrix[0, :] = self.chunk_matrix[1, :]
                    self.chunk_matrix[1, :] = self.chunk_matrix[2, :]


                    chunk_y = self.chunk_matrix[2, 0].pos.y + 1

                    for j in range(3):
                        chunk_x = self.chunk_matrix[2, 0].pos.x + j 
                        self.chunk_matrix[2, j] = world.load_chunk(chunk_x, chunk_y)
                else:
                    buff = self.surface_matrix[2, :].copy()
                    self.surface_matrix[2, :] = self.surface_matrix[1, :]
                    self.surface_matrix[1, :] = self.surface_matrix[0, :]
                    self.surface_matrix[0, :] = buff
                    self.chunk_matrix[2, :] = self.chunk_matrix[1, :]
                    self.chunk_matrix[1, :] = self.chunk_matrix[0, :]


                    chunk_y = self.chunk_matrix[0, 0].pos.y - 1

                    for j in range(3):
                        chunk_x = self.chunk_matrix[0, 0].pos.x + j 
                        self.chunk_matrix[0, j] = world.load_chunk(chunk_x, chunk_y)
            
            self._update_static_elements()

        if self.initializing:
            self.initializing = False

            self.current_chunk_position = self.get_chunk_position()
            
            for i in range(3):
                for j in range(3):
                    chunk_x = self.current_chunk_position[0] + (j - 1)
                    chunk_y = self.current_chunk_position[1] + (i - 1)
                    self.chunk_matrix[i, j] = world.load_chunk(chunk_x, chunk_y)
            
            self._update_static_elements()

    def render_chunks(self, screen):
        """
        Renders the 3x3 chunk matrix onto the screen.

        :param screen: pygame.Surface, the main game display.
        """
        for element in self.current_static_elements:
            image_name = S_ELEMENT_METADATA_LOADER.get_property_by_id(element.id, "image_name")
            im = IMAGE_LOADER.get_image(image_name)
            screen_position = v2(element.rect.topleft) + IMAGE_LOADER.get_image_atribute(image_name, "offset") - v2(self.current_position)
            screen.blit(im, screen_position)

        
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
            
        


    def render_single_chunk(self, surface: pygame.Surface, chunk: Chunk):
        """
        Renders a single chunk onto a given surface.

        :param surface: pygame.Surface, the surface to draw on.
        :param chunk: Chunk, the chunk object containing blocks and elements to render.
        """
        if chunk is None or not any(chunk.changes.values()) or not chunk.completed_created:
            return  # Skip rendering if chunk is not loaded or if it does not have changes.

        if chunk.changes.get("all"):
            surface.fill(self.color_key)  # Clear surface with transparent background.

            # Render the blocks in the chunk
            for x in range(commons.CHUNK_SIZE):
                for y in range(commons.CHUNK_SIZE):
                    for layer in range(1, -1, -1):
                        block = chunk.blocks_grid[layer, y, x]
                        edge = chunk.edges_matrix[layer, y, x]

                        if block:
                            block_rect = pygame.Rect(
                                        x * commons.BLOCK_SIZE,
                                        y * commons.BLOCK_SIZE,
                                        commons.BLOCK_SIZE,
                                        commons.BLOCK_SIZE)
                            
                            if layer==0:
                                image_name = f"{BLOCK_METADATA.get_property_by_id(block, "image_name")}.{edge:04b}"
                                surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)
                                
                            # Checks if the upper block has transparency or if there is no block
                            elif ((chunk.edges_matrix[0, y, x] != 0b1111 and chunk.edges_matrix[0, y, x] != edge) or chunk.blocks_grid[0, y, x] == 0): 
                                image_name = f"BACK_{BLOCK_METADATA.get_property_by_id(block, "image_name")}.{edge:04b}"
                                surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)
                            
                        if block and layer==0 and False:  # Legacy
                            block_color = BLOCK_METADATA.get_property_by_id(block, "color")

                            if edge == 0b1001:
                                p = v2(x * commons.BLOCK_SIZE, y * commons.BLOCK_SIZE)
                                block_poligon = [p, p+v2(0, commons.BLOCK_SIZE), p+v2(commons.BLOCK_SIZE, commons.BLOCK_SIZE)]
                                pygame.draw.polygon(surface, block_color, block_poligon)
                            elif edge == 0b0011:
                                p = v2(x * commons.BLOCK_SIZE, y * commons.BLOCK_SIZE)
                                block_poligon = [p+v2(commons.BLOCK_SIZE, 0), p+v2(0, commons.BLOCK_SIZE), p+v2(commons.BLOCK_SIZE, commons.BLOCK_SIZE)]
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
                break
                image_name = S_ELEMENT_METADATA_LOADER.get_property_by_id(element.id, "image_name")
                im = IMAGE_LOADER.get_image(image_name)
                screen_position = v2(element.rect.topleft) - IMAGE_LOADER.get_image_atribute(image_name, "offset")
                surface.blit(im, screen_position)
            
            chunk.clear_changes()
        
        if chunk.changes.get("line"):
            for line_index in chunk.changes['line']: #Iterates over the lines that were changed
                xi = 0
                yi = line_index * commons.BLOCK_SIZE
                line_rect = pygame.Rect(xi, yi, commons.CHUNK_SIZE_PIXELS, commons.BLOCK_SIZE) 
                # Line rectangle

                surface.fill(self.color_key, line_rect)  # Clear line surface with transparent background.

                y = line_index

                for x in range(commons.CHUNK_SIZE):
                    for layer in range(1, -1, -1):
                        block = chunk.blocks_grid[layer, y, x]
                        edge = chunk.edges_matrix[layer, y, x]

                        if block:
                            block_rect = pygame.Rect(
                                        x * commons.BLOCK_SIZE,
                                        y * commons.BLOCK_SIZE,
                                        commons.BLOCK_SIZE,
                                        commons.BLOCK_SIZE)

                            if layer==0:
                                image_name = f"{BLOCK_METADATA.get_property_by_id(block, "image_name")}.{edge:04b}"
                                surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)
                            
                            elif ((chunk.edges_matrix[0, y, x] != 0b1111 and chunk.edges_matrix[0, y, x] != edge) or chunk.blocks_grid[0, y, x] == 0): 
                                image_name = f"BACK_{BLOCK_METADATA.get_property_by_id(block, "image_name")}.{edge:04b}"
                                surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)

        if chunk.changes.get('column'):
            for column_index in chunk.changes['column']: #Iterates over the lines that were changed
                yi = 0
                xi = column_index * commons.BLOCK_SIZE
                col_rect = pygame.Rect(xi, yi, commons.BLOCK_SIZE, commons.CHUNK_SIZE_PIXELS) 
                # Column rectangle

                surface.fill(self.color_key, col_rect)  # Clear line surface with transparent background.

                x = column_index

                for y in range(commons.CHUNK_SIZE):
                    for layer in range(1, -1, -1):
                        block = chunk.blocks_grid[layer, y, x]
                        edge = chunk.edges_matrix[layer, y, x]

                        if block:
                            block_rect = pygame.Rect(
                                        x * commons.BLOCK_SIZE,
                                        y * commons.BLOCK_SIZE,
                                        commons.BLOCK_SIZE,
                                        commons.BLOCK_SIZE)

                            if layer==0:
                                image_name = f"{BLOCK_METADATA.get_property_by_id(block, "image_name")}.{edge:04b}"
                                surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)
                            
                            elif ((chunk.edges_matrix[0, y, x] != 0b1111 and chunk.edges_matrix[0, y, x] != edge) or chunk.blocks_grid[0, y, x] == 0): 
                                image_name = f"BACK_{BLOCK_METADATA.get_property_by_id(block, "image_name")}.{edge:04b}"
                                surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)

        if chunk.changes.get('block'):
            for block_info in chunk.changes['block']:  # Iterate over the blocks that were changed
                x, y = block_info  # Each block_info contains the layer, y-coordinate, and x-coordinate
                # Define the rectangle for the block
                block_rect = pygame.Rect(
                    x * commons.BLOCK_SIZE,
                    y * commons.BLOCK_SIZE,
                    commons.BLOCK_SIZE,
                    commons.BLOCK_SIZE
                )

                # Clear the block area on the surface
                surface.fill(self.color_key, block_rect)

                # Redraw the block based on its layer and edges
                block = chunk.blocks_grid[0, y, x]
                edge = chunk.edges_matrix[0, y, x]

                block_1 = chunk.blocks_grid[1, y, x]
                edge_1 = chunk.edges_matrix[1, y, x]

                if ((edge != 0b1111 and edge != edge_1) or block == 0) and block_1:
                    # Render the background block
                    image_name = f"BACK_{BLOCK_METADATA.get_property_by_id(chunk.blocks_grid[1, y, x], 'image_name')}.{chunk.edges_matrix[1, y, x]:04b}"
                    surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)

                if block:
                    # Render the foreground block
                    image_name = f"{BLOCK_METADATA.get_property_by_id(block, 'image_name')}.{edge:04b}"
                    surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)
        
        if chunk.changes.get('breaking'):
            for block_info, breaking_level in chunk.changes['breaking'].items():  # Iterate over the blocks that were changed
                x, y = block_info  # Each block_info contains the layer, y-coordinate, and x-coordinate
                
                # Define the rectangle for the block
                block_rect = pygame.Rect(
                    x * commons.BLOCK_SIZE,
                    y * commons.BLOCK_SIZE,
                    commons.BLOCK_SIZE,
                    commons.BLOCK_SIZE
                )

                # Clear the block area on the surface
                surface.fill(self.color_key, block_rect)

                # Redraw the block based on its layer and edges
                block = chunk.blocks_grid[0, y, x]
                edge = chunk.edges_matrix[0, y, x]

                block_1 = chunk.blocks_grid[1, y, x]
                edge_1 = chunk.edges_matrix[1, y, x]

                if ((edge != 0b1111 and edge != edge_1) or block == 0) and block_1:
                    # Render the background block
                    image_name = f"BACK_{BLOCK_METADATA.get_property_by_id(chunk.blocks_grid[1, y, x], 'image_name')}.{chunk.edges_matrix[1, y, x]:04b}"
                    surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)

                    surface.blit(IMAGE_LOADER.get_image(f"BREAKING_{breaking_level}.{edge:04b}"), block_rect)

                if block:
                    # Render the foreground block
                    image_name = f"{BLOCK_METADATA.get_property_by_id(block, 'image_name')}.{edge:04b}"
                    surface.blit(IMAGE_LOADER.get_image(image_name), block_rect)
                
                    surface.blit(IMAGE_LOADER.get_image(f"BREAKING_{breaking_level}.{edge:04b}"), block_rect)
                
                

                
        # Flag that the chunk has been rendered
        chunk.clear_changes()


    def render_moving_elements(self, elements: List[MovingElement], screen):
        """
        Renders a list of elements on the screen considering an offset (current_position).
        If an element does not have an image, a rectangle is rendered instead.

        :param elements: List of MovingElement objects to render.
        :param screen: Pygame screen surface to draw on.
        """
        for element in elements:
            # Compute the actual position considering the offset
            actual_x = element.rect.x - self.current_position[0]
            actual_y = element.rect.y - self.current_position[1]

            #print(f"Rendering {actual_x} {actual_y}")

            # Check if the element is within the screen boundaries
            if (0 <= actual_x < commons.WIDTH and
                0 <= actual_y < commons.HEIGHT):
                # Render the element's image if available, otherwise render a rectangle
                if hasattr(element, 'image') and element.image:
                    image = IMAGE_LOADER.get_image(element.image)
                    if offset := IMAGE_LOADER.get_image_atribute(element.image, "offset"):
                        screen.blit(image, (actual_x + offset[0], actual_y + offset[1]))
                        continue
                    
                    screen.blit(image, (actual_x, actual_y))
                else:
                    # Draw a rectangle if no image is present
                    pygame.draw.rect(
                        screen,
                        (255, 0, 0),  # Default color (red)
                        pygame.Rect(actual_x, actual_y, element.rect.width, element.rect.height)
                    )

    def render_all(self, screen, elements):
        """
        Renders the entire scene, including chunks and moving elements.

        :param screen: pygame.Surface, the main game display.
        """
        self.render_chunks(screen)
        self.render_moving_elements(elements, screen)

    def update_position(self, new_position):
        """
        Updates the current position and reloads chunks if necessary.

        :param new_position: Tuple[int, int], the new position (x, y) in world coordinates.
        """
        self.current_position = new_position
