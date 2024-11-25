import pygame
from abc import abstractmethod


class MovingElement(pygame.sprite.DirtySprite):
    """
    Base class for moving elements in the game, inheriting from pygame's DirtySprite.

    Attributes:
        position (pygame.Vector2): The current position in world coordinates.
        velocity (pygame.Vector2): The velocity of the element (units per tick).
        size (tuple[int, int]): The size (width, height) of the element in pixels.
    """
    def __init__(self, position, size, velocity=(0, 0)):
        """
        Initialize a moving element.

        :param position: A tuple (x, y) representing the starting position in world coordinates.
        :param size: A tuple (width, height) representing the size of the element in pixels.
        :param velocity: A tuple (vx, vy) representing the initial velocity.
        """
        super().__init__()
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.size = size

        # Create the pygame Rect for collisions and rendering
        self.rect = pygame.Rect(self.position.x, self.position.y, *self.size)

    @abstractmethod
    def update(self, delta_time):
        """
        Update the position based on velocity.

        :param delta_time: The time step to apply to the motion.
        """
        pass


class CollidableMovingElement(MovingElement):
    """
    A moving element that supports collision management.

    Methods:
        resolve_collision: Resolve collisions with other collidable sprites.
        move: Move the element by first handling horizontal movement, then vertical movement.
    """
    def __init__(self, position, size, velocity=(0, 0)):
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
        # Move horizontally (x direction)
        self.rect.x += self.velocity.x * delta_time

        for rect in colliding_rects:
            if self.rect.colliderect(rect):
                if self.velocity.x > 0:  # Moving right
                    self.rect.right = rect.left
                    self.velocity.x = 0
                    self.collided_right()
                elif self.velocity.x < 0:  # Moving left
                    self.rect.left = rect.right
                    self.velocity.x = 0
                    self.collided_left()

        # Update position vector to match adjusted rect
        self.position.x, self.position.y = self.rect.topleft

        # Move vertically (y direction)
        self.rect.y += self.velocity.y * delta_time
        

        for rect in colliding_rects:
            if self.rect.colliderect(rect):
                if self.velocity.y > 0:  # Moving down
                    self.rect.bottom = rect.top
                    self.collided_down()
                elif self.velocity.y < 0:  # Moving up
                    self.rect.top = rect.bottom 
                    self.collided_up()
                print("collided")
                self.velocity.y = 0

        # Update position vector to match adjusted rect
        self.position.x, self.position.y = self.rect.topleft
    
    def collided_up(self):
        """
        Handle the collision when the object collides from above.
        """
        print("Collided up")
        # Implement your specific logic for upward collision

    def collided_down(self):
        """
        Handle the collision when the object collides from below.
        """
        print("Collided down")
        # Implement your specific logic for downward collision

    def collided_left(self):
        """
        Handle the collision when the object collides from the left.
        """
        print("Collided left")
        # Implement your specific logic for leftward collision

    def collided_right(self):
        """
        Handle the collision when the object collides from the right.
        """
        print("Collided right")
        # Implement your specific logic for rightward collision
