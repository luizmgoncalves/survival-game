import numpy as np
import pygame
from random import randint
from perlin_noise import PerlinNoise
from .world_elements.chunk import Chunk
from .world_elements.block_metadata_loader import BLOCK_METADATA
import commons
import noise

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
        #self.underground_noise_generator = PerlinNoise(octaves=4)
        #self.surface_noise_generator = PerlinNoise(octaves=2)

    
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
        edges_matrix = np.zeros((2, commons.CHUNK_SIZE, commons.CHUNK_SIZE), dtype=int)

        #noise = self.perlin.gen

        # Generate block data for each position
        base_x, base_y = chunk_pos
        chunk_world_x = base_x * commons.CHUNK_SIZE
        chunk_world_y = base_y * commons.CHUNK_SIZE

        for y in range(commons.CHUNK_SIZE):
            for x in range(commons.CHUNK_SIZE):
                # Calculate global block position
                world_x = chunk_world_x + x
                world_y = chunk_world_y + y

                # Get Perlin noise value
                surface_y = (noise.pnoise1(world_x*0.0009) * commons.CHUNK_SIZE * 4) # 0 - 100
                surface_y += (noise.pnoise1(world_x*0.05) * commons.CHUNK_SIZE*0.25)
                surface_y = round(surface_y)
                unoise = (noise.pnoise2(world_x*0.09, world_y*0.09) * 0.3)  # 0.0 - 1.0
                unoise += (noise.pnoise2(world_x*0.02, world_y*0.02))
                unoise = abs(unoise)

                # Map noise to two layers: 0 = air, 1 = ground, 2 = stone
                if world_y == surface_y: # Surface
                    if unoise >= 0.01:
                        blocks_grid[0, y, x] = GRASS
                        collidible_grid[y, x] = True
                    
                    #blocks_grid[1, y, x] = GRASS
                    #collidible_grid[y, x] = True
                
                elif world_y > surface_y + commons.CHUNK_SIZE and world_y > surface_y: # Underground
                    if unoise >= 0.3:
                        blocks_grid[1, y, x] = STONE
                        blocks_grid[0, y, x] = STONE
                        collidible_grid[y, x] = True

                    elif unoise >= 0.1:
                        blocks_grid[1, y, x] = DIRT
                        blocks_grid[0, y, x] = DIRT
                        collidible_grid[y, x] = True
                elif world_y > surface_y:
                    if unoise >= 0.4:
                        blocks_grid[1, y, x] = DIRT
                        blocks_grid[0, y, x] = DIRT
                        collidible_grid[y, x] = True

                    elif unoise >= 0.03:
                        blocks_grid[1, y, x] = DIRT
                        blocks_grid[0, y, x] = DIRT
                        collidible_grid[y, x] = True
                
                if blocks_grid[0, y, x]:
                    if y and blocks_grid[0, y-1, x]:
                        edges_matrix[0, y-1, x] += 0b0001
                        edges_matrix[0, y, x] += 0b0100
                    
                    if x and blocks_grid[0, y, x-1]:
                        edges_matrix[0, y, x-1] += 0b0010
                        edges_matrix[0, y, x] += 0b1000
                
                if blocks_grid[1, y, x]:
                    if y and blocks_grid[1, y-1, x]:
                        edges_matrix[1, y-1, x] += 0b0001
                        edges_matrix[1, y, x] += 0b0100
                    
                    if x and blocks_grid[1, y, x-1]:
                        edges_matrix[1, y, x-1] += 0b0010
                        edges_matrix[1, y, x] += 0b1000
                
                    





        # Create a Chunk object
        chunk = Chunk(
            x=chunk_pos[0],
            y=chunk_pos[1]
        )

        chunk.blocks_grid = blocks_grid
        chunk.collidable_grid = collidible_grid
        chunk.edges_matrix = edges_matrix
        chunk.changes['all'] = True

        return chunk

    def update_edges_matrix(self, chunk1: Chunk, chunk2: Chunk, index: int):
        match index:
            case 0: # left
                for i in range(commons.CHUNK_SIZE):
                    if chunk2.blocks_grid[0, i, -1] and chunk1.blocks_grid[0, i, 0]: # Last column <-> First column
                        chunk1.edges_matrix[0, i, 0] += 0b1000
                        chunk2.edges_matrix[0, i, -1] += 0b0010

                    if chunk2.blocks_grid[1, i, -1] and chunk1.blocks_grid[1, i, 0]: # Last column <-> First column
                        chunk1.edges_matrix[1, i, 0] += 0b1000
                        chunk2.edges_matrix[1, i, -1] += 0b0010
                
                chunk2.changes['column'] = [commons.CHUNK_SIZE-1]
                chunk1.changes['column'] = [0]
            case 1: # top
                for i in range(commons.CHUNK_SIZE):
                    if chunk2.blocks_grid[0, -1, i] and chunk1.blocks_grid[0, 0, i]: # Last column <-> First column
                        chunk1.edges_matrix[0, 0, i] += 0b0100
                        chunk2.edges_matrix[0, -1, i] += 0b0001

                    if chunk2.blocks_grid[1, -1, i] and chunk1.blocks_grid[1, 0, i]: # Last column <-> First column
                        chunk1.edges_matrix[1, 0, i] += 0b0100
                        chunk2.edges_matrix[1, -1, i] += 0b0001
                
                chunk2.changes['line'] = [commons.CHUNK_SIZE-1]
                chunk1.changes['line'] = [0]
            case 2: # right
                for i in range(commons.CHUNK_SIZE):
                    if chunk2.blocks_grid[0, i, 0] and chunk1.blocks_grid[0, i, -1]: # First column <-> Last column
                        chunk1.edges_matrix[0, i, -1] += 0b0010
                        chunk2.edges_matrix[0, i, 0] += 0b1000

                    if chunk2.blocks_grid[1, i, 0] and chunk1.blocks_grid[1, i, -1]: # First column <-> Last column
                        chunk1.edges_matrix[1, i, -1] += 0b0010
                        chunk2.edges_matrix[1, i, 0] += 0b1000
                
                chunk2.changes['column'] = [0]
                chunk1.changes['column'] = [commons.CHUNK_SIZE-1]
            case 3: #bottom
                for i in range(commons.CHUNK_SIZE):
                    if chunk2.blocks_grid[0, 0, i] and chunk1.blocks_grid[0, -1, i]: # First row <-> Last row
                        chunk1.edges_matrix[0, -1, i] += 0b0001
                        chunk2.edges_matrix[0, 0, i] += 0b0100

                    if chunk2.blocks_grid[1, 0, i] and chunk1.blocks_grid[1, -1, i]: # First row <-> Last row
                        chunk1.edges_matrix[1, -1, i] += 0b0001
                        chunk2.edges_matrix[1, 0, i] += 0b0100
                
                chunk2.changes['line'] = [0]
                chunk1.changes['line'] = [commons.CHUNK_SIZE-1]

