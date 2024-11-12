from pygame.sprite import LayeredUpdates
from gui.button import Button
from gui.label import Label
from .page import Page
import pygame
import commons

class SettingsPage(Page):
    def __init__(self):
        """
        Initialize the Settings page with a background image, labels, buttons for volume, mute, difficulty, and back.
        """
        super().__init__()
        
        self.showing = False
        self.current_selected_option = 0  # Index to track selected option
        
        # Load and scale the background image
        self._bg_image = pygame.image.load('./game_images/forest_background.png').convert()
        self.bg_image = self._bg_image

        # Labels and buttons for settings options
        self.labels = [Label("Settings", commons.WIDTH / 2, 100)]
        self.buttons = [
            Button("Master Volume", commons.WIDTH / 2, 250, width=400, font_size=60, on_click=self.adjust_master_volume),
            Button("Music Volume", commons.WIDTH / 2, 350, width=400, font_size=60, on_click=self.adjust_music_volume),
            Button("Sound Effects Volume", commons.WIDTH / 2, 450, width=400, font_size=60, on_click=self.adjust_sfx_volume),
            Button("Mute", commons.WIDTH / 2, 550, width=200, font_size=60, on_click=self.toggle_mute),
            Button("Difficulty", commons.WIDTH / 2, 650, width=300, font_size=60, on_click=self.change_difficulty),
            Button("Back", commons.WIDTH / 2, 750, width=200, font_size=60, on_click=self.go_back)
        ]
        
        # Set up elements for canvas and highlight selected option
        self.elements = self.labels + self.buttons
        self.canvas = LayeredUpdates(self.elements)
        self.highlight_selected()
        
        # Resize elements to initial screen size
        self.resize(pygame.display.get_window_size())

    def highlight_selected(self):
        """
        Highlight the currently selected button.
        """
        for i, button in enumerate(self.buttons):
            if i == self.current_selected_option:
                button.select()  # Custom method to visually select a button
            else:
                button.unselect()  # Custom method to visually deselect a button

    def adjust_master_volume(self):
        """Placeholder method to adjust the master volume."""
        pass

    def adjust_music_volume(self):
        """Placeholder method to adjust the music volume."""
        pass

    def adjust_sfx_volume(self):
        """Placeholder method to adjust sound effects volume."""
        pass

    def toggle_mute(self):
        """Placeholder method to mute or unmute all sounds."""
        pass

    def change_difficulty(self):
        """Placeholder method to cycle through difficulty levels."""
        pass

    def go_back(self):
        """
        Go back to the previous page (typically the main menu).
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'entry_menu'}))

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
                self.buttons[self.current_selected_option].press()

    def _handle_mouse_motion(self, mouse_pos):
        """
        Update current_selected_option based on mouse hover and highlight the corresponding button.
        """
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                self.current_selected_option = i
                self.highlight_selected()
                break

    def resize(self, display_size):
        """
        Adjust the page elements and background based on the new screen size.
        """
        scale_x, scale_y = display_size[0] / commons.WIDTH, display_size[1] / commons.HEIGHT

        # Scale the background image to fit the new screen size
        self.bg_image = pygame.transform.scale(self._bg_image, display_size).convert()

        # Resize and re-render each menu element
        for element in self.elements:
            element.resize(scale_x, scale_y)
            element.render()

    def update(self):
        """Update the settings page, if necessary."""
        pass

    def draw(self, screen):
        """
        Draw the settings page elements on the screen.
        """
        screen.blit(self.bg_image, (0, 0))  # Draw the scaled background image
        self.canvas.draw(screen)
        pygame.display.flip()
