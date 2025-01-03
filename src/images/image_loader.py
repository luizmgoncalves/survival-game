import pygame
import json
import commons
from pygame.math import Vector2 as v2
from typing import List, Tuple, Dict
import os
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
        self.images: Dict[str, Tuple[pygame.Surface, dict]] = {}
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

            self.images[name] = image, {}
            self.masks.append(name)

    def load_from_json(self, json_path):
        """Load image data and sprite regions defined in a JSON file."""

        self.load_masks()

        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
                for name, details in data.items():
                    if "#" in name:
                        self.load_bunch_of_images(name, details)
                        continue
                    self.load_image(name, details)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: JSON file '{json_path}' not found.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON file '{json_path}': {e}")

        self.generate_masked_blocks()
        #pprint.pprint(self.images)
    
    def load_bunch_of_images(self, name: str, details: dict):
        assert details['path'].count("#") == name.count("#"), "Different # number in name and path counting"

        index = 0
        

        while True:
            new_name = name.replace("#", str(index), 1)
            new_path = details["path"].replace("#", str(index), 1)

            if "#" in new_path:
                new_details = details.copy()
                new_details['path'] = new_path
                self.load_bunch_of_images(new_name, new_details)
            elif os.path.exists(commons.DEFAULT_IMAGES_PATH + new_path):
                new_details = details.copy()
                new_details['path'] = new_path
                self.load_image(new_name, new_details)
            else:
                break
                
            
            

            index += 1
            
    
    def generate_masked_blocks(self):
        for block_name in self.blocks:
            for mask_name in self.masks:
                # Mask default names: MASK_####
                # Example: MASK_0011
                edge = mask_name.split("_")[1] # Get the number of the mask
                surf = pygame.Surface((commons.BLOCK_SIZE, commons.BLOCK_SIZE)).convert()

                surf.blit(self.images[block_name][0], (0, 0))

                surf.blit(self.images[mask_name][0], (0, 0))
                
                surf.set_colorkey(commons.BLOCK_MASK_COLOR)

                self.images[f"{block_name}.{edge}"] = surf, self.images[block_name][1]

                back_block = self.images[block_name][0].copy()
                back_block.set_alpha(commons.BACK_LAYER_TRANSPARENCY)
                back_block_ = pygame.Surface((commons.BLOCK_SIZE, commons.BLOCK_SIZE)).convert()
                back_block_.fill((0, 0, 0))
                back_block_.blit(back_block, (0, 0))
                back_block_.blit(self.images[mask_name][0], (0, 0))

                self.images[f"BACK_{block_name}.{edge}"] = back_block_, self.images[block_name][1]
            
            self.images[f'{block_name}.1111'] = self.images[block_name]

            self.images[f'{block_name}.1111'][0].set_colorkey(commons.BLOCK_MASK_COLOR)

            back_block = self.images[block_name][0].copy()
            back_block.set_alpha(commons.BACK_LAYER_TRANSPARENCY)
            back_block_ = pygame.Surface((commons.BLOCK_SIZE, commons.BLOCK_SIZE)).convert()
            back_block_.fill((0, 0, 0))
            back_block_.blit(back_block, (0, 0))
            self.images[f"BACK_{block_name}.1111"] = back_block_, self.images[block_name][1]

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
            
            if "block_size" in details:
                size = v2(commons.BLOCK_SIZE, commons.BLOCK_SIZE)
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
                self.images[name] = (image, details)

                if "flipx" in details:
                    self.flip_image(name, x=True)
                
                if "flipy" in details:
                    self.flip_image(name, y=True)

                if "flipxy" in details:
                    self.flip_image(name, x=True, y=True)
            else:
                # Process sprite regions in a sprite sheet
                for sprite_c_name in details["sprite_regions"]:
                    region = details["sprite_regions"][sprite_c_name]
                    sprite_name = name + "." + sprite_c_name  # Concatenate the sprite name with the region name
                    x, y, width, height = region["x"], region["y"], region["width"], region["height"]
                    sprite = image.subsurface(pygame.Rect(x, y, width, height))

                    csize = v2(sprite.get_size())

                    if "scaled_size" in details:
                        size = v2(details["scaled_size"])
                        sprite = pygame.transform.scale_by(sprite, (size.x / csize.x, size.y / csize.y) )
                    
                    if "scaled_size" in region:
                        size = v2(region["scaled_size"])
                        sprite = pygame.transform.scale_by(sprite, (size.x / csize.x, size.y / csize.y) )

                    self.images[sprite_name] = (sprite, region)
                    
                    if "flipx" in details:
                        self.flip_image(sprite_name, x=True)
                    
                    if "flipy" in details:
                        self.flip_image(sprite_name, y=True)

                    if "flipxy" in details:
                        self.flip_image(sprite_name, x=True, y=True)

                    
                    
        except pygame.error as e:
            raise pygame.error(f"Error loading {details['path']}: {e}")

    def get_image(self, name):
        """Retrieve an image or sprite by name."""
        if not self._initialized:
            raise RuntimeError("ImageLoader is not initialized! Call 'init()' before using it.")
        
        if image_det := self.images.get(name, None):
            return image_det[0]
        else:
            raise KeyError(f"Image '{name}' not found in the ImageLoader!")

    def flip_image(self, image_name: str, x=False, y=False) -> str:
        """Flip an image and return its name.

        :param image_name: The name of the image to flip.
        :param x: Whether to flip horizontally.
        :param y: Whether to flip vertically.
        :return: The name of the flipped image.
        :raises RuntimeError: If the ImageLoader is not initialized.
        :raises ValueError: If the flipped image already exists.
        """
        if image_det := self.images.get(image_name, None):
            if not x and not y:
                raise ValueError(f"Trying to flip without setting x or y axis")
            image = image_det[0]

            if x and not y:
                flipped_x_name = f'{image_name}.FLIPED_X'
                if flipped_x_name in self.images:
                    raise ValueError(f"Flipped image '{flipped_x_name}' already exists!")
                imagex = pygame.transform.flip(image, True, False)
                self.images[flipped_x_name] = (imagex, image_det[1])
                return flipped_x_name

            if y and not x:
                flipped_y_name = f'{image_name}.FLIPED_Y'
                if flipped_y_name in self.images:
                    raise ValueError(f"Flipped image '{flipped_y_name}' already exists!")
                imagey = pygame.transform.flip(image, False, True)
                self.images[flipped_y_name] = (imagey, image_det[1])
                return flipped_y_name

            if x and y:
                flipped_xy_name = f'{image_name}.FLIPED_XY'
                if flipped_xy_name in self.images:
                    raise ValueError(f"Flipped image '{flipped_xy_name}' already exists!")
                imagexy = pygame.transform.flip(image, True, True)
                self.images[flipped_xy_name] = (imagexy, image_det[1])

                return flipped_xy_name

        else:
            raise KeyError(f"Image '{image_name}' not found in the ImageLoader!")


    def get_image_atribute(self, name, atribute):
        """Retrieve an image or sprite by name."""
        if not self._initialized:
            raise RuntimeError("ImageLoader is not initialized! Call 'init()' before using it.")
        
        if details := self.images.get(name)[-1]:
            return details.get(atribute, None)
        else:
            raise KeyError(f"Image '{name}' not found in the ImageLoader!")

# Initialize the loader in the main program or entry point
IMAGE_LOADER = ImageLoader()
