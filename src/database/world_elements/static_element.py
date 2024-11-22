import pygame

class StaticElement:
    def __init__(self, name, element_id, dimensions, position, health):
        """
        Represents a static element in the game (e.g., trees, chests).

        :param element_id: Unique identifier for the element type.
        :param dimensions: The width and height of the element as a Vector2.
        :param position: The position of the element in world coordinates as a Vector2.
        :param health: The current health of the element.
        """
        self.name = name
        self.element_id = element_id  # Unique ID for the static element type
        self.dim = pygame.math.Vector2(dimensions)  # Dimensions (width, height) of the element
        self.pos = pygame.math.Vector2(position)  # Position in world space
        self.health = health  # Health of the element

    def take_damage(self, amount):
        """
        Reduces the health of the element by a specified amount.

        :param amount: Amount of damage to deal.
        """
        self.health = max(0, self.health - amount)

    def is_destroyed(self):
        """
        Checks if the element has been destroyed (health <= 0).

        :return: True if destroyed, False otherwise.
        """
        return self.health <= 0

    def __repr__(self):
        """Returns a string representation of the static element."""
        return (f"StaticElement(name={self.name},id={self.element_id}, pos={self.pos}, "
                f"dim={self.dim}, health={self.health})")
