from pygame.sprite import LayeredUpdates
from gui.button import Button
from gui.label import Label
from .page import Page
import commons
import pygame
import images.image_loader as image_loader

WIDTH, HEIGHT = 1920, 1080

# Custom event for page change

class EntryMenu(Page):
    def __init__(self):
        """
        Initialize the Menu with background image, labels, buttons, and other display elements.
        """
        super().__init__()  # Call the constructor of the base Page class
        
        self.QUIT = False
        self.showing = False
        self.current_selected_option = 0  # Index to track selected option
        
        # Load and scale background image
        self._bg_image = image_loader.IMAGE_LOADER.get_image('WALLPAPER')
        self.bg_image = self._bg_image
        
        # Initialize menu labels and buttons
        self.labels = [Label("Cave Game", WIDTH / 2, 220)]
        self.buttons = [
            Button("settings", WIDTH - 50, 50, width=100, height=80, font_size=60, on_click=self.go_to_settings_page),
            Button("Worlds", WIDTH / 2, 400, width=400, font_size=60, on_click=self.go_to_worlds_page), 
            Button("New World", WIDTH / 2, 550, width=440, font_size=60, on_click=self.go_to_creating_page),
            Button("Quit", WIDTH / 2, 700, width=300, font_size=60, on_click=self.quit_action),
        ]
        
        # Combine labels and buttons for unified handling
        self.elements = self.labels + self.buttons
        
        # Set up layered canvas for drawing elements
        self.canvas = LayeredUpdates(self.elements)

        self.resize(pygame.display.get_window_size())
    
    def reset(self, **kwargs):
        self.unselect_all()

    def quit_action(self):
        """
        Action to set QUIT to True, triggered by the Quit button.
        """
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def go_to_creating_page(self):
        """
        Action to trigger a custom event that changes the page to the WorldsPage.
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'create'}))

    def go_to_worlds_page(self):
        """
        Action to trigger a custom event that changes the page to the WorldsPage.
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'worlds_page'}))
    
    def go_to_settings_page(self):
        """
        Action to trigger a custom event that changes the page to the WorldsPage.
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'settings'}))

    def resize(self, display_size):
        """
        Handle resizing the menu elements and background image based on screen size.
        """
        scale_x, scale_y = display_size[0] / WIDTH, display_size[1] / HEIGHT

        # Scale the background image to fit the new screen size
        self.bg_image = pygame.transform.smoothscale(self._bg_image, display_size).convert()

        # Resize and re-render each menu element
        for element in self.elements:
            element.resize(scale_x, scale_y)
            element.render()

    def handle_events(self, event):
        """
        Process user input events including window resize, mouse movement, clicks, and key presses.
        """
        if event.type == pygame.QUIT:
            self.QUIT = True
        elif event.type == pygame.VIDEORESIZE:
            self.resize(event.size)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self._handle_mouse_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.quit_action()
            elif event.key == pygame.K_DOWN:
                self.current_selected_option = (self.current_selected_option + 1) % len(self.buttons)
                self.highlight_selected()
            elif event.key == pygame.K_UP:
                self.current_selected_option = (self.current_selected_option - 1) % len(self.buttons)
                self.highlight_selected()
            elif event.key == pygame.K_RETURN:
                self.buttons[self.current_selected_option].press()

    def _handle_mouse_motion(self, mouse_pos):
        """
        Check if the mouse is hovering over any buttons and adjust the selection state.
        """
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                self.current_selected_option = i
                self.highlight_selected()
                return

        self.unselect_all()
        self.current_selected_option = -1  # Indicate no button is selected

    def _handle_mouse_click(self, mouse_pos):
        """
        Handle mouse clicks, triggering the action for the hovered button.
        """
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                self.current_selected_option = i
                button.press()
                return

    def highlight_selected(self):
        """
        Highlight the currently selected button.
        """
        for i, button in enumerate(self.buttons):
            if i == self.current_selected_option:
                button.select()
            else:
                button.unselect()

    def unselect_all(self):
        """
        Unhighlight all buttons.
        """
        for button in self.buttons:
            button.unselect()

    def update(self):
        """
        Update the menu's state, such as animations or button states.
        """
        # If there are any updates to the menu (e.g., animations, changing states), implement here.
        pass

    def draw(self, screen):
        """
        Draw the page elements on the screen.
        """
        screen.blit(self.bg_image, (0, 0))
        self.canvas.draw(screen)
        pygame.display.flip()
