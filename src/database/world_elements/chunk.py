import numpy as np
import pygame

class Chunk:
    # Class attribute for chunk size
    CHUNK_SIZE = 16  # Default chunk size (can be changed globally)

    def __init__(self, x, y, layers=3):
        """
        Represents a section of the world, loaded into memory as needed.

        :param x: The chunk's x-coordinate in the world grid.
        :param y: The chunk's y-coordinate in the world grid.
        :param layers: Number of block layers in the chunk.
        """
        self.pos = pygame.math.Vector2(x, y)  # Position of the chunk in chunk coordinates
        self.world_elements = []  # List of static elements (trees, chests, etc.)
        self.blocks_grid = np.zeros((layers, self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=object)  # 3D matrix for block layers
        self.collidable_grid = np.zeros((self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=bool)  # Collidable matrix
        self.has_changes = False  # Tracks whether the chunk has been modified

    def add_block(self, block, local_x, local_y, layer):
        """
        Adds a block to the chunk at the specified local position and layer.

        :param block: The block to add.
        :param local_x: The block's x-coordinate within the chunk.
        :param local_y: The block's y-coordinate within the chunk.
        :param layer: The layer index to which the block belongs.
        """
        self.blocks_grid[layer, local_y, local_x] = block
        if layer == 0 and block.is_collidable:  # Only base layer affects collision
            self.collidable_grid[local_y, local_x] = True
        self.has_changes = True

    def add_static_element(self, static_element):
        """
        Adds a static element (e.g., tree, chest) to the chunk.

        :param static_element: The static element to add.
        """
        self.world_elements.append(static_element)
        self.has_changes = True

    def clear_changes_flag(self):
        """Resets the `has_changes` flag to False after saving or syncing."""
        self.has_changes = False

    def get_block(self, local_x, local_y, layer):
        """
        Retrieves a block at the specified local position and layer.

        :param local_x: The block's x-coordinate within the chunk.
        :param local_y: The block's y-coordinate within the chunk.
        :param layer: The layer index from which to retrieve the block.
        :return: The block at the specified position and layer, or None if empty.
        """
        return self.blocks_grid[layer, local_y, local_x]

    def is_position_collidable(self, local_x, local_y):
        """
        Checks if a position in the chunk is collidable.

        :param local_x: The position's x-coordinate within the chunk.
        :param local_y: The position's y-coordinate within the chunk.
        :return: True if collidable, False otherwise.
        """
        return self.collidable_grid[local_y, local_x]

    @classmethod
    def set_chunk_size(cls, size):
        """Sets the global chunk size."""
        cls.CHUNK_SIZE = size

    def __repr__(self):
        """Returns a string representation of the chunk."""
        return f"Chunk(pos={self.pos}, size={self.CHUNK_SIZE}, layers={self.blocks_grid.shape[0]})"
