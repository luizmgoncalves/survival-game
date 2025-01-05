import sqlite3
import os
import commons
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

            # Create Worlds table without size_x and size_y
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Worlds (
                    world_id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    score INTEGER DEFAULT 0
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
                    item_count INTEGER NOT NULL CHECK(item_count >= 0),
                    PRIMARY KEY (world_id, slot),
                    FOREIGN KEY (world_id) REFERENCES Worlds(world_id) ON DELETE CASCADE
                );
            ''')

            # Create StaticObjects table with health column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS StaticObjects (
                    object_id INTEGER PRIMARY KEY,
                    world_id INTEGER,
                    x INTEGER,
                    y INTEGER,
                    type TEXT,
                    width INTEGER DEFAULT 1,
                    height INTEGER DEFAULT 1,
                    health INTEGER DEFAULT 100,
                    state TEXT DEFAULT 'active',
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
                    block_id INTEGER PRIMARY KEY,
                    world_id INTEGER,
                    x INTEGER,
                    y INTEGER,
                    layer INTEGER,
                    type TEXT,
                    FOREIGN KEY(world_id) REFERENCES Worlds(world_id) ON DELETE CASCADE
                );
            ''')

            print("Database and tables created successfully.")
    
    def create_world(self, name, score=0):
        """
        Create a new world with the given name and optional score.
        
        Args:
            name (str): The name of the world.
            score (int): The initial score of the world (default is 0).
        
        Raises:
            ValueError: If a world with the same name already exists.
        """
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
                    INSERT INTO Worlds (name, score)
                    VALUES (?, ?);
                ''', (name, score))

                print(f"World '{name}' created successfully with score {score}.")
                return True
        except sqlite3.Error as e:
            print(f"An error occurred while creating the world: {e}")
            return False
    
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
    
    def load_inventory(self, world_id):
        """
        Load the inventory for a specific world.

        :param world_id: The ID of the world whose inventory is to be loaded.
        :return: An Inventory object populated with the data from the database.
        """
        inventory = Inventory()

        query = """
        SELECT slot, item_count FROM Inventory WHERE world_id = ?
        """
        params = (world_id,)

        try:
            # Retrieve inventory data from the database
            inventory_data = self._execute_query(query, params)

            # Add each item to the Inventory object
            for slot, item_count in inventory_data:
                if not inventory.add_item(slot, item_count):
                    print(f"Failed to add item in slot {slot} with count {item_count}")
        except sqlite3.Error as e:
            print(f"An error occurred while loading inventory: {e}")

        return inventory


    def _execute_query(self, query, params):
        """Helper method to execute a query and fetch results."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def load_blocks(self, world_id, x_min=None, x_max=None, y_min=None, y_max=None, layer=None):
        """Load blocks for a specific world, optionally filtered by position and layer."""
        query = """
        SELECT * FROM Blocks WHERE world_id = ?
        """
        params = [world_id]

        if x_min is not None and x_max is not None:
            query += " AND x BETWEEN ? AND ?"
            params.extend([x_min, x_max])
        if y_min is not None and y_max is not None:
            query += " AND y BETWEEN ? AND ?"
            params.extend([y_min, y_max])
        if layer is not None:
            query += " AND layer = ?"
            params.append(layer)

        return self._execute_query(query, tuple(params))

    def load_static_objects(self, world_id, object_type=None, x_min=None, x_max=None, y_min=None, y_max=None):
        """Load static objects for a specific world, optionally filtered by type, position, and health."""
        query = "SELECT * FROM StaticObjects WHERE world_id = ?"
        params = [world_id]

        if object_type is not None:
            query += " AND type = ?"
            params.append(object_type)
        if x_min is not None and x_max is not None:
            query += " AND x BETWEEN ? AND ?"
            params.extend([x_min, x_max])
        if y_min is not None and y_max is not None:
            query += " AND y BETWEEN ? AND ?"
            params.extend([y_min, y_max])

        return self._execute_query(query, tuple(params))



    def load_moving_entities(self, world_id, entity_type=None, x_min=None, x_max=None, y_min=None, y_max=None):
        """Load moving entities for a specific world, optionally filtered by type, health, and position."""
        query = "SELECT * FROM MovingEntities WHERE world_id = ?"
        params = [world_id]

        if entity_type is not None:
            query += " AND type = ?"
            params.append(entity_type)
        if x_min is not None and x_max is not None:
            query += " AND x BETWEEN ? AND ?"
            params.extend([x_min, x_max])
        if y_min is not None and y_max is not None:
            query += " AND y BETWEEN ? AND ?"
            params.extend([y_min, y_max])

        return self._execute_query(query, tuple(params))


    def get_world_id_by_name(self, name):
        """Retrieve the world ID for a given world name."""
        query = "SELECT world_id FROM Worlds WHERE name = ?"
        result = self._execute_query(query, (name,))
        return result[0][0] if result else None

    def get_worlds(self) -> List[Dict[str, Any]]:
        """
        Retrieve a list of all worlds already created.

        Returns:
            list: A list of dictionaries, where each dictionary represents a world
                with keys 'world_id', 'name', and 'score'.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Query all worlds from the Worlds table
                cursor.execute('SELECT world_id, name, score FROM Worlds')
                rows = cursor.fetchall()

                # Convert the result to a list of dictionaries
                worlds = [{'world_id': row[0], 'name': row[1], 'score': row[2]} for row in rows]

                return worlds
        except sqlite3.Error as e:
            print(f"An error occurred while fetching the worlds: {e}")
            return []
        
    def get_world(self, name: str):
        """
        Retrieve a specific world by its name.

        Args:
            name (str): The name of the world to retrieve.

        Returns:
            dict or None: A dictionary representing the world with keys 'world_id',
                        'name', and 'score' if found; None if the world does not exist.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Query the world from the Worlds table
                cursor.execute('SELECT world_id, name, score FROM Worlds WHERE name = ?', (name,))
                row = cursor.fetchone()

                if row:
                    # Return the world as a dictionary
                    return {'world_id': row[0], 'name': row[1], 'score': row[2]}
                else:
                    # Return None if the world does not exist
                    return None
        except sqlite3.Error as e:
            print(f"An error occurred while fetching the world: {e}")
            return None

WORLD_LOADER = WorldLoader()

# Example usage
if __name__ == "__main__":
    world_loader = WorldLoader()

    # Create the database
    world_loader.create_database()

    # Example: Load blocks in a specific range
    print(world_loader._execute_query(""))
