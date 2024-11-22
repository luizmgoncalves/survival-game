import json
from pathlib import Path

class BlockMetadataLoader:
    def __init__(self, metadata_file):
        """
        Loads metadata about blocks from a JSON file.

        :param metadata_file: Path to the JSON file containing block metadata.
        """
        self.metadata_file = Path(metadata_file)
        self.metadata = {}

        self._load_metadata()

    def _load_metadata(self):
        """
        Loads metadata from the JSON file into the class.
        """
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"Metadata file '{self.metadata_file}' not found.")

        with open(self.metadata_file, 'r') as file:
            self.metadata = json.load(file)

    def get_name_by_id(self, block_id):
        """
        Retrieves the name of a block based on its ID.

        :param block_id: The ID of the block type.
        :return: The name of the block.
        :raises ValueError: If the block ID is not found in the metadata.
        """
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
        if block_id not in self.metadata:
            raise ValueError(f"Block ID {block_id} not found in metadata.")
        
        if property_name not in self.metadata[block_id]:
            raise ValueError(f"Property '{property_name}' not found for Block ID {block_id}.")
        
        return self.metadata[block_id][property_name]

    def __repr__(self):
        """Returns a string representation of the metadata loader."""
        return f"BlockMetadataLoader({self.metadata_file})"
