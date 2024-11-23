import numpy as np
import pygame
from random import randint
from perlin_noise import PerlinNoise
from .world_elements.chunk import Chunk
from .world_elements.block_metadata_loader import BLOCK_METADATA


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
        self.noise_generator = PerlinNoise(octaves=3)

    def generate_chunk(self, chunk_pos):
        """
        Generates a chunk at a specific chunk position.

        :param chunk_pos: Tuple of (chunk_x, chunk_y) defining the chunk's position.
        :return: A Chunk object with generated terrain.
        """

        GRASS = BLOCK_METADATA.get_id_by_name("GRASS") # Get the ID for the "GRASS" block.
        DIRT  = BLOCK_METADATA.get_id_by_name("DIRT")  # Get the ID for the "DIRT" block.
        STONE = BLOCK_METADATA.get_id_by_name("STONE") # Get the ID for the "STONE" block.


        blocks_grid = np.zeros((self.LAYERS, Chunk.CHUNK_SIZE, Chunk.CHUNK_SIZE), dtype=int)
        collidible_grid = np.zeros((Chunk.CHUNK_SIZE, Chunk.CHUNK_SIZE), dtype=bool)

        # Generate block data for each position
        base_x, base_y = chunk_pos
        for y in range(Chunk.CHUNK_SIZE):
            for x in range(Chunk.CHUNK_SIZE):
                # Calculate global block position
                world_x = base_x * Chunk.CHUNK_SIZE + x
                world_y = base_y * Chunk.CHUNK_SIZE + y

                # Get Perlin noise value
                surface_y = int(self.noise_generator.get_noise(world_x/100, 0) * 100) # 0 - 100
                unoise = self.noise_generator.get_noise(world_x/100, world_y/100)  # 0.0 - 1.0

                # Map noise to two layers: 0 = air, 1 = ground, 2 = stone
                if world_y == surface_y: # Surface
                    if unoise >= 0.02:
                        blocks_grid[0, x, y] = GRASS
                        collidible_grid[x, y] = True
                    
                    blocks_grid[1, x, y] = GRASS
                
                elif world_y > surface_y: # Underground
                    if unoise >= 0.4:
                        blocks_grid[1, x, y] = STONE
                        blocks_grid[0, x, y] = STONE
                        collidible_grid[x, y] = True

                    elif unoise >= 0.3:
                        blocks_grid[1, x, y] = DIRT
                        blocks_grid[0, x, y] = DIRT
                        collidible_grid[x, y] = True
                    
                    





        # Create a Chunk object
        chunk = Chunk(
            pos=pygame.math.Vector2(chunk_pos),
            world_elements=[],  # No static elements yet
            blocks_grid=blocks_grid,
            collidible_grid=collidible_grid,
            has_changes=False
        )
        return chunk
