import pygame
import commons

class StaticElement:
    def __init__(self, element_id, dimensions, position, health):
        """
        Represents a static element in the game (e.g., trees, chests).

        :param element_id: Unique identifier for the element type.
        :param dimensions: The width and height of the element as a Vector2.
        :param position: The position of the element in world coordinates as a Vector2.
        :param health: The current health of the element.
        """
        self.id: int = element_id  # Unique ID for the static element type
        self.rect: pygame.rect.Rect = pygame.Rect((0, 0), dimensions)
        self.rect.bottomleft = pygame.math.Vector2(position)  # Dimensions (width, height) of the element
        self.max_health: float = health
        self.health: float = health  # Health of the element

    def take_damage(self, damage, delta_time):
        """
        Reduces the health of the element by a specified amount.

        :param amount: Amount of damage to deal.
        """
        self.health = max(0, self.health - damage * delta_time)

    def is_destroyed(self):
        """
        Checks if the element has been destroyed (health <= 0).

        :return: True if destroyed, False otherwise.
        """
        return self.health <= 0

    def __repr__(self):
        """Returns a string representation of the static element."""
        return (f"StaticElement(id={self.id}, pos={self.rect.topleft}, "
                f"dim={self.rect.size}, health={self.health})")

    @classmethod
    def from_dict(cls, static_element):
        """
        Cria uma instância de StaticElement a partir de um dicionário.

        :param static_element: Dicionário com as informações do elemento.
        :return: Instância de StaticElement.
        """
        element_id = static_element['type']  # 'type' é o ID do elemento
        dimensions = (static_element['width'], static_element['height'])
        position = (static_element['x'], static_element['y'])
        health = static_element['health']
        return cls(element_id, dimensions, position, health)

