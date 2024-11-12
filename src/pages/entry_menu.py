from pygame.sprite import LayeredUpdates
from gui.button import Button
from gui.label import Label
from .page import Page
import commons
import pygame

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
        
        # Load and scale background image
        self._bg_image = pygame.image.load('./game_images/forest_background.png').convert()
        self.bg_image = self._bg_image
        
        # Initialize menu labels and buttons
        self.labels = [Label("Cave Game", WIDTH / 2, 220)]
        self.buttons = [
            Button("Worlds", WIDTH / 2, 400, width=400, font_size=60, on_click=self.go_to_worlds_page), 
            Button("New World", WIDTH / 2, 550, width=440, font_size=60),
            Button("Quit", WIDTH / 2, 700, width=300, font_size=60, on_click=self.quit_action),
        ]
        
        # Combine labels and buttons for unified handling
        self.elements = self.labels + self.buttons
        
        # Set up layered canvas for drawing elements
        self.canvas = LayeredUpdates(self.elements)

        self.resize(pygame.display.get_window_size())

    def quit_action(self):
        """
        Action to set QUIT to True, triggered by the Quit button.
        """
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def go_to_worlds_page(self):
        """
        Action to trigger a custom event that changes the page to the WorldsPage.
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'worlds_page'}))

    def resize(self, display_size):
        """
        Handle resizing the menu elements and background image based on screen size.
        """
        scale_x, scale_y = display_size[0] / WIDTH, display_size[1] / HEIGHT

        # Scale the background image to fit the new screen size
        self.bg_image = pygame.transform.scale(self._bg_image, display_size).convert()

        # Resize and re-render each menu element
        for element in self.elements:
            element.resize(scale_x, scale_y)
            element.render()

    def handle_events(self, event):
        """
        Process user input events including window resize, mouse movement, and clicks.
        """
        if event.type == pygame.QUIT:
            self.QUIT = True
        elif event.type == pygame.VIDEORESIZE:
            self.resize(event.size)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.quit_action()

    def _handle_mouse_motion(self, mouse_pos):
        """
        Check if the mouse is hovering over any buttons and adjust selection state.
        """
        for button in self.buttons:
            if button.rect.collidepoint(mouse_pos):
                button.select()
            else:
                button.unselect()

    def _handle_mouse_click(self, event):
        """
        Process mouse button clicks. You can add custom actions here.
        """
        if event.button == 1:
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    button.press()  # Perform button action on click

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
