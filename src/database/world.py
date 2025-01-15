from .world_loader import WorldLoader
from .world_elements.chunk import Chunk
from .world_elements.static_element import StaticElement
from .world_generator import WorldGenerator
from .world_elements.block_metadata_loader import BLOCK_METADATA
from .world_elements.item_metadata import ITEM_METADATA
from .world_elements.static_elements_manager import S_ELEMENT_METADATA_LOADER
from pygame.math import Vector2 as v2
from physics.player import Player
from pygame.rect import Rect
import pygame
from typing import Dict, Tuple, Set
import commons
from math import ceil
from threading import Thread


def get_chunk_block_coordinates(val: int) -> Tuple[int, int]:
    chunk_v, block_v_offset = divmod(val, commons.CHUNK_SIZE_PIXELS)
    block_v = block_v_offset // commons.BLOCK_SIZE
    if val < 0 and not block_v_offset:  # Handle negative coordinate edge case
        chunk_v -= 1
    return chunk_v, block_v, int(val // commons.BLOCK_SIZE) # Chunk pos, block pos in chunk, block absolute pos

class World:
    def __init__(self, world_name):
        """
        Initialize the world with its name, an empty chunk dictionary,
        a database interface, and a world generator.
        """
        self.world_name   : str         = world_name
        self.all_chunks   : Dict[tuple[int, int], Chunk]        = {}
        self.db_interface : WorldLoader = WorldLoader()
        self.world        : dict        = self.db_interface.get_world(self.world_name)
        self.world_id     : int         = self.world['world_id']
        self.generator    : WorldGenerator = WorldGenerator(self.world['seed'])
        self.mining_blocks: Dict[Tuple[int, int, int, int], int] = {}  # Tracks mining level of blocks being mined
        self.mining_objects: Dict[StaticElement, Chunk] = {}  # Tracks mining level of blocks being mined


        if self.world_id is None:
            raise ValueError(f"World '{self.world_name}' does not exist in the database.")

        self.load_all_data()

    def _gen(self, chunk: Chunk):
        chunk_x, chunk_y = chunk.pos
        self.generator.generate_chunk(chunk)

        # Verifying around chunks to update their edges matrix
        for i in range(0, 4):
            match i:
                case 0:
                    around_chunk = self.all_chunks.get((chunk_x-1, chunk_y))
                case 1:
                    around_chunk = self.all_chunks.get((chunk_x, chunk_y-1))
                case 2:
                    around_chunk = self.all_chunks.get((chunk_x+1, chunk_y))
                case 3:
                    around_chunk = self.all_chunks.get((chunk_x, chunk_y+1))
            
            if around_chunk: #Check if it exists
                self.generator.update_edges_matrix(chunk, around_chunk, index=i)
        
        chunk.completed_created = True

    def load_chunk(self, chunk_x, chunk_y):
        """
        Load a specific chunk by its coordinates.
        If the chunk does not exist in the database, generate a new chunk.
        """
        chunk_key = (chunk_x, chunk_y)
        if chunk_key in self.all_chunks:
            chunk = self.all_chunks[chunk_key]
            chunk.changes['all'] = True
            return chunk  # Return already loaded chunk
        

        if True or not blocks:
            # Generate a new chunk if no data exists
            chunk = Chunk(chunk_x, chunk_y)
            
            self._gen(chunk)

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

    def save_all_data(self):
        blocks_to_be_saved = []
        static_elements_to_be_saved = []
        chunks_to_be_saved = []
        for chunk in self.all_chunks.values():
            chunks_to_be_saved.append({'x': chunk.pos.x, 'y': chunk.pos.y})
            for x in range(commons.CHUNK_SIZE):
                for y in range(commons.CHUNK_SIZE):
                    l0 = {'x': x+chunk.pos.x*commons.CHUNK_SIZE, 'y': y+chunk.pos.y*commons.CHUNK_SIZE, 'type': int(chunk.blocks_grid[0, y, x]), 'layer': 0}
                    l1 = {'x': x+chunk.pos.x*commons.CHUNK_SIZE, 'y': y+chunk.pos.y*commons.CHUNK_SIZE, 'type': int(chunk.blocks_grid[1, y, x]), 'layer': 1}
                    blocks_to_be_saved.append(l0)
                    blocks_to_be_saved.append(l1)
            
            for s in chunk.world_elements:
                static_elements_to_be_saved.append(
                    {'x': s.rect.x, 
                     'y': s.rect.bottom,
                     'width': s.rect.w,
                     'height': s.rect.h,
                     'health': s.health,
                     'type': s.id
                     }
                )
        
        self.db_interface.save_blocks(self.world_id, blocks_to_be_saved)
        self.db_interface.save_static_objects(self.world_id, static_elements_to_be_saved)
        self.db_interface.save_chunks(self.world_id, chunks_to_be_saved)

    def load_all_data(self):
        self.load_all_chunks()

    def load_all_chunks(self, min_health=None):
        chunks = self.db_interface.load_chunks(self.world_id)
        for c in chunks:

            x, y = c['x'], c['y']
            new_chunk = Chunk(x, y)
            blocks = self.db_interface.load_blocks(self.world_id, x*commons.CHUNK_SIZE, (x+1)*commons.CHUNK_SIZE-1, y*commons.CHUNK_SIZE, (y+1)*commons.CHUNK_SIZE-1)
            for b in blocks:
                new_chunk.add_block(b[3], b[0]%commons.CHUNK_SIZE, b[1]%commons.CHUNK_SIZE, b[2])

            static_elements = self.db_interface.load_static_objects(self.world_id, x*commons.CHUNK_SIZE_PIXELS, (x+1)*commons.CHUNK_SIZE_PIXELS-1, y*commons.CHUNK_SIZE_PIXELS, (y+1)*commons.CHUNK_SIZE_PIXELS-1)

            for s in static_elements:
                new_chunk.add_static_element(StaticElement.from_dict(s))
            
            self.all_chunks[(x, y)] = new_chunk

            # Verifying around chunks to update their edges matrix
            for i in range(0, 4):
                match i:
                    case 0:
                        around_chunk = self.all_chunks.get((x-1, y))
                    case 1:
                        around_chunk = self.all_chunks.get((x, y-1))
                    case 2:
                        around_chunk = self.all_chunks.get((x+1, y))
                    case 3:
                        around_chunk = self.all_chunks.get((x, y+1))
                
                if around_chunk: #Check if it exists
                    self.generator.update_edges_matrix(new_chunk, around_chunk, index=i)
            
            new_chunk.changes['all'] = True

            new_chunk.completed_created = True
            

    def mine(self, position, dimensions, damage, delta_time):
        """
        Handles the mining logic for blocks in a grid-based chunk system.

        Args:
            position (tuple): The (x, y) coordinates of the starting position in pixels.
            dimensions (tuple): The dimensions (width, height) of the mining area in pixels.
            damage (float): The amount of damage dealt per unit of time.
            delta_time (float): The time since the last update.
        """
        
        # Extract coordinates
        x, y = position

        # Determine chunk and block indices from position
        chunk_x, block_x, block_abs_x = get_chunk_block_coordinates(x)
        chunk_y, block_y, block_abs_y = get_chunk_block_coordinates(y)


        final_chunk_x, final_block_x, final_abs_x = get_chunk_block_coordinates(x+dimensions[0])
        final_chunk_y, final_block_y, final_abs_y = get_chunk_block_coordinates(y+dimensions[1])

        rows_range = final_abs_y - block_abs_y
        cols_range = final_abs_x - block_abs_x




        visited_chunks : Set[Chunk] = set()

        for row_offset in range(0, rows_range + 1):
            for col_offset in range(0, cols_range + 1):
                # Determine the local block coordinates
                local_col = block_x + col_offset
                local_row = block_y + row_offset

                # Adjust chunk and block indices for wrapping
                current_chunk_x = chunk_x
                current_chunk_y = chunk_y

                if local_col < 0:
                    current_chunk_x -= 1
                    local_col %= commons.CHUNK_SIZE
                elif local_col >= commons.CHUNK_SIZE:
                    current_chunk_x += 1
                    local_col %= commons.CHUNK_SIZE

                if local_row < 0:
                    current_chunk_y -= 1
                    local_row %= commons.CHUNK_SIZE
                elif local_row >= commons.CHUNK_SIZE:
                    current_chunk_y += 1
                    local_row %= commons.CHUNK_SIZE

                # Retrieve the relevant chunk
                chunk_key = (current_chunk_x, current_chunk_y)
                chunk = self.all_chunks.get(chunk_key)

                # Skip if the chunk is not loaded
                if chunk is None:
                    continue
                
                visited_chunks.add(chunk)

                # Check for collidable blocks in the current position
                if chunk.blocks_grid[0, local_row, local_col] or chunk.blocks_grid[1, local_row, local_col]:
                    # Apply damage to the mining state
                    key = (current_chunk_x, current_chunk_y, local_row, local_col)
                    self.mining_blocks[key] = self.mining_blocks.get(key, 0) + damage * delta_time
        
        mining_area = pygame.Rect(x, y, dimensions[0], dimensions[1])

        for chunk in visited_chunks:
            for s_el in chunk.world_elements:
                if mining_area.colliderect(s_el.rect):
                    # Apply damage to the static object's mining state
                    s_el.take_damage(damage, delta_time)
                    self.mining_objects[s_el] = chunk
    
    def put(self, position: v2, dimensions: v2, block_type: int, quant: int, player: Player, down=False):
        """
        Handles the mining logic for blocks in a grid-based chunk system.

        Args:
            position (tuple): The (x, y) coordinates of the starting position in pixels.
            dimensions (tuple): The dimensions (width, height) of the mining area in pixels.
            damage (float): The amount of damage dealt per unit of time.
            delta_time (float): The time since the last update.
        """

        if BLOCK_METADATA.get_name_by_id(block_type) is None:
            print("Trying to put a non-registered block type")
            return
        
        # Extract coordinates
        x, y = int(position[0]), int(position[1])

        putted: int = 0

        # Determine chunk and block indices from position
        chunk_x, block_x, block_abs_x = get_chunk_block_coordinates(x)
        chunk_y, block_y, block_abs_y = get_chunk_block_coordinates(y)


        final_chunk_x, final_block_x, final_abs_x = get_chunk_block_coordinates(x+dimensions[0])
        final_chunk_y, final_block_y, final_abs_y = get_chunk_block_coordinates(y+dimensions[1])

        print(final_abs_x, block_abs_x)

        rows_range = final_abs_y - block_abs_y
        cols_range = final_abs_x - block_abs_x


        update_around = False

        visited_chunks : Set[Chunk] = set()

        for row_offset in range(0, rows_range + 1):
            for col_offset in range(0, cols_range + 1):
                # Determine the local block coordinates
                if quant == putted:
                    return putted
                
                local_col = block_x + col_offset
                local_row = block_y + row_offset

                # Adjust chunk and block indices for wrapping
                current_chunk_x = chunk_x
                current_chunk_y = chunk_y

                if local_col < 0:
                    current_chunk_x -= 1
                    local_col %= commons.CHUNK_SIZE
                elif local_col >= commons.CHUNK_SIZE:
                    current_chunk_x += 1
                    local_col %= commons.CHUNK_SIZE

                if local_row < 0:
                    current_chunk_y -= 1
                    local_row %= commons.CHUNK_SIZE
                elif local_row >= commons.CHUNK_SIZE:
                    current_chunk_y += 1
                    local_row %= commons.CHUNK_SIZE

                # Retrieve the relevant chunk
                chunk_key = (current_chunk_x, current_chunk_y)
                chunk = self.all_chunks.get(chunk_key)

                # Skip if the chunk is not loaded
                if chunk is None:
                    continue
                
                visited_chunks.add(chunk)

                # Calculate the world coordinates for the block
                block_world_x = current_chunk_x * commons.CHUNK_SIZE_PIXELS + local_col * commons.BLOCK_SIZE
                block_world_y = current_chunk_y * commons.CHUNK_SIZE_PIXELS + local_row * commons.BLOCK_SIZE

                b_rect = Rect(block_world_x, block_world_y, commons.BLOCK_SIZE, commons.BLOCK_SIZE)

                if b_rect.colliderect(player.rect): #Not putting where the player is
                    continue

                # Check for collidable blocks in the current position
                if chunk.blocks_grid[1, local_row, local_col] == 0 and down: #verify if it's air
                    #chunk.changes['block'].append((local_col, local_row))
                    if local_col == commons.CHUNK_SIZE - 1 or local_col == 0 or local_row == 0 or local_row == commons.CHUNK_SIZE -1:
                        update_around = True
                    
                    chunk.add_block(block_type, local_col, local_row, 1)
                    putted += 1
                
                if chunk.blocks_grid[0, local_row, local_col] == 0 and not down:
                    if local_col == commons.CHUNK_SIZE - 1 or local_col == 0 or local_row == 0 or local_row == commons.CHUNK_SIZE -1:
                        update_around = True
                    #chunk.changes['block'].append((local_col, local_row))
                    chunk.add_block(block_type, local_col, local_row, 0)
                    putted += 1
        
        if update_around and (cchunk := self.all_chunks.get((chunk_x, chunk_y), None)):
            print("AQQQQ")
            for i in range(0, 4):
                match i:
                    case 0: 
                        around_chunk = self.all_chunks.get((chunk_x-1, chunk_y))
                    case 1:
                        around_chunk = self.all_chunks.get((chunk_x, chunk_y-1))
                    case 2:
                        around_chunk = self.all_chunks.get((chunk_x+1, chunk_y))
                    case 3:
                        around_chunk = self.all_chunks.get((chunk_x, chunk_y+1))
                
                if around_chunk: #Check if it exists
                    self.generator.update_edges_matrix(cchunk, around_chunk, index=i)
        
        return putted
                    
        

    def update_world_state(self, delta_time: float):
        self.update_blocks_state(delta_time)
        self.update_objects_state(delta_time)
    
    def update_blocks_state(self, delta_time: float):
        """
        Updates the state of blocks being mined, applying damage and handling block destruction.
        """
        # Copy all mining blocks to iterate safely
        blocks_pos_damage = list(self.mining_blocks.items())


        for (chunk_x, chunk_y, row, col), damage in blocks_pos_damage:
            # Retrieve the chunk
            chunk = self.all_chunks.get((chunk_x, chunk_y))

            if chunk is None:
                continue

            # Check the primary and secondary block layers
            for layer in (0, 1):
                block = chunk.blocks_grid[layer, row, col]
                if block:
                    # Get the health of the block
                    health = BLOCK_METADATA.get_property_by_id(block, "health")
                    if damage >= health:
                        # Destroy the block
                        chunk.remove_block(col, row, layer)
                        self.mining_blocks.pop((chunk_x, chunk_y, row, col))

                        try:
                            chunk.changes['breaking'].pop((col, row))
                        except KeyError:
                            pass

                        for (item_name, num) in BLOCK_METADATA.get_property_by_id(block, 'drops').items():
                            for _ in range(num):
                                drop_event_dict = {
                                    'item': ITEM_METADATA.get_id_by_name(item_name),
                                    'pos': (commons.CHUNK_SIZE_PIXELS * chunk_x + commons.BLOCK_SIZE * col, commons.CHUNK_SIZE_PIXELS * chunk_y + commons.BLOCK_SIZE * row)
                                    }

                                pygame.event.post(pygame.event.Event(commons.ITEM_DROP_EVENT, drop_event_dict))
                        
                        if col == 0 and (side_chunk := self.all_chunks.get((chunk_x-1, chunk_y), None)):
                            
                            if side_chunk.edges_matrix[layer, row, commons.CHUNK_SIZE-1] & 0b0010:
                                side_chunk.edges_matrix[layer, row, commons.CHUNK_SIZE-1] -= 0b0010
                                side_chunk.changes['block'].append((commons.CHUNK_SIZE-1, row))
                            
                        if col == commons.CHUNK_SIZE-1 and (side_chunk := self.all_chunks.get((chunk_x+1, chunk_y), None)):
                            if side_chunk.edges_matrix[layer, row, 0] & 0b1000:
                                side_chunk.edges_matrix[layer, row, 0] -= 0b1000
                                side_chunk.changes['block'].append((0, row))
                        
                        if row == 0 and (side_chunk := self.all_chunks.get((chunk_x, chunk_y-1), None)):
                            if side_chunk.edges_matrix[layer, commons.CHUNK_SIZE-1, col] & 0b0001:
                                side_chunk.edges_matrix[layer, commons.CHUNK_SIZE-1, col] -= 0b0001
                                side_chunk.changes['block'].append((col, commons.CHUNK_SIZE-1))
                        if row == commons.CHUNK_SIZE-1 and (side_chunk := self.all_chunks.get((chunk_x, chunk_y+1), None)):
                            if side_chunk.edges_matrix[layer, 0, col] & 0b0100:
                                side_chunk.edges_matrix[layer, 0, col] -= 0b0100
                                side_chunk.changes['block'].append((col, 0))
                        
                    else:
                        # Decrease block damage, considering recuperation
                        new_damage = damage - commons.BLOCK_RECUPERATION_PERCENTAGE * delta_time
                        self.mining_blocks[(chunk_x, chunk_y, row, col)] = max(new_damage, 0)
                        if new_damage <= 0:
                            self.mining_blocks.pop((chunk_x, chunk_y, row, col))
                            chunk.changes['block'].append((col, row))
                            try:
                                chunk.changes['breaking'].pop((col, row))
                            except KeyError:
                                pass
                        else:
                            chunk.changes['breaking'][(col, row)] = int((new_damage / health) * commons.BREAKING_STAGES_NUMBER) # 0 to breaking stages number
                    break
            else:
                # Raise error if no block exists at the given position
                raise ValueError(f"Trying to mine a place with no blocks at ({chunk_x}, {chunk_y}, {row}, {col}).")


    def update_objects_state(self, delta_time: float):
        destroyed_objects = []
        
        for s_el, chunk in self.mining_objects.items():
            if s_el.is_destroyed():
                drops = S_ELEMENT_METADATA_LOADER.get_property_by_id(s_el.id, "drop")
                for iten_name, quant in drops.items():
                    item_id = ITEM_METADATA.get_id_by_name(iten_name)
                    for _ in range(quant):
                        pygame.event.post(pygame.event.Event(commons.ITEM_DROP_EVENT, {"item": item_id, "pos": s_el.rect.center}))
                chunk.world_elements.remove(s_el)
                destroyed_objects.append(s_el)
                pygame.event.post(pygame.event.Event(commons.S_ELEMENT_BROKEN))
            else:
                s_el.health += commons.BLOCK_RECUPERATION_PERCENTAGE * delta_time 

                if s_el.health >= s_el.max_health:
                    s_el.health = s_el.max_health
                    destroyed_objects.append(s_el)
        
        for o in destroyed_objects:
            self.mining_objects.pop(o)

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
        edge_blocks = []

        # Calculate the number of blocks in each direction based on dimensions
        rows_range = max(ceil(dimensions[1] / commons.BLOCK_SIZE), 1)  # Vertical range
        cols_range = max(ceil(dimensions[0] / commons.BLOCK_SIZE), 1)  # Horizontal range

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
                    continue# If the chunk isn't loaded, raise an error
                    raise RuntimeError("Attempting to get collision blocks from non-generated chunks")

                # Check if the block at the local position is collidable
                if chunk.collidable_grid[local_row, local_col]:
                    # Calculate the world coordinates for the block
                    block_world_x = current_chunk_x * commons.CHUNK_SIZE_PIXELS + local_col * commons.BLOCK_SIZE
                    block_world_y = current_chunk_y * commons.CHUNK_SIZE_PIXELS + local_row * commons.BLOCK_SIZE

                    # Append the block as a Rect object
                    collidable_blocks.append((chunk.edges_matrix[0, local_row, local_col], Rect(block_world_x, block_world_y, commons.BLOCK_SIZE, commons.BLOCK_SIZE)))

        return collidable_blocks


