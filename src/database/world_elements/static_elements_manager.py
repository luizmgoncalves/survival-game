from .static_element import StaticElement
import json
import random
from pathlib import Path

class StaticElementMetadataLoader:

    DEFAULT_PATH = './assets/elements_metadata/static_elements_meta.json'

    def __init__(self):
        """
        Loads metadata about static elements from a JSON file.

        :param metadata_file: Path to the JSON file containing static element metadata.
        """
        self.metadata_file = Path(self.DEFAULT_PATH)
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
    
    def get_name(self, element_id):
        """
        Retrieves the name of a static element based on its ID.

        :param element_id: The ID of the static element type.
        :return: The name of the static element.
        :raises ValueError: If the element ID is not found in the metadata.
        """
        if element_id not in self.metadata:
            raise ValueError(f"Element ID {element_id} not found in metadata.")
        
        return self.metadata[element_id].get("name", "Unknown")
    

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
            name=self.get_name(element_id),
            element_id=element_id,
            dimensions=dimensions,
            position=position,
            health=health if health is not None else default_health
        )

    def __repr__(self):
        """Returns a string representation of the metadata loader."""
        return f"StaticElementMetadataLoader({self.metadata_file})"


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
