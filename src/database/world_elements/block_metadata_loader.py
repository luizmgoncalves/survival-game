import json
from pathlib import Path
import commons

class BlockMetadataLoader:

    FILENAME = 'block_metadata.json'

    def __init__(self):
        """
        Initializes the BlockMetadataLoader with a path to the metadata file.
        Metadata is not loaded automatically; it must be loaded explicitly using the `init` method.

        :param metadata_file: Path to the JSON file containing block metadata.
        """
        self.metadata_file = Path(commons.METADATA_PATH + self.FILENAME)
        self.metadata = {}
        self._initialized = False  # Attribute to track if the metadata is loaded.

    def init(self):
        """
        Loads metadata from the JSON file into the class.
        """
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"Metadata file '{self.metadata_file}' not found.")

        with open(self.metadata_file, 'r') as file:
            self.metadata = json.load(file)

        self._initialized = True  # Mark as initialized.

    def _check_initialized(self):
        """
        Verifies if the metadata was loaded. Raises an error if not.
        """
        if not self._initialized:
            raise RuntimeError("BlockMetadataLoader is not initialized. Call `init` to load metadata before accessing it.")

    def get_name_by_id(self, block_id):
        """
        Retrieves the name of a block based on its ID.

        :param block_id: The ID of the block type.
        :return: The name of the block.
        :raises ValueError: If the block ID is not found in the metadata.
        """
        self._check_initialized()

        if block_id not in self.metadata:
            raise ValueError(f"Block ID {block_id} not found in metadata.")
        
        return self.metadata[block_id].get("name", "Unknown")

    def get_property_by_id(self, block_id, property_name):
        """
        Retrieves a specific property of a block based on its ID.

        :param block_id: The ID of the block type.
        :param property_name: The name of the property to retrieve.
        :return: The property value.
        :raises ValueError: If the block ID or property is not found in the metadata.
        """
        self._check_initialized()

        if block_id not in self.metadata:
            raise ValueError(f"Block ID {block_id} not found in metadata.")
        
        if property_name not in self.metadata[block_id]:
            raise ValueError(f"Property '{property_name}' not found for Block ID {block_id}.")
        
        return self.metadata[block_id][property_name]

    def get_id_by_name(self, block_name):
        """
        Retrieves the ID of a block based on its name.

        :param block_name: The name of the block type.
        :return: The ID of the block.
        :raises ValueError: If the block name is not found in the metadata.
        """
        self._check_initialized()

        for block_id, block_data in self.metadata.items():
            if block_data.get("name") == block_name:
                return block_id

        raise ValueError(f"Block name '{block_name}' not found in metadata.")

    def __repr__(self):
        """Returns a string representation of the metadata loader."""
        return f"BlockMetadataLoader({self.metadata_file})"


BLOCK_METADATA = BlockMetadataLoader()