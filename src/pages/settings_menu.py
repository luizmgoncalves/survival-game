from pygame.sprite import LayeredUpdates
from gui.button import Button
from gui.label import Label
from .page import Page
import pygame
import commons
import images.image_loader as image_loader
from audio.audio_manager import AUDIO_MANAGER

class SettingsPage(Page):
    def __init__(self):
        """
        Initialize the Settings page with a background image, labels, buttons for volume, mute, difficulty, and back.
        """
        super().__init__()
        
        self.showing = False
        self.current_selected_option = 0  # Index to track selected option
        
        # Load and scale the background image
        self._bg_image = image_loader.IMAGE_LOADER.get_image("WALLPAPER")
        self.bg_image = self._bg_image

        # Labels and buttons for settings options
        self.labels = [Label("Settings", commons.IWIDTH / 2, 100)]
        self.buttons = [
            Button("Master Volume", commons.IWIDTH / 2, 250, width=400, height=80, font_size=60),
            Button("Music Volume", commons.IWIDTH / 2, 350, width=400, height=80, font_size=60),
            Button("Sound Effects Volume", commons.IWIDTH / 2, 450, width=440, height=80, font_size=60),
            Button("Mute", commons.IWIDTH / 2, 550, width=200, height=80, font_size=60, on_click=self.toggle_mute),
            Button("Difficulty", commons.IWIDTH / 2, 650, width=300, height=80, font_size=60, on_click=self.change_difficulty),
            Button("Back", commons.IWIDTH / 2, 750, width=200, height=80, font_size=60, on_click=self.go_back)
        ]

        # Dynamic labels for displaying current states
        self.state_labels = [
            Label(f"{AUDIO_MANAGER.master_volume*100:.0f}%", commons.IWIDTH / 2 + 300, 250, font_size=40),
            Label(f"{AUDIO_MANAGER.music_volume*100:.0f}%", commons.IWIDTH / 2 + 300, 350, font_size=40),
            Label(f"{AUDIO_MANAGER.effects_volume*100:.0f}%", commons.IWIDTH / 2 + 300, 450, font_size=40),
            Label("Muted" if AUDIO_MANAGER.muted else "Unmuted", commons.IWIDTH / 2 + 300, 550, font_size=40),
            Label(commons.CURRENT_DIFFICULTY_MODE, commons.IWIDTH / 2 + 300, 650, font_size=40)
        ]
        
        # Set up elements for canvas and highlight selected option
        self.elements = self.labels + self.buttons + self.state_labels

        self.canvas = LayeredUpdates(self.elements)
        
        # Resize elements to initial screen size
        self.resize(pygame.display.get_window_size())
    
    def reset(self, **kwargs):
        self.unselect_all()
    
    def unselect_all(self):
        """
        Unhighlight all buttons.
        """
        for i, button in enumerate(self.buttons):
            if i == self.current_selected_option:
                button.unselect()  # Custom method to visually deselect a button

    def highlight_selected(self):
        """
        Highlight the currently selected button.
        """
        for i, button in enumerate(self.buttons):
            if i == self.current_selected_option:
                button.select()  # Custom method to visually select a button
            else:
                button.unselect()  # Custom method to visually deselect a button

    def adjust_master_volume(self, delta=0.0):
        """Adjust the master volume."""
        if delta != 0.0:
            new_volume = min(max(AUDIO_MANAGER.master_volume + delta, 0.0), 1.0)
            AUDIO_MANAGER.set_master_volume(new_volume)
            AUDIO_MANAGER.play_sound("BUBBLE")
            self.update_labels()
            

    def adjust_music_volume(self, delta=0.0):
        """Adjust the music volume."""
        if delta != 0.0:
            new_volume = min(max(AUDIO_MANAGER.music_volume + delta, 0.0), 1.0)
            AUDIO_MANAGER.set_music_volume(new_volume)
            self.update_labels()

    def adjust_sfx_volume(self, delta=0.0):
        """Adjust sound effects volume."""
        if delta != 0.0:
            new_volume = min(max(AUDIO_MANAGER.effects_volume + delta, 0.0), 1.0)
            AUDIO_MANAGER.set_effects_volume(new_volume)
            AUDIO_MANAGER.play_sound("BUBBLE")
            self.update_labels()

    def toggle_mute(self):
        """Mute or unmute all sounds."""
        if AUDIO_MANAGER.muted:
            AUDIO_MANAGER.unmute()
            self.update_labels()
        else:
            AUDIO_MANAGER.mute()
            self.update_labels()
    
    def update_labels(self):
        """
        Update the text of the state labels and redraw them.
        """
        self.state_labels[0].set_text(f"{AUDIO_MANAGER.master_volume*100:.0f}%")
        self.state_labels[1].set_text(f"{AUDIO_MANAGER.music_volume*100:.0f}%")
        self.state_labels[2].set_text(f"{AUDIO_MANAGER.effects_volume*100:.0f}%")
        self.state_labels[3].set_text("Muted" if AUDIO_MANAGER.muted else "Unmuted")
        self.state_labels[4].set_text(commons.CURRENT_DIFFICULTY_MODE)
        
        # Redraw labels
        for label in self.state_labels:
            label.render()
    
    def change_difficulty(self):
        """Placeholder method to cycle through difficulty levels."""
        commons.CURRENT_DIFFICULTY_MODE = commons.DIFFICULTY_MODES[(commons.DIFFICULTY_MODES.index(commons.CURRENT_DIFFICULTY_MODE) + 1) % len(commons.DIFFICULTY_MODES)]
        self.update_labels()

    def go_back(self):
        """
        Go back to the previous page (typically the main menu).
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'entry'}))


    def handle_events(self, event):
        """
        Handle navigation and actions based on the selected option.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.current_selected_option = (self.current_selected_option + 1) % len(self.buttons)
                self.highlight_selected()
            elif event.key == pygame.K_UP:
                self.current_selected_option = (self.current_selected_option - 1) % len(self.buttons)
                self.highlight_selected()
            elif event.key == pygame.K_RETURN:
                self.buttons[self.current_selected_option].press()
            elif event.key == pygame.K_ESCAPE:
                self.go_back()
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.buttons[self.current_selected_option].is_hovered:
                    self.buttons[self.current_selected_option].press()
        elif event.type == pygame.MOUSEWHEEL:
            self._handle_mouse_scroll(event.y)

    def _handle_mouse_scroll(self, scroll_direction):
        """
        Handle mouse scroll to increase or decrease the volume of the selected button.
        """
        if self.current_selected_option == 0:  # Master Volume
            self.adjust_master_volume(delta=0.01 * scroll_direction)
        elif self.current_selected_option == 1:  # Music Volume
            self.adjust_music_volume(delta=0.01 * scroll_direction)
        elif self.current_selected_option == 2:  # Sound Effects Volume
            self.adjust_sfx_volume(delta=0.01 * scroll_direction)

    def _handle_mouse_motion(self, mouse_pos):
        """
        Update current_selected_option based on mouse hover and highlight the corresponding button.
        """
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                self.current_selected_option = i
                self.highlight_selected()
                return
        
        self.unselect_all()

    def resize(self, display_size):
        """
        Adjust the page elements and background based on the new screen size.
        """
        scale_x, scale_y = display_size[0] / commons.IWIDTH, display_size[1] / commons.IHEIGHT

        # Scale the background image to fit the new screen size
        self.bg_image = pygame.transform.scale(self._bg_image, display_size).convert()

        # Resize and re-render each menu element
        for element in self.elements:
            element.resize(scale_x, scale_y)
            element.render()

    def update(self, delta_time):
        """Update the settings page, if necessary."""
        pass

    def draw(self, screen):
        """
        Draw the settings page elements on the screen.
        """
        screen.blit(self.bg_image, (0, 0))  # Draw the scaled background image
        self.canvas.draw(screen)
        pygame.display.flip()
