import sqlite3
import os
import commons
import random
from utils.inventory import Inventory
from typing import List, Any, Dict

class WorldLoader:
    FILENAME = 'game.db'

    def __init__(self):
        """Initialize the WorldLoader with the database name."""
        self.db_name = commons.DEFAULT_DB_PATH + self.FILENAME
        self._ensure_database()

    def _ensure_database(self):
        """Check if the database exists; if not, create it."""
        if not os.path.exists(self.db_name):
            print(f"Database {self.db_name} not found. Creating it...")
            self.create_database()
        else:
            print(f"Database {self.db_name} found.")

    def create_database(self):
        """Create the database and all necessary tables."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Enable foreign keys
            cursor.execute('PRAGMA foreign_keys = ON;')  # Adicionado para ativar as chaves estrangeiras

            # Create Worlds table without size_x and size_y
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Worlds (
                    world_id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    deaths INTEGER DEFAULT 0,
                    kills INTEGER DEFAULT 0,
                    seed INTEGER DEFAULT 4
                );
            ''')

            # Create PlayerLocations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS PlayerLocations (
                    world_id INTEGER NOT NULL,
                    x INTEGER NOT NULL,
                    y INTEGER NOT NULL,
                    PRIMARY KEY (world_id),
                    FOREIGN KEY (world_id) REFERENCES Worlds(world_id) ON DELETE CASCADE
                );
            ''')

            # Create Inventory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Inventory (
                    world_id INTEGER NOT NULL,
                    slot INTEGER NOT NULL,
                    item_count INTEGER NOT NULL,
                    item_type INTEGER NOT NULL,
                    PRIMARY KEY (world_id, slot),
                    FOREIGN KEY (world_id) REFERENCES Worlds(world_id) ON DELETE CASCADE
                );
            ''')

            # Create StaticObjects table with health column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS StaticObjects (
                    object_id INTEGER,
                    world_id INTEGER,
                    x INTEGER,
                    y INTEGER,
                    type TEXT,
                    width INTEGER DEFAULT 1,
                    height INTEGER DEFAULT 1,
                    health INTEGER DEFAULT 100,
                    PRIMARY KEY (world_id, x, y),
                    FOREIGN KEY(world_id) REFERENCES Worlds(world_id) ON DELETE CASCADE
                );
            ''')

            # Create MovingEntities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS MovingEntities (
                    entity_id INTEGER PRIMARY KEY,
                    world_id INTEGER,
                    x INTEGER,
                    y INTEGER,
                    type TEXT,
                    health INTEGER,
                    speed INTEGER,
                    state TEXT DEFAULT 'active',
                    FOREIGN KEY(world_id) REFERENCES Worlds(world_id) ON DELETE CASCADE
                );
            ''')

            # Create Blocks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Blocks (
                    world_id INTEGER,
                    x INTEGER,
                    y INTEGER,
                    layer INTEGER,
                    type INTEGER,
                    PRIMARY KEY (world_id, x, y, layer),
                    FOREIGN KEY(world_id) REFERENCES Worlds(world_id) ON DELETE CASCADE
                );
            ''')

            # Create Chunks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Chunks (
                    world_id INTEGER NOT NULL,
                    x INTEGER NOT NULL,
                    y INTEGER NOT NULL,
                    PRIMARY KEY (world_id, x, y),
                    FOREIGN KEY(world_id) REFERENCES Worlds(world_id) ON DELETE CASCADE
                );
            ''')

            print("Database and tables created successfully.")
    
    def create_world(self, name, seed=None):
        """
        Create a new world with the given name, score, and seed.

        Args:
            name (str): The name of the world.
            seed (int): The seed value for the world (default is None).
        
        Raises:
            ValueError: If a world with the same name already exists.
        """

        if seed is None:
            seed = int(random.random() * 1000)

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Check if the world already exists
                cursor.execute('SELECT * FROM Worlds WHERE name = ?', (name,))
                if cursor.fetchone():
                    print(f"A world with the name '{name}' already exists.")
                    return False

                # Insert the new world into the Worlds table
                cursor.execute('''
                    INSERT INTO Worlds (name, seed)
                    VALUES (?, ?);
                ''', (name, seed))

                print(f"World '{name}' created successfully, seed {seed}.")

        except sqlite3.Error as e:
            print(f"An error occurred while creating the world: {e}")
            return False

        return True
    
    def delete_world(self, name):
        """
        Delete a specific world and all its associated data from the database.

        Args:
            name (str): The name of the world to be deleted.

        Returns:
            bool: True if the world was successfully deleted, False if the world was not found.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Enable foreign keys
                cursor.execute('PRAGMA foreign_keys = ON;')  # Garantir que as chaves estrangeiras estejam ativadas

                # Check if the world exists
                cursor.execute('SELECT world_id FROM Worlds WHERE name = ?', (name,))
                world = cursor.fetchone()
                if not world:
                    print(f"World '{name}' does not exist.")
                    return False

                # Delete the world (triggers cascading deletion)
                cursor.execute('DELETE FROM Worlds WHERE name = ?', (name,))
                conn.commit()

                print(f"World '{name}' and all associated data have been successfully deleted.")
                return True
        except sqlite3.Error as e:
            print(f"An error occurred while deleting the world: {e}")
            return False
    
    def set_world_score(self, name, score):
        """
        Update the score for a specific world.
        
        Args:
            name (str): The name of the world.
            score (int): The new score to set.
        
        Raises:
            ValueError: If the world does not exist.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Check if the world exists
                cursor.execute('SELECT world_id FROM Worlds WHERE name = ?', (name,))
                if not cursor.fetchone():
                    raise ValueError(f"World '{name}' does not exist.")

                # Update the world's score
                cursor.execute('''
                    UPDATE Worlds
                    SET score = ?
                    WHERE name = ?;
                ''', (score, name))
                conn.commit()

                print(f"Score for world '{name}' updated to {score}.")
        except sqlite3.Error as e:
            print(f"An error occurred while updating the score: {e}")

    def save_player_location(self, world_id, x, y, deaths:int=0, kills: int=0):
        """Save the player's location in the given world."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                # Use INSERT OR REPLACE to update location if it already exists
                cursor.execute('''
                    INSERT OR REPLACE INTO PlayerLocations (world_id, x, y)
                    VALUES (?, ?, ?);
                ''', (world_id, x, y))
                print(f"Player location saved for world_id={world_id}: ({x}, {y})")
            except sqlite3.Error as e:
                print(f"Error saving player location: {e}")

    def load_player_location(self, world_id):
        """Load the player's location for the given world."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT x, y FROM PlayerLocations
                    WHERE world_id = ?;
                ''', (world_id,))
                result = cursor.fetchone()
                if result:
                    print(f"Player location loaded for world_id={world_id}: {result}")
                    return result  # Returns a tuple (x, y, kills, deaths)
                else:
                    print(f"No location found for world_id={world_id}.")
                    return None
            except sqlite3.Error as e:
                print(f"Error loading player location: {e}")
                return None


    def save_inventory(self, world_id, inventory: Inventory):
        """Save the inventory for a specific world.

        Args:
            world_id (int): The ID of the world.
            inventory (list of dict): A list of inventory slots, where each slot is a dictionary with keys:
                - slot (int): Slot index.
                - item_count (int): Number of items in the slot.
                - item_type (int): Type of item in the slot.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Insert new inventory data
            for i in range(inventory.max_slots):
                slot = i
                quant, item = inventory.get_slot(i)
                cursor.execute(
                    "INSERT OR REPLACE INTO Inventory (world_id, slot, item_count, item_type) VALUES (?, ?, ?, ?)",
                    (world_id, slot, quant, item)
                )

            conn.commit()
            print(f"Inventory for world_id {world_id} saved successfully.")

    def load_inventory(self, world_id, inventory: Inventory):
        """Load the inventory for a specific world.

        Args:
            world_id (int): The ID of the world.

        Returns:
            list of dict: A list of inventory slots, where each slot is a dictionary with keys:
                - slot (int): Slot index.
                - item_count (int): Number of items in the slot.
                - item_type (int): Type of item in the slot.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Fetch inventory data
            cursor.execute("SELECT slot, item_count, item_type FROM Inventory WHERE world_id = ?", (world_id,))
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            for row in rows:
                slot, quant, item = row
                inventory.set_slot(slot, str(item), quant)

            print(f"Inventory for world_id {world_id} loaded successfully.")
            return inventory


    def _execute_query(self, query, params):
        """Helper method to execute a query and fetch results."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def save_blocks(self, world_id, blocks):
        """
        Save a list of blocks to the database.
        :param world_id: The ID of the world.
        :param blocks: A list of dictionaries, each representing a block.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO Blocks (world_id, x, y, layer, type)
                VALUES (?, ?, ?, ?, ?)
            ''', [(world_id, block['x'], block['y'], block['layer'], block['type']) for block in blocks])
            conn.commit()

    def load_blocks(self, world_id, x_min, x_max, y_min, y_max):
        """
        Load blocks for a specific world within a coordinate range.
        :param world_id: The ID of the world.
        :param x_min: Minimum x-coordinate.
        :param x_max: Maximum x-coordinate.
        :param y_min: Minimum y-coordinate.
        :param y_max: Maximum y-coordinate.
        :return: A list of dictionaries representing the blocks.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT x, y, layer, type
                FROM Blocks
                WHERE world_id = ? AND x BETWEEN ? AND ? AND y BETWEEN ? AND ?
            ''', (world_id, x_min, x_max, y_min, y_max))
            rows = cursor.fetchall()
            return rows

    def save_static_objects(self, world_id, static_objects):
        """
        Save a list of static objects to the database.
        :param world_id: The ID of the world.
        :param static_objects: A list of dictionaries, each representing a static object.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO StaticObjects (world_id, x, y, type, width, height, health)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [(world_id, obj['x'], obj['y'], obj['type'], obj.get('width', 1), obj.get('height', 1), obj.get('health', 100)) for obj in static_objects])
            conn.commit()
            print(f"Saved {len(static_objects)} static objects for world {world_id}.")

    def load_static_objects(self, world_id, x_min, x_max, y_min, y_max):
        """
        Load static objects for a specific world within a coordinate range.
        :param world_id: The ID of the world.
        :param x_min: Minimum x-coordinate.
        :param x_max: Maximum x-coordinate.
        :param y_min: Minimum y-coordinate.
        :param y_max: Maximum y-coordinate.
        :return: A list of dictionaries representing the static objects.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT x, y, type, width, height, health
                FROM StaticObjects
                WHERE world_id = ? AND x BETWEEN ? AND ? AND y BETWEEN ? AND ?
            ''', (world_id, x_min, x_max, y_min, y_max))
            rows = cursor.fetchall()
            return [{'x': row[0], 'y': row[1], 'type': row[2], 'width': row[3], 'height': row[4], 'health': row[5]} for row in rows]

    def save_chunks(self, world_id, chunks):
        """
        Save a list of chunks to the database.
        :param world_id: The ID of the world.
        :param chunks: A list of dictionaries, each representing a chunk with x and y coordinates.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR IGNORE INTO Chunks (world_id, x, y)
                VALUES (?, ?, ?)
            ''', [(world_id, chunk['x'], chunk['y']) for chunk in chunks])
            conn.commit()
            print(f"Saved {len(chunks)} chunks for world {world_id}.")

    def load_chunks(self, world_id):
        """
        Load all chunks for a specific world.
        :param world_id: The ID of the world.
        :return: A list of dictionaries representing the chunks.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT x, y
                FROM Chunks
                WHERE world_id = ?
            ''', (world_id,))
            rows = cursor.fetchall()
            return [{'x': row[0], 'y': row[1]} for row in rows]


    def load_moving_entities(self, world_id, entity_type: int, x_min: int, x_max: int, y_min: int, y_max: int):
        """Load moving entities for a specific world, optionally filtered by type, health, and position."""
        query = "SELECT * FROM MovingEntities WHERE world_id = ?"
        params = [world_id]

        
        query += " AND type = ?"
        params.append(entity_type)
    
        query += " AND x BETWEEN ? AND ?"
        params.extend([x_min, x_max])
    
        query += " AND y BETWEEN ? AND ?"
        params.extend([y_min, y_max])

        return self._execute_query(query, tuple(params))


    def get_world_id_by_name(self, name):
        """Retrieve the world ID for a given world name."""
        query = "SELECT world_id FROM Worlds WHERE name = ?"
        result = self._execute_query(query, (name,))
        return result[0][0] if result else None

    def get_worlds(self):
        """
        Retrieve a list of all worlds already created.

        Returns:
            list: A list of dictionaries, where each dictionary represents a world
                with keys 'world_id', 'name', 'score', and 'seed'.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Query all worlds from the Worlds table
                cursor.execute('SELECT world_id, name, seed FROM Worlds')
                rows = cursor.fetchall()

                # Convert the result to a list of dictionaries
                worlds = [{'world_id': row[0], 'name': row[1], 'seed': row[2]} for row in rows]

                return worlds
        except sqlite3.Error as e:
            print(f"An error occurred while fetching the worlds: {e}")
            return []
        
    def get_world(self, name):
        """
        Retrieve a specific world by its name.

        Args:
            name (str): The name of the world to retrieve.

        Returns:
            dict or None: A dictionary representing the world with keys 'world_id',
                        'name', 'score', and 'seed' if found; None if the world does not exist.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Query the world from the Worlds table
                cursor.execute('SELECT world_id, name, deaths, kills, seed FROM Worlds WHERE name = ?', (name,))
                row = cursor.fetchone()

                if row:
                    # Return the world as a dictionary
                    return {'world_id': row[0], 'name': row[1], 'deaths': row[2], 'kills': row[3], 'seed': row[4]}
                else:
                    # Return None if the world does not exist
                    return None
        except sqlite3.Error as e:
            print(f"An error occurred while fetching the world: {e}")
            return None
    
    def save_score(self, name: str, kills: int, deaths: int):
        """
        Save the kills and deaths for a specific world in the database.

        Args:
            name (str): The name of the world.
            kills (int): The number of kills to save.
            deaths (int): The number of deaths to save.

        Returns:
            bool: True if the score was successfully updated, False otherwise.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Check if the world exists
                cursor.execute('SELECT world_id FROM Worlds WHERE name = ?', (name,))
                world = cursor.fetchone()

                if not world:
                    print(f"World '{name}' does not exist.")
                    return False

                # Update kills and deaths
                cursor.execute('''
                    UPDATE Worlds
                    SET kills = ?, deaths = ?
                    WHERE name = ?;
                ''', (kills, deaths, name))

                conn.commit()
                print(f"Score updated for world '{name}': kills={kills}, deaths={deaths}.")
                return True
        except sqlite3.Error as e:
            print(f"An error occurred while saving the score: {e}")
            return False


WORLD_LOADER = WorldLoader()

# Example usage
if __name__ == "__main__":
    world_loader = WorldLoader()

    # Create the database
    world_loader.create_database()

    # Example: Load blocks in a specific range
    print(world_loader._execute_query(""))
