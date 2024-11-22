import pygame
import json

class AudioLoader:
    """
    AudioLoader handles the loading and management of audio files for the game.

    JSON File Structure:
    ---------------------
    The JSON file should contain a dictionary where:
    - Each key is a unique name for an audio asset (e.g., "BUTTON_HOVER_SOUND").
    - Each value is the file path to the corresponding audio file.

    Example:
    {
        "BUTTON_HOVER_SOUND": "sounds/button_hover.wav",
        "GAME_MUSIC": "music/game_music.mp3",
        "PLAYER_JUMP": "sounds/player_jump.wav",
        "ENEMY_DEATH": "sounds/enemy_death.wav"
    }
    """

    METADATA_PATH = './assets/audio/metadata.json'

    DEFAULT_SOUND_PATH = './assets/audio/sounds/'

    def __init__(self):
        """Initialize the loader and load audio data from the assets metadata JSON file."""
        self.audio_files = {}
        self.load_from_json(self.METADATA_PATH)

    def load_from_json(self, json_path):
        """Load audio files defined in a JSON file."""
        try:
            with open(json_path, 'r') as file:
                audio_data = json.load(file)
                for name, file_path in audio_data.items():
                    self.load_audio(name, file_path)
        except FileNotFoundError:
            print(f"Error: JSON file '{json_path}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file '{json_path}': {e}")

    def load_audio(self, name, file_path):
        """Loads an audio file and associates it with a name."""
        try:
            sound = pygame.mixer.Sound(self.DEFAULT_SOUND_PATH + file_path)
            self.audio_files[name] = sound
        except pygame.error as e:
            print(f"Error loading {file_path}: {e}")

    def get_audio(self, name):
        """Returns the audio object associated with the name."""
        return self.audio_files.get(name, None)
