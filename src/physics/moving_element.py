import pygame
import commons
from typing import Tuple
from pygame.math import Vector2 as v2

class MovingElement(pygame.sprite.DirtySprite):
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

    def move(self, colliding_rects, delta_time):
        """
        Move the element first in the x direction, check for collisions, 
        then move in the y direction and check for collisions.

        :param colliding_rects: A list of rectangles to check for collisions.
        """

        #print(len(colliding_rects))
        #print(f'Current position {self.rect.topleft}, deltax: {self.velocity.x * delta_time}, deltay: {self.velocity.y * delta_time} - {colliding_rects}')

        # Move horizontally (x direction)
        self.rect.x += self.velocity.x * delta_time

        collided = False

        _colliding_rects = colliding_rects

        if self.velocity.x > 0:
            _colliding_rects = colliding_rects[-1::-1] # reverse the list

        for edge, rect in _colliding_rects: 
            if self.rect.colliderect(rect):
                


                if self.velocity.x > 0 and edge == 0b0011:
                    dx = self.rect.right - rect.left
                    self.rect.right = rect.left + dx
                    if self.rect.bottom > rect.bottom - dx:
                        self.rect.bottom = rect.bottom - dx
                        if self.velocity.y > 0:
                            self.velocity.y = 0
                        self.collided_right()
                
                elif self.velocity.x < 0 and edge == 0b0011:
                    dx = self.rect.right - rect.right
                    self.rect.right = rect.right + dx
                    if self.rect.bottom > rect.top - dx:
                        self.rect.bottom = rect.top - dx
                        if self.velocity.y > 0:
                            self.velocity.y = 0
                        self.collided_down()

                
                elif self.velocity.x < 0 and edge == 0b1001:
                    dx = self.rect.left - rect.right
                    self.rect.left = rect.right + dx
                    if self.rect.bottom > rect.bottom + dx:
                        self.rect.bottom = rect.bottom + dx
                        if self.velocity.y > 0:
                            self.velocity.y = 0
                        self.collided_down()
                
                elif self.velocity.x > 0 and edge == 0b1001:
                    dx = self.rect.left - rect.right
                    self.rect.left = rect.right + dx
                    if self.rect.bottom > rect.bottom + dx:
                        self.rect.bottom = rect.bottom + dx
                        if self.velocity.y > 0:
                            self.velocity.y = 0
                        self.collided_down()

                
                elif self.velocity.x > 0:  # Moving right
                    self.rect.right = rect.left
                    self.collided_right()
                    collided = True
                elif self.velocity.x < 0:  # Moving left
                    self.rect.left = rect.right
                    self.collided_left()
                    collided = True
                
    
        if collided:
            self.velocity.x = 0
            #print(f'{self.rect} collided in {_colliding_rects} - x')
        collided = False

        _colliding_rects = colliding_rects
        if self.velocity.y > 0: 
            _colliding_rects = colliding_rects[-1::-1]  # reverse the list

        # Update position vector to match adjusted rect
        self.position.x, self.position.y = self.rect.topleft

        # Move vertically (y direction)
        self.rect.y += self.velocity.y * delta_time

        for edge, rect in _colliding_rects:
            if self.rect.colliderect(rect):
                #print(f'{self.rect} collided with {rect} -- y')
                if self.velocity.y > 0 and edge == 0b0011:
                    dx = self.rect.right - rect.left
                    self.rect.bottom = rect.bottom - dx
                    self.collided_right()
                elif self.velocity.y < 0 and edge == 0b0011:
                    dx = self.rect.right - rect.left
                    #print("EXTROU")
                    if self.rect.bottom > rect.bottom - dx:
                        self.rect.bottom = rect.bottom - dx
                        collided = True
                        self.collided_right()
                        #print("entrou")
                elif self.velocity.y > 0 and edge == 0b1001:
                    dx = rect.right - self.rect.left
                    if abs(dx) < commons.BLOCK_SIZE:
                        self.rect.bottom = rect.bottom - dx
                    else:
                        self.rect.bottom = rect.top

                    self.collided_right()
                    #print(f"AQUI1: {self.velocity}")
                elif self.velocity.y < 0 and edge == 0b1001:
                    dx = rect.right - self.rect.left
                    if self.rect.bottom > rect.bottom - dx and abs(dx) < commons.BLOCK_SIZE:
                        self.rect.bottom = rect.bottom - dx
                        collided = True
                        self.collided_right()
                        #print("aqui2")
                elif self.velocity.y > 0:  # Moving down
                    self.rect.bottom = rect.top
                    self.collided_down()
                    collided = True
                elif self.velocity.y < 0:  # Moving up
                    self.rect.top = rect.bottom 
                    self.collided_up()
                    collided = True

        if collided:
            self.velocity.y = 0
            #print(f'{self.rect} collided in {_colliding_rects} - y')

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
