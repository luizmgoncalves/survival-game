from .moving_element import MovingElement, CollidableMovingElement
from images.image_loader import IMAGE_LOADER
from pygame import Vector2 as v2
import pygame
from rendering.animation import Animation



class ThrowableItem(CollidableMovingElement):
    def __init__(self, pos: v2, size: v2, velocity: v2, animation: Animation):
        """
        Initialize a throwable item with a single animation.

        :param pos: Initial position of the throwable item.
        :param size: Size of the throwable item.
        :param velocity: Initial velocity of the throwable item.
        :param animation: Animation to display for the throwable item.
        """
        super().__init__(pos, size, velocity)
        self.animation = animation
        self.image = IMAGE_LOADER.get_image(animation.get_current_frame())
        self.dying = False
    
    def is_alive(self):
        #...
        return self.is_falling

    def update(self, delta_time: float):
        """
        Update the throwable item position and animation.

        :param delta_time: Time elapsed since the last update.
        """

        # Update animation
        self.animation.update(delta_time)
        self.image = IMAGE_LOADER.get_image(self.animation.get_current_frame())


class DirectionalThrowableItem(ThrowableItem):
    def __init__(self, pos: v2, size: v2, velocity: v2, animation: Animation):
        """
        Initialize a directional throwable item that rotates based on its velocity.

        :param pos: Initial position of the throwable item.
        :param size: Size of the throwable item.
        :param velocity: Initial velocity of the throwable item.
        :param animation: Animation to display for the throwable item.
        """
        super().__init__(pos, size, velocity, animation)

    def update(self, delta_time: float):
        """
        Update the throwable item's position, animation, and rotation based on velocity.

        :param delta_time: Time elapsed since the last update.
        """
        super().update(delta_time)

        # Calculate the angle of rotation based on velocity
        angle = self.velocity.angle_to(v2(1, 0))

        # Rotate the image to match the velocity direction
        if self.image:
            self.image = pygame.transform.rotate(IMAGE_LOADER.get_image(self.animation.get_current_frame()), angle)
            self.rect = self.image.get_rect(center=self.rect.center)


class Bullet(ThrowableItem):
    def __init__(self, pos: v2, size: v2, velocity: v2, animation: Animation, damage: int):
        """
        Initialize a bullet with a specific damage value.

        :param pos: Initial position of the bullet.
        :param size: Size of the bullet.
        :param velocity: Initial velocity of the bullet.
        :param animation: Animation to display for the bullet.
        :param damage: The amount of damage the bullet inflicts.
        """
        super().__init__(pos, size, velocity, animation)
        self.damage = damage

    def get_damage(self) -> int:
        """
        Retrieve the damage value of the bullet.
        :return: The damage value.
        """
        return self.damage


class DirectionalBullet(DirectionalThrowableItem):
    def __init__(self, pos: v2, size: v2, velocity: v2, animation: Animation, damage: int):
        """
        Initialize a directional bullet with a specific damage value.

        :param pos: Initial position of the bullet.
        :param size: Size of the bullet.
        :param velocity: Initial velocity of the bullet.
        :param animation: Animation to display for the bullet.
        :param damage: The amount of damage the bullet inflicts.
        """
        # Call both parent constructors
        DirectionalThrowableItem.__init__(self, pos, size, velocity, animation)
        self.damage = damage

    def update(self, delta_time: float):
        """
        Update the directional bullet's position, animation, and rotation based on velocity.

        :param delta_time: Time elapsed since the last update.
        """
        # Call the update method from DirectionalThrowableItem
        DirectionalThrowableItem.update(self, delta_time)


class Arrow(DirectionalBullet):
    def __init__(self, pos: v2, velocity: v2):
        im = IMAGE_LOADER.get_image("ARSENAL_ARROW.FRAME1")
        an = Animation(["ARSENAL_ARROW.FRAME1"], 1, False)
        size = im.get_size()
        DirectionalBullet.__init__(self, pos, size, velocity, an, 8)

class Axe(Bullet):
    def __init__(self, pos: v2, velocity: v2):
        im = IMAGE_LOADER.get_image("ARSENAL_AXE.FRAME1")
        an = Animation([f"ARSENAL_AXE.FRAME{i}" for i in range(1, 9)], 0.05, False)
        size = v2(im.get_size())/2
        Bullet.__init__(self, pos, size, velocity, an, 20)
