from .static_element import StaticElement
import json
import commons
import random
from pathlib import Path

class StaticElementMetadataLoader:

    FILENAME = 'static_elements_meta.json'

    def __init__(self):
        """
        Initializes the metadata loader for static elements with a path to the metadata file.
        Metadata is not loaded automatically; it must be loaded explicitly using the `init` method.
        """
        self.metadata_file = Path(commons.METADATA_PATH + self.FILENAME)
        self.metadata = {}
        self._initialized = False  # Tracks if the metadata is loaded.

    def init(self):
        """
        Loads metadata from the JSON file into the class and marks it as initialized.
        """
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"Metadata file '{self.metadata_file}' not found.")

        with open(self.metadata_file, 'r') as file:
            self.metadata = json.load(file)

        self._initialized = True

    def _check_initialized(self):
        """
        Checks if the metadata has been initialized and raises an error if not.
        """
        if not self._initialized:
            raise RuntimeError("StaticElementMetadataLoader is not initialized. Call `init` to load metadata before accessing it.")
    
    def get_property_by_id(self, element_id, property_name):
        """
        Retrieves a specific property of a element based on its ID.

        :param element_id: The ID of the element type.
        :param property_name: The name of the property to retrieve.
        :return: The property value.
        :raises ValueError: If the element ID or property is not found in the metadata.
        """
        self._check_initialized()

        if not isinstance(element_id, str):
            try:
                element_id = str(element_id)
            except ValueError:
                raise ValueError(f"Element ID {element_id} not found in metadata. Wrong type!")

        if element_id not in self.metadata:
            raise ValueError(f"Element ID {element_id} not found in metadata.")
        
        if property_name not in self.metadata[element_id]:
            raise ValueError(f"Property '{property_name}' not found for element ID {element_id}.")
        
        return self.metadata[element_id][property_name]


    def get_name(self, element_id):
        """
        Retrieves the name of a static element based on its ID.

        :param element_id: The ID of the static element type.
        :return: The name of the static element.
        :raises ValueError: If the element ID is not found in the metadata.
        """
        self._check_initialized()

        if element_id not in self.metadata:
            raise ValueError(f"Element ID {element_id} not found in metadata.")
        
        return self.metadata[element_id].get("name", "Unknown")
    
    def get_id_by_name(self, element_name):
        """
        Retrieves the id of a static element based on its name.

        :param element_name: The name of the static element type.
        :return: The name of the static element.
        :raises ValueError: If the element ID is not found in the metadata.
        """
        self._check_initialized()

        for element_id in self.metadata:
            if self.metadata[element_id]['name'] == element_name:
                return element_id
        
        raise ValueError(f"Element ID {element_id} not found in metadata.")
    

    @staticmethod
    def _get_randomized_attribute(attribute):
        """
        Randomizes an attribute if it is a range; otherwise, returns the attribute itself.

        :param attribute: The attribute value or range.
        :return: A randomized value if the attribute is a range, otherwise the original value.
        """
        if isinstance(attribute, list) and len(attribute) == 2:
            return random.randint(attribute[0], attribute[1])
        return attribute

    def create_static_element(self, element_id, position, health=None):
        """
        Creates a new StaticElement instance based on the loaded metadata.

        :param element_id: The ID of the static element type.
        :param position: The position of the element in world coordinates as a Vector2.
        :param health: (Optional) Overrides the default health from the metadata.
        :return: An instance of StaticElement.
        """
        self._check_initialized()

        if isinstance(element_id, int):
            element_id = str(element_id)

        if element_id not in self.metadata:
            raise ValueError(f"Element ID {element_id} not found in metadata.")

        element_data = self.metadata[element_id]
        dimensions = [
            self._get_randomized_attribute(attr)
            for attr in element_data["dimensions"]
        ]
        default_health = self._get_randomized_attribute(element_data["health"])

        return StaticElement(
            element_id=element_id,
            dimensions=dimensions,
            position=position,
            health=health if health is not None else default_health
        )

    def __repr__(self):
        """Returns a string representation of the metadata loader."""
        return f"StaticElementMetadataLoader({self.metadata_file})"


# Global instance of StaticElementMetadataLoader
S_ELEMENT_METADATA_LOADER = StaticElementMetadataLoader()


if __name__ == "__main__":
    # Create a static element (e.g., a tree)

    loader = StaticElementMetadataLoader()

    tree = loader.create_static_element(1, (10, 10)) # Tree

    print(tree)  # Initial state

    # Apply damage
    tree.take_damage(40)
    print(f"After taking damage: {tree}")

    # Check if destroyed
    print(f"Is the tree destroyed? {'Yes' if tree.is_destroyed() else 'No'}")

    # Apply more damage
    tree.take_damage(70)
    print(f"After taking more damage: {tree}")
    print(f"Is the tree destroyed? {'Yes' if tree.is_destroyed() else 'No'}")
