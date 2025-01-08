import pygame
from pygame.sprite import LayeredUpdates
from gui.button import Button
from gui.label import Label
from .page import Page
import commons
import images.image_loader as image_loader
from database.world_loader import WORLD_LOADER

class WorldPage(Page):
    def __init__(self):
        """
        Initialize the WorldsPage with a background image, labels, buttons, and world buttons.
        """
        super().__init__()

        self.QUIT = False
        self.showing = False
        
        # Load and scale background image
        self._bg_image = image_loader.IMAGE_LOADER.get_image("WALLPAPER")
        self.bg_image = self._bg_image

        self.current_selected_option = 0  # Index to track selected option

        self.world_name: str = ''

        # Initialize labels and buttons
        self.world_name_label = Label(f"", commons.WIDTH / 2, 220)
        self.statistics = Label(f"Score: ", commons.WIDTH / 2, 500, font_size=40)
        self.buttons = [
            Button("Play", commons.WIDTH / 3, 400, width=440, font_size=60),
            Button("Delete", commons.WIDTH / 3 * 2, 400, width=440, font_size=60, on_click=self.delete_world),
            Button("Back to Worlds Menu", commons.WIDTH / 2, 900, width=440, font_size=60, on_click=self.go_back_to_worlds_menu),
        ]

        self.elements: list = [self.world_name_label, self.statistics] + self.buttons

        # Set up layered canvas for drawing elements
        self.canvas = LayeredUpdates(self.elements)
    
    def delete_world(self):
        """
        Delete world names from the database.
        """
        if not self.world_name:
            return
        
        WORLD_LOADER.delete_world(self.world_name)

        self.go_back_to_worlds_menu()
    
    def _gen_stats(self) -> str:
        world = WORLD_LOADER.get_world(self.world_name)

        self.statistics = Label(f"Score: {world.get('score', 0)}, Seed: {world.get('seed', 0)}", commons.WIDTH / 2, 500, font_size=40)
    
    def reset(self, world='', **kwargs):

        if WORLD_LOADER.get_world(world) is None:
            self.go_back_to_worlds_menu()
            return
        
        self.unselect_all()

        self.elements.remove(self.world_name_label)
        self.elements.remove(self.statistics)
        self.canvas.remove(self.world_name_label)
        self.canvas.remove(self.statistics)

        self.world_name = world

        self.world_name_label = Label(f"{world}", commons.WIDTH / 2, 220)
        self._gen_stats()
        self.elements.append(self.world_name_label)
        self.elements.append(self.statistics)
        self.canvas.add(self.world_name_label)
        self.canvas.add(self.statistics)

        self.resize(pygame.display.get_window_size())
    
    def unselect_all(self):
        for button in self.buttons:
            button.unselect()
    
    def highlight_selected(self):
        """
        Highlight the currently selected button.
        """
        for i, button in enumerate(self.buttons):
            if i == self.current_selected_option:
                button.select()  # Custom method to visually select a button
            else:
                button.unselect()  # Custom method to visually deselect a button

    def go_back_to_worlds_menu(self):
        """
        Action to trigger a custom event that changes the page back to the EntryMenu.
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'worlds_page'}))

    def resize(self, display_size):
        """
        Handle resizing the menu elements and background image based on screen size.
        """
        scale_x, scale_y = display_size[0] / commons.WIDTH, display_size[1] / commons.HEIGHT

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
        elif event.type == pygame.KEYDOWN:
            self._handle_key_down(event)

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
                    button.press()

    def _handle_key_down(self, event):
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

    def update(self):
        """
        Update the page's state, such as animations or button states.
        """
        pass

    def draw(self, screen):
        """
        Draw the page elements on the screen.
        """
        screen.blit(self.bg_image, (0, 0))
        self.canvas.draw(screen)
        pygame.display.flip()
