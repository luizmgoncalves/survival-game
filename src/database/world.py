from .db import WorldLoader
from .world_elements.chunk import Chunk

class World:
    def __init__(self, world_name):
        """
        Initialize the world with its name, an empty chunk dictionary,
        and a database interface.
        """
        self.world_name   : str         = world_name
        self.all_chunks   : dict        = {}
        self.db_interface : WorldLoader = WorldLoader()
        self.world_id     : int         = self._get_world_id()

        if self.world_id is None:
            raise ValueError(f"World '{self.world_name}' does not exist in the database.")

    def _get_world_id(self):
        """Retrieve the world ID from the database."""
        query = "SELECT world_id FROM Worlds WHERE name = ?"
        result = self.db_interface._execute_query(query, (self.world_name,))
        return result[0][0] if result else None

    def load_chunk(self, chunk_x, chunk_y, chunk_size):
        """
        Load a specific chunk by its coordinates.
        Data is loaded for the given chunk size, and optionally filtered by health.
        """
        chunk_key = (chunk_x, chunk_y)
        if chunk_key in self.all_chunks:
            return self.all_chunks[chunk_key]  # Return already loaded chunk

        # Create a new chunk
        chunk = Chunk(chunk_x, chunk_y)
        x_min = chunk_x * chunk_size
        x_max = x_min + chunk_size - 1
        y_min = chunk_y * chunk_size
        y_max = y_min + chunk_size - 1

        # Load blocks (no health filtering for blocks)
        blocks = self.db_interface.load_blocks(self.world_id, x_min, x_max, y_min, y_max)
        for block in blocks:
            chunk.add_block(block)

        # Load static objects with optional health filter
        static_objects = self.db_interface.load_static_objects(self.world_id, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
        for static_object in static_objects:
            chunk.add_static_object(static_object)

        # Load moving entities with optional health filter
        moving_entities = self.db_interface.load_moving_entities(self.world_id, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
        for entity in moving_entities:
            chunk.add_moving_entity(entity)

        # Store the chunk in the dictionary
        self.all_chunks[chunk_key] = chunk
        return chunk

    def load_all_chunks(self, chunk_size, min_health=None):
        """Load all chunks for the entire world with optional health filtering."""
        query = "SELECT size_x, size_y FROM Worlds WHERE world_id = ?"
        result = self.db_interface._execute_query(query, (self.world_id,))
        if not result:
            raise ValueError(f"World size could not be retrieved for '{self.world_name}'.")

        size_x, size_y = result[0]
        for chunk_x in range(size_x // chunk_size):
            for chunk_y in range(size_y // chunk_size):
                self.load_chunk(chunk_x, chunk_y, chunk_size, min_health)
