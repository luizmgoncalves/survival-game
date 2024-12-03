import numpy as np
import pygame
import commons
from typing import Dict
from .block_metadata_loader import BLOCK_METADATA

class Chunk:

    def __init__(self, x, y, layers=2):
        """
        Represents a section of the world, loaded into memory as needed.

        :param x: The chunk's x-coordinate in the world grid.
        :param y: The chunk's y-coordinate in the world grid.
        :param layers: Number of block layers in the chunk.
        """
        self.pos = pygame.math.Vector2(x, y)  # Position of the chunk in chunk coordinates
        self.world_elements = []  # List of static elements (trees, chests, etc.)
        self.blocks_grid = np.zeros((layers, commons.CHUNK_SIZE, commons.CHUNK_SIZE), dtype=int)  # 3D matrix for block layers
        self.collidable_grid = np.zeros((commons.CHUNK_SIZE, commons.CHUNK_SIZE), dtype=bool)  # Collidable matrix
        self.edges_matrix = np.ones((2, commons.CHUNK_SIZE, commons.CHUNK_SIZE), dtype=int)  # Collidable matrix

        # Changes dict track the changings of the Chunk for Chunk rendering optimization
        # It can have the line key with the lines that have changed
        # It can have the column key with the lines that have changed
        # It can have the block key with the blocks that must be re-rendered
        # It can have a all key with some irrelevant value that means that the entire Chunk must be rendered
        # If the all key are in self.changes all other keys are ignored
        self.changes: Dict[str, list] = {'all': False,
                                         'line': [],
                                         'column': [],
                                         'block': []}
    
    def clear_changes(self):
        self.changes = {'all': False,
                        'line': [],
                        'column': [],
                        'block': []}

    def add_block(self, block, col, row, layer):
        """
        Adds a block to the chunk at the specified local position and layer.

        :param block: The block to add.
        :param col: The block's x-coordinate within the chunk.
        :param row: The block's y-coordinate within the chunk.
        :param layer: The layer index to which the block belongs.
        """

        need_around_update = bool(self.blocks_grid[layer, row, col]) ^ bool(block)

        need_update = self.blocks_grid[layer, row, col] != block and (layer == 1 and not self.blocks_grid[0, row, col] or layer == 0)

        self.blocks_grid[layer, row, col] = block

        if layer == 0 and BLOCK_METADATA.get_property_by_id(block, 'collidable'):  # Only base layer affects collision
            self.collidable_grid[row, col] = True
        elif layer == 0:
            self.collidable_grid[row, col] = False
        
        if need_around_update:
            self.update_around(block, layer, col, row)
        if need_update:
            self.changes['block'].append((layer, col, row))
    
    def remove_block(self, col, row, layer):
        """
        Removes a block from the chunk at the specified local position and layer.

        :param col: The block's x-coordinate within the chunk.
        :param row: The block's y-coordinate within the chunk.
        :param layer: The layer index from which the block is being removed.
        """

        block = self.blocks_grid[layer, row, col]
        if not block:
            # No block to remove
            return

        self.changes['block'].append((col, row))

        # Mark the block as removed
        self.blocks_grid[layer, row, col] = 0
        self.edges_matrix[layer, row, col] = 0b0000

        # Update collision grid if on the base layer
        if layer == 0:
            self.collidable_grid[row, col] = False

        # Update neighboring blocks
        self.update_around(0, layer, col, row)

    
    def update_around(self, block, layer, col, row):
        if block:
            # Left (col - 1)
            if col > 0 and self.blocks_grid[layer, row, col - 1] and not (self.edges_matrix[layer, row, col - 1] & 0b0010):
                self.edges_matrix[layer, row, col - 1] += 0b0010
                self.changes['block'].append((col-1, row))
            
            # Right (col + 1)
            if col < commons.CHUNK_SIZE - 1 and self.blocks_grid[layer, row, col + 1] and not (self.edges_matrix[layer, row, col + 1] & 0b1000):
                self.edges_matrix[layer, row, col + 1] += 0b1000
                self.changes['block'].append((col+1, row))
            
            # Up (row - 1)
            if row > 0 and self.blocks_grid[layer, row - 1, col] and not (self.edges_matrix[layer, row - 1, col] & 0b0001):
                self.edges_matrix[layer, row - 1, col] += 0b0001
                self.changes['block'].append((col, row-1))
            
            # Down (row + 1)
            if row < commons.CHUNK_SIZE - 1 and self.blocks_grid[layer, row + 1, col] and not (self.edges_matrix[layer, row + 1, col] & 0b0100):
                self.edges_matrix[layer, row + 1, col] += 0b0100
                self.changes['block'].append((col, row+1))
        
        else:
            # Left (col - 1)
            if col > 0 and self.blocks_grid[layer, row, col - 1] and (self.edges_matrix[layer, row, col - 1] & 0b0010):
                self.edges_matrix[layer, row, col - 1] -= 0b0010
                self.changes['block'].append((col-1, row))
            
            # Right (col + 1)
            if col < commons.CHUNK_SIZE - 1 and self.blocks_grid[layer, row, col + 1] and (self.edges_matrix[layer, row, col + 1] & 0b1000):
                self.edges_matrix[layer, row, col + 1] -= 0b1000
                self.changes['block'].append((col+1, row))
            
            # Up (row - 1)
            if row > 0 and self.blocks_grid[layer, row - 1, col] and (self.edges_matrix[layer, row - 1, col] & 0b0001):
                self.edges_matrix[layer, row - 1, col] -= 0b0001
                self.changes['block'].append((col, row-1))
            
            # Down (row + 1)
            if row < commons.CHUNK_SIZE - 1 and self.blocks_grid[layer, row + 1, col] and (self.edges_matrix[layer, row + 1, col] & 0b0100):
                self.edges_matrix[layer, row + 1, col] -= 0b0100
                self.changes['block'].append((col, row+1))
            

        
    def add_static_element(self, static_element):
        """
        Adds a static element (e.g., tree, chest) to the chunk.

        :param static_element: The static element to add.
        """
        self.world_elements.append(static_element)