import json
from pathlib import Path
import commons

class ItemMetadataLoader:
    FILENAME = 'item_metadata.json'

    def __init__(self):
        """
        Initializes the ItemMetadataLoader with a path to the metadata file.
        Metadata is not loaded automatically; it must be loaded explicitly using the `init` method.
        """
        self.metadata_file = Path(commons.METADATA_PATH + self.FILENAME)
        self.metadata = {}
        self._initialized = False

    def init(self):
        """
        Loads metadata from the JSON file into the class.
        """
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"Metadata file '{self.metadata_file}' not found.")

        with open(self.metadata_file, 'r') as file:
            self.metadata = json.load(file)

        self._initialized = True

    def _check_initialized(self):
        """
        Verifies if the metadata was loaded. Raises an error if not.
        """
        if not self._initialized:
            raise RuntimeError("ItemMetadataLoader is not initialized. Call `init` to load metadata before accessing it.")

    def get_name_by_id(self, item_id):
        """
        Retrieves the name of an item based on its ID.

        :param item_id: The ID of the item.
        :return: The name of the item.
        :raises ValueError: If the item ID is not found in the metadata.
        """
        self._check_initialized()

        if item_id not in self.metadata:
            raise ValueError(f"Item ID '{item_id}' not found in metadata.")

        return self.metadata[item_id].get("name", "Unknown")

    def get_property_by_id(self, item_id, property_name):
        """
        Retrieves a specific property of an item based on its ID.

        :param item_id: The ID of the item.
        :param property_name: The name of the property to retrieve.
        :return: The property value.
        :raises ValueError: If the item ID or property is not found in the metadata.
        """
        self._check_initialized()

        if item_id not in self.metadata:
            raise ValueError(f"Item ID '{item_id}' not found in metadata.")

        if property_name not in self.metadata[item_id]:
            raise ValueError(f"Property '{property_name}' not found for Item ID '{item_id}'.")

        return self.metadata[item_id][property_name]

    def get_id_by_name(self, item_name):
        """
        Retrieves the ID of an item based on its name.

        :param item_name: The name of the item.
        :return: The ID of the item.
        :raises ValueError: If the item name is not found in the metadata.
        """
        self._check_initialized()

        for item_id, item_data in self.metadata.items():
            if item_data.get("name") == item_name:
                return item_id

        raise ValueError(f"Item name '{item_name}' not found in metadata.")

    def __repr__(self):
        """Returns a string representation of the metadata loader."""
        return f"ItemMetadataLoader({self.metadata_file})"


ITEM_METADATA = ItemMetadataLoader()
