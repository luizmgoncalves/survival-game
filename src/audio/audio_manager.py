import pygame
from .audio_loader import AudioLoader

class AudioManager:
    """
    Manages audio playback, volumes, muting, and tracking currently playing music.
    """

    def __init__(self):
        """
        Initialize the AudioManager.
        :param loader: An instance of AudioLoader.
        """
        self.loader = AudioLoader()
        self.master_volume = 1.0  # Range: 0.0 to 1.0
        self.effects_volume = 0.4  # Range: 0.0 to 1.0
        self.music_volume = 1.0  # Range: 0.0 to 1.0
        self.muted = False
        self.current_playing = None  # Name of the currently playing music

    def play_sound(self, name):
        """Play a sound effect by name."""
        if self.muted:
            return
        sound = self.loader.get_audio(name)
        if sound:
            sound.set_volume(self.master_volume * self.effects_volume)
            sound.play()
        else:
            print(f"Sound '{name}' not found.")

    def play_music(self, name, loop=False):
        """Play music by name, stopping any previously playing music."""
        if self.muted:
            return
        sound = self.loader.get_audio(name)
        if sound:
            # Stop current music if playing
            if self.current_playing:
                self.stop_music()
            self.current_playing = name
            sound.set_volume(self.master_volume * self.music_volume)
            sound.play(-1 if loop else 0)
        else:
            print(f"Music '{name}' not found.")

    def stop_music(self):
        """Stop the currently playing music."""
        if self.current_playing:
            sound = self.loader.get_audio(self.current_playing)
            if sound:
                sound.stop()
            self.current_playing = None

    def set_master_volume(self, volume):
        """Set the master volume."""
        self.master_volume = max(0.0, min(volume, 1.0))
        self._update_volumes()

    def set_effects_volume(self, volume):
        """Set the effects volume."""
        self.effects_volume = max(0.0, min(volume, 1.0))

    def set_music_volume(self, volume):
        """Set the music volume."""
        self.music_volume = max(0.0, min(volume, 1.0))
        if self.current_playing:
            sound = self.loader.get_audio(self.current_playing)
            if sound:
                sound.set_volume(self.master_volume * self.music_volume)

    def mute(self):
        """Mute all audio playback (both effects and music)."""
        if not self.muted:
            self.muted = True
            pygame.mixer.stop()  # Stop all sounds immediately when muting.

    def unmute(self):
        """Unmute all audio and restore playback."""
        if self.muted:
            self.muted = False
            # Restart the currently playing music if unmuting
            if self.current_playing:
                self.play_music(self.current_playing)

    def _update_volumes(self):
        """Update the volumes of currently playing music and effects."""
        if self.current_playing:
            sound = self.loader.get_audio(self.current_playing)
            if sound:
                sound.set_volume(self.master_volume * self.music_volume)

pygame.mixer.init()

AUDIO_MANAGER = AudioManager()