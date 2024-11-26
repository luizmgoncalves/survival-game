from .world_loader import WorldLoader
from .world_elements.chunk import Chunk
from .world_generator import WorldGenerator
from pygame.rect import Rect
from typing import Dict
import commons

class World:
    def __init__(self, world_name):
        """
        Initialize the world with its name, an empty chunk dictionary,
        a database interface, and a world generator.
        """
        self.world_name   : str         = world_name
        self.all_chunks   : Dict[tuple[int, int], Chunk]        = {}
        self.db_interface : WorldLoader = WorldLoader()
        self.world_id     : int         = self._get_world_id()
        self.generator    : WorldGenerator = WorldGenerator()

        if self.world_id is None:
            pass#raise ValueError(f"World '{self.world_name}' does not exist in the database.")

    def _get_world_id(self):
        """Retrieve the world ID from the database."""
        query = "SELECT world_id FROM Worlds WHERE name = ?"
        result = self.db_interface._execute_query(query, (self.world_name,))
        return result[0][0] if result else None

    def load_chunk(self, chunk_x, chunk_y):
        """
        Load a specific chunk by its coordinates.
        If the chunk does not exist in the database, generate a new chunk.
        """
        chunk_key = (chunk_x, chunk_y)
        if chunk_key in self.all_chunks:
            return self.all_chunks[chunk_key]  # Return already loaded chunk
        
        x_min = chunk_x * commons.CHUNK_SIZE
        x_max = x_min + commons.CHUNK_SIZE - 1
        y_min = chunk_y * commons.CHUNK_SIZE
        y_max = y_min + commons.CHUNK_SIZE - 1 

        # Try loading data from the database
        blocks = self.db_interface.load_blocks(self.world_id, x_min, x_max, y_min, y_max)
        static_objects = self.db_interface.load_static_objects(self.world_id, x_min, x_max, y_min, y_max)
        moving_entities = self.db_interface.load_moving_entities(self.world_id, x_min, x_max, y_min, y_max)

        if not blocks:
            # Generate a new chunk if no data exists
            chunk = self.generator.generate_chunk((chunk_x, chunk_y))

            # Optionally, save the generated chunk back to the database here

        else:
            # Create a new chunk
            chunk = Chunk(chunk_x, chunk_y)

            # Add loaded data to the chunk
            for block in blocks:
                chunk.add_block(block)
            for static_object in static_objects:
                chunk.add_static_object(static_object)
            # for entity in moving_entities:
            #    chunk.add_moving_entity(entity)

        # Store the chunk in the dictionary
        self.all_chunks[chunk_key] = chunk
        return chunk

    def load_all_chunks(self, min_health=None):
        """Load all chunks for the entire world with optional health filtering."""
        query = "SELECT size_x, size_y FROM Worlds WHERE world_id = ?"
        result = self.db_interface._execute_query(query, (self.world_id,))
        if not result:
            raise ValueError(f"World size could not be retrieved for '{self.world_name}'.")

        size_x, size_y = result[0]
        for chunk_x in range(size_x // commons.CHUNK_SIZE):
            for chunk_y in range(size_y // commons.CHUNK_SIZE):
                self.load_chunk(chunk_x, chunk_y, commons.CHUNK_SIZE, min_health)

    def get_collision_blocks_around(self, position, dimensions):
        """
        Get all collidable blocks in a rectangular area around a specific position.

        :param position: A tuple (x, y) representing the central position in world coordinates.
        :param dimensions: A tuple (width, height) specifying the rectangular area's size in world coordinates.
        :return: A list of Rect objects representing the collidable blocks.
        """
        # Extract coordinates
        x, y = position

        # Determine the chunk and block indices for the starting position
        chunk_x, block_x_offset = divmod(x, commons.CHUNK_SIZE_PIXELS)
        block_x = block_x_offset // commons.BLOCK_SIZE
        if x < 0 and not chunk_x:
            chunk_x -= 1

        chunk_y, block_y_offset = divmod(y, commons.CHUNK_SIZE_PIXELS)
        block_y = block_y_offset // commons.BLOCK_SIZE
        if y < 0 and not chunk_y:
            chunk_y -= 1

        # Initialize the list to store collidable blocks
        collidable_blocks = []

        # Calculate the number of blocks in each direction based on dimensions
        rows_range = max(dimensions[1] // commons.BLOCK_SIZE, 1)  # Vertical range
        cols_range = max(dimensions[0] // commons.BLOCK_SIZE, 1)  # Horizontal range

        # Iterate through the potential grid area
        for row_offset in range(-rows_range, rows_range+1):
            for col_offset in range(-cols_range, cols_range+1):
                # Calculate the relative coordinates of the block
                local_col = block_x + col_offset
                local_row = block_y + row_offset

                # Adjust chunk coordinates and block indices for wrapping
                current_chunk_x = chunk_x
                current_chunk_y = chunk_y

                # Handle column wrapping
                if local_col < 0:
                    current_chunk_x -= 1
                    local_col %= commons.CHUNK_SIZE
                elif local_col >= commons.CHUNK_SIZE:
                    current_chunk_x += 1
                    local_col %= commons.CHUNK_SIZE

                # Handle row wrapping
                if local_row < 0:
                    current_chunk_y -= 1
                    local_row %= commons.CHUNK_SIZE
                elif local_row >= commons.CHUNK_SIZE:
                    current_chunk_y += 1
                    local_row %= commons.CHUNK_SIZE

                # Get the chunk at the current position
                chunk_key = (current_chunk_x, current_chunk_y)
                chunk = self.all_chunks.get(chunk_key, None)

                if chunk is None:
                    # If the chunk isn't loaded, raise an error
                    raise RuntimeError("Attempting to get collision blocks from non-generated chunks")

                # Check if the block at the local position is collidable
                if chunk.collidable_grid[local_row, local_col]:
                    # Calculate the world coordinates for the block
                    block_world_x = current_chunk_x * commons.CHUNK_SIZE_PIXELS + local_col * commons.BLOCK_SIZE
                    block_world_y = current_chunk_y * commons.CHUNK_SIZE_PIXELS + local_row * commons.BLOCK_SIZE

                    # Append the block as a Rect object
                    collidable_blocks.append(Rect(block_world_x, block_world_y, commons.BLOCK_SIZE, commons.BLOCK_SIZE))

        return collidable_blocks


