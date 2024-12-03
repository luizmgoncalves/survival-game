import pygame

# Constants and event types shared across multiple modules

WIDTH, HEIGHT = 1920, 1080

CHUNK_SIZE = 40
BLOCK_SIZE = 32

CHUNK_SIZE_PIXELS = CHUNK_SIZE * BLOCK_SIZE

# Custom event type for handling page changes.
# This event can be used to trigger page transitions in the game.
# The event's dictionary contains the 'page' attribute, which specifies 
# the target page to transition to.
CHANGE_PAGE_EVENT = pygame.event.custom_type()


# Custom event for item dropping
# Triggered when a block is broke or if the player drop
# Has the position and the item id atributes
ITEM_DROP_EVENT = pygame.event.custom_type()

# Metadata files path
METADATA_PATH = './assets/metadata/'

#Images  path
DEFAULT_IMAGES_PATH = './assets/images/'

#Database path
DEFAULT_DB_PATH = './assets/database/'

#Audio files path
DEFAULT_SOUND_PATH = './assets/audio/'

PLAYER_START_POSITION = (100, 100)  # Starting position
PLAYER_SIZE = (50, 50)        # Default size
PLAYER_LIFE = 100             # Default life points
PLAYER_MAX_VEL = 200          # Default maximum velocity

GRAVITY_ACELERATION = 40

WORLD_SELECTED = '' # World selected on Worlds page to being played

BLOCK_MASK_COLOR = (255, 0, 255)
MASK_DEFAULT_PATH = 'assets/images/block_masks/'

BACK_LAYER_TRANSPARENCY = 100 # Rule the back layer filtering (max: 255)

BLOCK_RECUPERATION_PERCENTAGE = 0.009