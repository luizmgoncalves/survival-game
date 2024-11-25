# File path: render_manager.py

import pygame
import commons
from database.world_elements.block_metadata_loader import BLOCK_METADATA

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
        self.color_key = color_key
        self.chunk_matrix = [[None for _ in range(3)] for _ in range(3)]
        self.surface_matrix = [[self.create_surface() for _ in range(3)] for _ in range(3)]
        self.moving_elements = []

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
        for i in range(3):
            for j in range(3):
                chunk_x = (self.current_position[0] // commons.CHUNK_SIZE_PIXELS) + (i - 1)
                chunk_y = (self.current_position[1] // commons.CHUNK_SIZE_PIXELS) + (j - 1)
                self.chunk_matrix[i][j] = world.load_chunk(chunk_x, chunk_y)

    def render_chunks(self, screen):
        """
        Renders the 3x3 chunk matrix onto the screen.

        :param screen: pygame.Surface, the main game display.
        """
        for i in range(3):
            for j in range(3):
                chunk_surface = self.surface_matrix[i][j]
                chunk_data = self.chunk_matrix[i][j]

                # Calculate chunk position relative to the current position
                chunk_x = (i - 1) * commons.CHUNK_SIZE_PIXELS - (self.current_position[0] % commons.CHUNK_SIZE_PIXELS)
                chunk_y = (j - 1) * commons.CHUNK_SIZE_PIXELS - (self.current_position[1] % commons.CHUNK_SIZE_PIXELS)

                self.render_single_chunk(chunk_surface, chunk_data)
                screen.blit(chunk_surface, (chunk_x, chunk_y))

    def render_single_chunk(self, surface, chunk):
        """
        Renders a single chunk onto a given surface.

        :param surface: pygame.Surface, the surface to draw on.
        :param chunk: Chunk, the chunk object containing blocks and elements to render.
        """
        if chunk is None or not chunk.has_changes:
            return  # Skip rendering if chunk is not loaded.

        surface.fill(self.color_key)  # Clear surface with transparent background.

        # Render the blocks in the chunk
        for x in range(chunk.blocks_grid.shape[1]):
            for y in range(chunk.blocks_grid.shape[2]):
                for layer in range(chunk.blocks_grid.shape[0]):
                    block = chunk.blocks_grid[layer, x, y]
                    if block:  # Skip empty blocks
                        block_color = BLOCK_METADATA.get_property_by_id(block, "color")
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
