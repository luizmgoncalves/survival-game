import pygame
import json

class ImageLoader:
    """
    Handles loading and management of image files and sprite sheets for the game.

    JSON Structure:
    - "path": Path to the image file.
    - "color_key": [R, G, B] (optional): The color to treat as transparent.
    - "sprite_regions": (optional): A list of dictionaries defining regions in a sprite sheet:
        - "name": The unique name for the sprite.
        - "x", "y", "width", "height": The region's position and size.
    """
    METADATA_PATH = './assets/images/metadata.json'

    DEFAULT_IMAGE_PATH = './assets/images/images/'


    def __init__(self):
        """Initialize the loader and load image data from a JSON file."""
        self.images = {}
        self.load_from_json(self.METADATA_PATH)

    def load_from_json(self, json_path):
        """Load image data and sprite regions defined in a JSON file."""
        try:
            with open(self.DEFAULT_IMAGE_PATH + json_path, 'r') as file:
                data = json.load(file)
                for name, details in data.items():
                    self.load_image(name, details)
        except FileNotFoundError:
            print(f"Error: JSON file '{json_path}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file '{json_path}': {e}")

    def load_image(self, name, details):
        """
        Load an individual image or sprite sheet and handle regions and transparency.
        """
        try:
            image = pygame.image.load(details["path"]).convert_alpha()

            # Apply color key if specified
            if "color_key" in details:
                color_key = tuple(details["color_key"])
                image.set_colorkey(color_key)

            # Store full image if no regions
            if "sprite_regions" not in details:
                self.images[name] = image
            else:
                # Process sprite regions in a sprite sheet
                for region in details["sprite_regions"]:
                    sprite_name = name + "." + region["name"] # Concatenate the sprite name with the region name
                    x, y, width, height = region["x"], region["y"], region["width"], region["height"]
                    sprite = image.subsurface(pygame.Rect(x, y, width, height))
                    self.images[sprite_name] = sprite
        except pygame.error as e:
            print(f"Error loading {details['path']}: {e}")

    def get_image(self, name):
        """Retrieve an image or sprite by name."""
        return self.images.get(name, None)