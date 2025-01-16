import pygame
from pygame.math import Vector2 as v2

# Constants and event types shared across multiple modules

WIDTH, HEIGHT = 1920, 1080

IWIDTH, IHEIGHT = 1920, 1080

CHUNK_SIZE = 31
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

# Custom event for item collecting
# Triggered when a block is getted by the player
# Has the item id atributes
ITEM_COLLECT_EVENT = pygame.event.custom_type()

# Custom event for static element breaking
# Triggered when a element is broke
# Has no atributes
S_ELEMENT_BROKEN = pygame.event.custom_type()

RENDER_MANAGER_INIT = pygame.event.custom_type()


THROWING = pygame.event.custom_type()

# Metadata files path
METADATA_PATH = './assets/metadata/'

#Images  path
DEFAULT_IMAGES_PATH = './assets/images/'

#Database path
DEFAULT_DB_PATH = './assets/database/'

#Audio files path
DEFAULT_SOUND_PATH = './assets/audio/'

PLAYER_SIZE = (30, 50)        # Default size
PLAYER_LIFE = 500             # Default life points
PLAYER_MAX_VEL = 900          # Default maximum velocity

PLAYER_ATTACK_DAMAGE = 40

GRAVITY_ACELERATION = 40

TERMINAL_SPEED = 1500

WORLD_SELECTED = '' # World selected on Worlds page to being played

BLOCK_MASK_COLOR = (255, 0, 255)
MASK_DEFAULT_PATH = 'assets/images/block_masks/'


BACK_LAYER_TRANSPARENCY = 100 # Rule the back layer filtering (max: 255)

BLOCK_RECUPERATION_PERCENTAGE = 5

ITEM_INITIAL_VELOCITY = 600

ITEM_SIZE = BLOCK_SIZE * 0.5

BREAKING_STAGES_NUMBER = 3

ITEM_ATTRACTION_FORCE = 100

INVULNERABILITY_DURATION = 0.1

PLAYER_INVULNERABILITY_DURATION = 0.5

MAX_DISTANCE_OF_ITEM_ATTRACTION = 200 # in pixels

DEFAULT_JUMP_STRENGHT = 500

DEFAULT_WALKING_VEL = 500


DEFAULT_START_PLAYER_POSITION = pygame.math.Vector2(100, -100)

CURRENT_POSITION = pygame.math.Vector2(0, 0)


INVENTORY_POS = lambda : v2(pygame.display.get_window_size()[0]/2, pygame.display.get_window_size()[1]-200)


DESPAWN_DISTANCE = 10_000

BULLET_INITIAL_VELOCITY = 1000

DAY_DURATION = 120 # Duração dos dias em segundos

TIME_TO_LIFE_RECUPERATION = 2

LIFE_RECUPERATION_RATE = 10

DIFFICULTY_MODES = ['EASY', 'MEDIUM', 'HARD']

CURRENT_DIFFICULTY_MODE = 'MEDIUM'

ENEMY_SPAWN_RATE = {'EASY': 5, 'MEDIUM': 3, 'HARD': 1}

MAX_ENEMIES = {'EASY': 10, 'MEDIUM': 20, 'HARD': 30}