import pygame

# Constants and event types shared across multiple modules

WIDTH, HEIGHT = 1920, 1080

# Custom event type for handling page changes.
# This event can be used to trigger page transitions in the game.
# The event's dictionary contains the 'page' attribute, which specifies 
# the target page to transition to.
CHANGE_PAGE_EVENT = pygame.event.custom_type()


# Metadata files path
METADATA_PATH = './assets/metadata/'

#Images  path
DEFAULT_IMAGES_PATH = './assets/images/'

#Database path
DEFAULT_DB_PATH = './assets/database/'

#Audio files path
DEFAULT_SOUND_PATH = './assets/audio/'