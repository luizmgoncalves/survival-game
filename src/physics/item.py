from .moving_element import CollidableMovingElement
from images.image_loader import IMAGE_LOADER
from database.world_elements.item_metadata import ITEM_METADATA
from typing import Tuple
import commons

class Item(CollidableMovingElement):
    def __init__(self, item_id, position: Tuple[int, int], velocity):
        self.id = item_id
        size = (commons.ITEM_SIZE, commons.ITEM_SIZE)
        super().__init__(position, size, velocity)

        self.image = ITEM_METADATA.get_property_by_id(item_id, 'image_name')