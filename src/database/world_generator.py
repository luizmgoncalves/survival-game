import numpy as np
import pygame
from random import randint
from perlin_noise import PerlinNoise
from .world_elements.chunk import Chunk
from .world_elements.block_metadata_loader import BLOCK_METADATA
import commons
import numba

class WorldGenerator:
    """
    A class to generate chunks using the PerlinNoise class.
    """
    LAYERS = 2  # Only two layers

    def __init__(self):
        """
        Initializes the WorldGenerator.

        :param noise_generator: An instance of PerlinNoise.
        """
        self.underground_noise_generator = PerlinNoise(octaves=6)
        self.surface_noise_generator = PerlinNoise(octaves=2)

    
    def generate_chunk(self, chunk_pos):
        """
        Generates a chunk at a specific chunk position.

        :param chunk_pos: Tuple of (chunk_x, chunk_y) defining the chunk's position.
        :return: A Chunk object with generated terrain.
        """

        GRASS = BLOCK_METADATA.get_id_by_name("GRASS") # Get the ID for the "GRASS" block.
        DIRT  = BLOCK_METADATA.get_id_by_name("DIRT")  # Get the ID for the "DIRT" block.
        STONE = BLOCK_METADATA.get_id_by_name("STONE") # Get the ID for the "STONE" block.


        blocks_grid = np.zeros((self.LAYERS, commons.CHUNK_SIZE, commons.CHUNK_SIZE), dtype=int)
        collidible_grid = np.zeros((commons.CHUNK_SIZE, commons.CHUNK_SIZE), dtype=bool)

        # Generate block data for each position
        base_x, base_y = chunk_pos
        for y in range(commons.CHUNK_SIZE):
            for x in range(commons.CHUNK_SIZE):
                # Calculate global block position
                world_x = base_x * commons.CHUNK_SIZE + x
                world_y = base_y * commons.CHUNK_SIZE + y

                # Get Perlin noise value
                surface_y = int(self.surface_noise_generator([world_x/100, 0]) * commons.CHUNK_SIZE * 4) # 0 - 100
                unoise = abs(self.underground_noise_generator([world_x/100, world_y/100]))  # 0.0 - 1.0

                # Map noise to two layers: 0 = air, 1 = ground, 2 = stone
                if world_y == surface_y: # Surface
                    if unoise >= 0.02:
                        blocks_grid[0, y, x] = GRASS
                        collidible_grid[y, x] = True
                    
                    blocks_grid[1, y, x] = GRASS
                    collidible_grid[y, x] = True
                
                elif world_y > surface_y: # Underground
                    if unoise >= 0.09:
                        blocks_grid[1, y, x] = STONE
                        blocks_grid[0, y, x] = STONE
                        collidible_grid[y, x] = True

                    elif unoise >= 0.04:
                        blocks_grid[1, y, x] = DIRT
                        blocks_grid[0, y, x] = DIRT
                        collidible_grid[y, x] = True
                    
                    





        # Create a Chunk object
        chunk = Chunk(
            x=chunk_pos[0],
            y=chunk_pos[1]
        )

        chunk.blocks_grid = blocks_grid
        chunk.collidable_grid = collidible_grid

        return chunk
