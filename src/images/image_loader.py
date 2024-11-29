import pygame
import json
import commons
from pygame.math import Vector2 as v2
from typing import List
import pprint

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
    FILENAME = 'images_metadata.json'

    def __init__(self):
        """Initialize the loader, but leave images uninitialized until explicitly set."""
        self.images = {}
        self.blocks: List[str] = []
        self.masks: List[str] = []
        self._initialized = False  # Track if the loader has been initialized

    def init(self):
        """Initialize the loader by loading data from the JSON file."""
        if self._initialized:
            raise RuntimeError("ImageLoader is already initialized!")
        self.load_from_json(commons.METADATA_PATH + self.FILENAME)
        self._initialized = True  # Mark as initialized
    
    def load_masks(self):
        masks = [f"{i:04b}" for i in range(15)] # Generate all mask names from "0000" to "1111"

        for mask in masks:
            name = f"MASK_{mask}"

            image = pygame.image.load(f"{commons.MASK_DEFAULT_PATH}{mask}.png").convert_alpha()
            csize = v2(image.get_size())

            size = v2(commons.BLOCK_SIZE, commons.BLOCK_SIZE)
            image = pygame.transform.scale_by(image, (size.x / csize.x, size.y / csize.y) )

            #color_key = commons.BLOCK_MASK_COLOR_KEY
            #image.set_colorkey(color_key)

            self.images[name] = image
            self.masks.append(name)

    def load_from_json(self, json_path):
        """Load image data and sprite regions defined in a JSON file."""

        self.load_masks()

        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
                for name, details in data.items():
                    self.load_image(name, details)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: JSON file '{json_path}' not found.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON file '{json_path}': {e}")

        self.generate_masked_blocks()
        pprint.pprint(self.images)
    
    def generate_masked_blocks(self):
        for block_name in self.blocks:
            for mask_name in self.masks:
                # Mask default names: MASK_####
                # Example: MASK_0011
                edge = mask_name.split("_")[1] # Get the number of the mask
                surf = pygame.Surface((commons.BLOCK_SIZE, commons.BLOCK_SIZE)).convert()

                surf.blit(self.images[block_name], (0, 0))
                surf.blit(self.images[mask_name], (0, 0))
                
                surf.set_colorkey(commons.BLOCK_MASK_COLOR)

                self.images[f"{block_name}.{edge}"] = surf
            
            self.images[f'{block_name}.1111'] = self.images[block_name]

    def load_image(self, name, details):
        """
        Load an individual image or sprite sheet and handle regions and transparency.
        """
        try:
            image = pygame.image.load(commons.DEFAULT_IMAGES_PATH + details["path"]).convert()
            csize = v2(image.get_size())

            if "scaled_size" in details:
                size = v2(details["scaled_size"])
                image = pygame.transform.scale_by(image, (size.x / csize.x, size.y / csize.y) )
            
            if "block" in details:
                size = v2(commons.BLOCK_SIZE, commons.BLOCK_SIZE)
                image = pygame.transform.scale_by(image, (size.x / csize.x, size.y / csize.y) )
                self.blocks.append(name)

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
                    sprite_name = name + "." + region["name"]  # Concatenate the sprite name with the region name
                    x, y, width, height = region["x"], region["y"], region["width"], region["height"]
                    sprite = image.subsurface(pygame.Rect(x, y, width, height))

                    csize = v2(sprite.get_size())

                    if "scaled_size" in region:
                        size = v2(region["scaled_size"])
                        sprite = pygame.transform.scale_by(sprite, (size.x / csize.x, size.y / csize.y) )

                    self.images[sprite_name] = sprite
                    
        except pygame.error as e:
            raise pygame.error(f"Error loading {details['path']}: {e}")

    def get_image(self, name):
        """Retrieve an image or sprite by name."""
        if not self._initialized:
            raise RuntimeError("ImageLoader is not initialized! Call 'init()' before using it.")
        return self.images.get(name, None)

# Initialize the loader in the main program or entry point
IMAGE_LOADER = ImageLoader()
