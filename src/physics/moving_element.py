import pygame
import commons
from typing import Tuple, List
from pygame.math import Vector2 as v2

class MovingElement(pygame.sprite.Sprite):
    """
    Base class for moving elements in the game, inheriting from pygame's DirtySprite.

    Attributes:
        position (pygame.Vector2): The current position in world coordinates.
        velocity (pygame.Vector2): The velocity of the element (units per tick).
        size (tuple[int, int]): The size (width, height) of the element in pixels.
    """
    def __init__(self, position: Tuple[int, int], size: Tuple[int, int], velocity: Tuple[int, int] = (0, 0), falls: bool=True):
        """
        Initialize a moving element.

        :param position: A tuple (x, y) representing the starting position in world coordinates.
        :param size: A tuple (width, height) representing the size of the element in pixels.
        :param velocity: A tuple (vx, vy) representing the initial velocity.
        :param falls: A bool b representing if the moving element does fall (needs to have gravity applied).
        """
        super().__init__()
        self.position: v2 = pygame.Vector2(position)
        self.velocity: v2 = pygame.Vector2(velocity)
        self.size: v2 = v2(size)
        self.does_fall = falls

        # Create the pygame Rect for collisions and rendering
        self.rect = pygame.Rect(self.position.x, self.position.y, *self.size)


class CollidableMovingElement(MovingElement):
    """
    A moving element that supports collision management.

    Methods:
        resolve_collision: Resolve collisions with other collidable sprites.
        move: Move the element by first handling horizontal movement, then vertical movement.
    """
    def __init__(self, position: Tuple[int, int], size: Tuple[int, int], velocity: Tuple[int, int]=(0, 0)):
        """
        Initialize a collidable moving element.

        :param position: A tuple (x, y) representing the starting position in world coordinates.
        :param size: A tuple (width, height) representing the size of the element in pixels.
        :param velocity: A tuple (vx, vy) representing the initial velocity.
        """
        super().__init__(position, size, velocity)
        self.is_falling = True  # Initially assume the object is falling.

    def move(self, colliding_rects: List[pygame.Rect], delta_time: float):
        """
        Move the element first in the x direction, check for collisions, 
        then move in the y direction and check for collisions.

        :param colliding_rects: A list of rectangles to check for collisions.
        :param delta_time: The time delta for movement calculations.
        """

        tallest_down = None
        last_velocity = self.velocity.x

        def get_tallest_down_collision(rect: pygame.Rect):
            nonlocal tallest_down
            if tallest_down is None  or rect.top < tallest_down:
                tallest_down = rect.top


        def handle_horizontal_collisions():
            nonlocal collided

            for edge, rect in _colliding_rects:
                if self.rect.colliderect(rect):
                    if edge not in (0b0011, 0b1001):
                        if self.velocity.x > 0:  # Moving right
                            self.rect.right = rect.left
                            self.collided_right()
                        elif self.velocity.x < 0:  # Moving left
                            self.rect.left = rect.right
                            self.collided_left()
                        collided = True
                        get_tallest_down_collision(rect)

                if one_above.colliderect(rect):
                    nonlocal one_above_collided, one_above_y_collision
                    one_above_collided = True
                    one_above_y_collision = rect.bottom

        def handle_vertical_collisions():
            nonlocal collided

            for edge, rect in _colliding_rects:
                if self.rect.colliderect(rect):
                    if edge not in (0b0011, 0b1001):
                        if self.velocity.y > 0:  # Moving down
                            self.rect.bottom = rect.top
                            self.collided_down()
                        elif self.velocity.y < 0:  # Moving up
                            self.rect.top = rect.bottom
                            self.collided_up()
                        collided = True

        def handle_ramps():
            nonlocal collided

            for edge, rect in ramps:
                if self.rect.colliderect(rect):
                    dx = self.rect.right - rect.left if edge == 0b0011 else rect.right - self.rect.left
                    ramp_bottom = rect.bottom - dx

                    if dx > 0 and self.rect.bottom > ramp_bottom:
                        self.rect.bottom = max(ramp_bottom, rect.top)
                        if one_above_collided:
                            adjust_for_one_above(edge)
                        collided = True
                        self.collided_down()
                    
                    if tallest_down is not None and self.rect.bottom <= tallest_down:
                        self.velocity.x = last_velocity

        def adjust_for_one_above(edge):
            nonlocal one_above_y_collision, last_velocity

            new_top = max(one_above_y_collision, self.rect.top)
            dy = new_top - self.rect.top
            self.rect.x += dy if edge == 0b1001 else -dy
            self.rect.top = new_top

            if dy:
                self.velocity.x = 0
                last_velocity = 0

        # Move horizontally (x direction)
        one_above = self.rect.copy()
        one_above.y -= commons.BLOCK_SIZE

        one_above_collided = False
        one_above_y_collision = 0.0

        self.rect.x += self.velocity.x * delta_time
        collided = False

        _colliding_rects = colliding_rects[::-1] if self.velocity.x > 0 else colliding_rects
        handle_horizontal_collisions()

        if collided:
            self.velocity.x = 0

        # Move vertically (y direction)
        self.rect.y += self.velocity.y * delta_time
        collided = False

        self.is_falling = True  # Initially assume the object is falling.

        _colliding_rects = colliding_rects if self.velocity.y > 0 else colliding_rects[::-1]
        handle_vertical_collisions()

        ramps = [(edge, rect) for edge, rect in _colliding_rects if edge in (0b0011, 0b1001)]
        handle_ramps()

        if collided:
            self.velocity.y = 0

        # Update position vector to match adjusted rect
        self.position.x, self.position.y = self.rect.topleft


    
    def collided_up(self):
        """
        Handle the collision when the object collides from above.
        """
        #print("Collided up")
        # Implement your specific logic for upward collision

    def collided_down(self):
        """
        Handle the collision when the object collides from below.
        """
        self.is_falling = False  # Initially assume the object is falling.
        #print("Collided down")
        # Implement your specific logic for downward collision

    def collided_left(self):
        """
        Handle the collision when the object collides from the left.
        """
        #print("Collided left")
        # Implement your specific logic for leftward collision

    def collided_right(self):
        """
        Handle the collision when the object collides from the right.
        """
        #print("Collided right")
        # Implement your specific logic for rightward collision
