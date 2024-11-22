import sqlite3
import os

class WorldLoader:
    DEFAULT_DB_PATH = './assets/database/'

    def __init__(self, db_name='game.db'):
        """Initialize the WorldLoader with the database name."""
        self.db_name = self.DEFAULT_DB_PATH + db_name
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

            # Create Worlds table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Worlds (
                    world_id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    size_x INTEGER,
                    size_y INTEGER
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
                    FOREIGN KEY(world_id) REFERENCES Worlds(world_id)
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
                    FOREIGN KEY(world_id) REFERENCES Worlds(world_id)
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
                    FOREIGN KEY(world_id) REFERENCES Worlds(world_id)
                );
            ''')

            print("Database and tables created successfully.")


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
    
    def get_worlds_names(self):
        """Retrieve the world ID for a given world name."""
        query = "SELECT * FROM Worlds"
        result = self._execute_query(query, [])
        return result

WORLD_LOADER = WorldLoader()

# Example usage
if __name__ == "__main__":
    world_loader = WorldLoader()

    # Create the database
    world_loader.create_database()

    # Example: Load blocks in a specific range
    print(world_loader._execute_query(""))
