import pygame
from pygame.sprite import LayeredUpdates
from gui.button import Button
from gui.label import Label
from .page import Page
import commons
import images.image_loader as image_loader
from database.world_loader import WORLD_LOADER

ANIMATION_SPEED = 50  # Controls the speed of the animation

class WorldsPage(Page):
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
        
        # Initialize labels and buttons
        self.labels = [Label("Worlds", commons.WIDTH / 2, 220)]
        self.buttons = [
            Button("Back to Entry Menu", commons.WIDTH / 2, 900, width=440, font_size=60, on_click=self.go_back_to_entry_menu),
        ]

        self.no_worlds = Label("You have no worlds yet", commons.WIDTH / 2, commons.HEIGHT / 2)

        # Set up layered canvas for drawing elements
        self.canvas = LayeredUpdates()
        
        self.reset()
    
    def reset(self, **kwargs):
        self.unselect_all()

         # Load worlds from the database
        self.worlds = self.load_worlds()
        self.world_buttons = self.create_world_buttons()

        # Set up the floating world button in the center
        self.floating_button = self.world_buttons[0] if self.world_buttons else None

        # Combine labels, buttons, and world buttons for unified handling
        self.elements = self.labels + self.buttons + self.world_buttons

        if not self.world_buttons:
            self.elements.append(self.no_worlds)
        
        self.canvas.empty()
        self.canvas.add(self.elements)

        self.resize(pygame.display.get_window_size())
        
        # Tracking the current world button index
        self.current_world_index = 0
        self.animating = False
        self.animation_progress = 0  # Used for tracking animation progress
    
    def unselect_all(self):
        for button in self.buttons:
            button.unselect()

    def go_back_to_entry_menu(self):
        """
        Action to trigger a custom event that changes the page back to the EntryMenu.
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'entry'}))
    
    def go_to_create_world(self):
        """
        Action to trigger a custom event that changes the page to the Creating World page.
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'create'}))

    def go_to_world_page(self, world):
        """
        Action to trigger a custom event that changes the page to the World page.
        """
        pygame.event.post(pygame.event.Event(commons.CHANGE_PAGE_EVENT, {'page': 'world', 'world': world}))

    def load_worlds(self):
        """
        Load world names from the database.
        """
        from random import randint
        worlds = WORLD_LOADER.get_worlds() # {world_id: int, name: str, score: int}
        worlds = [x['name'] for x in worlds]
        #cursor = self.db.cursor()
        #cursor.execute("SELECT name FROM worlds")  # Modify as per your database schema
        #rows = cursor.fetchall()
        #for row in rows:
        #    worlds.append(row[0])
        return worlds

    def create_world_buttons(self):
        """
        Create buttons for each world.
        """
        world_buttons = []
        button_height = 60
        for i, world in enumerate(self.worlds):
            if i == 0:
                button = Button(world, commons.WIDTH/2, commons.HEIGHT/2, width=400, font_size=50, on_click=self.go_to_world_page, click_args=[world])
            else:
                button = Button(world, commons.WIDTH*1.5, commons.HEIGHT/2, width=400, font_size=50, on_click=self.go_to_world_page, click_args=[world])
            world_buttons.append(button)
        

        return world_buttons

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
        for button in self.buttons + self.world_buttons:
            if button.rect.collidepoint(mouse_pos):
                button.select()
            else:
                button.unselect()

    def _handle_mouse_click(self, event):
        """
        Process mouse button clicks. You can add custom actions here.
        """
        if event.button == 1:
            for button in self.buttons + self.world_buttons:
                if button.rect.collidepoint(event.pos):
                    button.press()

    def _handle_key_down(self, event):
        """
        Handle key presses to toggle between world buttons.
        """
        if event.key == pygame.K_LEFT:
            self.switch_world(1)  # Move to previous world
        elif event.key == pygame.K_RIGHT:
            self.switch_world(-1)  # Move to next world

    def switch_world(self, direction):
        """
        Switch to the next or previous world button with animation.
        """
        if self.animating:
            return  # If an animation is already in progress, prevent switching worlds

        if len(self.world_buttons) <= 1:
            return  # No world buttons to switch
 
        self.animating = True
        self.animation_progress = 0  # Reset animation progress
        self.animation_direction = direction  # Store direction for the animation

        # Move the current world button off-screen (left or right)
        self.animation_target_x = -commons.WIDTH/2 if direction == -1 else commons.WIDTH * 1.5  # Move left or right

        # Update the current world index
        self.current_world_index = (self.current_world_index + direction) % len(self.world_buttons)

        # Get the next world button and position it off-screen
        self.floating_button = self.world_buttons[self.current_world_index]

        # Move the current button off-screen (direction can be left or right)
        self.current_button = self.world_buttons[(self.current_world_index - direction) % len(self.world_buttons)]

        if self.floating_button.base_rect.centerx <= 0 and direction == -1:
            self.floating_button.set_pos(commons.WIDTH*1.5,commons.HEIGHT/2)
        
        elif self.floating_button.base_rect.centerx >= commons.WIDTH and direction == 1:
            self.floating_button.set_pos(commons.WIDTH*-0.5,commons.HEIGHT/2)

    def update(self):
        """
        Update the page's state, such as animations or button states.
        """
        if self.animating:
            # Animate the current button out of the screen
            if self.animation_direction == -1:  # Move to the left
                self.current_button.move(-ANIMATION_SPEED, 0)
                self.floating_button.move(-ANIMATION_SPEED, 0)
            else:  # Move to the right
                self.current_button.move(ANIMATION_SPEED, 0)
                self.floating_button.move(ANIMATION_SPEED, 0)

            # Check if the animation is complete
            if (self.animation_direction == -1 and self.current_button.base_rect.center[0] <= self.animation_target_x) or \
               (self.animation_direction == 1 and self.current_button.base_rect.center[0] >= self.animation_target_x):
                # Once off-screen, reset position and stop animating
                self.animating = False
                self.current_button.set_pos(-commons.WIDTH / 2, commons.HEIGHT / 2)
                self.floating_button.set_pos(commons.WIDTH / 2, commons.HEIGHT / 2)

    def draw(self, screen):
        """
        Draw the page elements on the screen.
        """
        screen.blit(self.bg_image, (0, 0))
        self.canvas.draw(screen)
        pygame.display.flip()
