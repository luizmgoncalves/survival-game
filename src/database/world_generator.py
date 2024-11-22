import numpy as np
import pygame
from random import randint
from perlin_noise import PerlinNoise


class WorldGenerator:
    """
    A class to generate chunks using the PerlinNoise class.
    """

    CHUNK_SIZE = 16
    LAYERS = 2  # Only two layers

    def __init__(self):
        """
        Initializes the WorldGenerator.

        :param noise_generator: An instance of PerlinNoise.
        """
        self.underground_noise_generator = PerlinNoise(octaves=3)
        self.surface_noise_generator = PerlinNoise(octaves=3)

    def generate_chunk(self, chunk_pos):
        """
        Generates a chunk at a specific chunk position.

        :param chunk_pos: Tuple of (chunk_x, chunk_y) defining the chunk's position.
        :return: A Chunk object with generated terrain.
        """
        blocks_grid = np.zeros((self.LAYERS, self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=int)
        collidible_grid = np.zeros((self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=bool)

        # Generate block data for each position
        base_x, base_y = chunk_pos
        for y in range(self.CHUNK_SIZE):
            for x in range(self.CHUNK_SIZE):
                # Calculate global block position
                world_x = base_x * self.CHUNK_SIZE + x
                world_y = base_y * self.CHUNK_SIZE + y

                # Get Perlin noise value
                surface_y = int(self.noise_generator.get_noise(world_x/100, 0) * 100)
                unoise = self.noise_generator.get_noise(world_x/100, world_y/100)

                # Map noise to two layers: 0 = air, 1 = ground, 2 = stone
                if world_y == surface_y:
                    if unoise >= 0.02:
                        blocks_grid[0, x, y] = 1

        # Create a Chunk object
        chunk = Chunk(
            pos=pygame.math.Vector2(chunk_pos),
            world_elements=[],  # No static elements yet
            blocks_grid=blocks_grid,
            collidible_grid=collidible_grid,
            has_changes=False
        )
        return chunk
