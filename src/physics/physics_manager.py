import commons
from .player import Player
from .enemy import Enemy
from .bullet import Bullet
from .moving_element import MovingElement
from typing import List

class PhysicsManager:
    def __init__(self, 
                 player: Player, 
                 player_bullets: List[Bullet], 
                 enemies: List[Enemy], 
                 enemy_bullets: List[Bullet],
                 moving_elements: List[MovingElement]):
        """
        Initialize the PhysicsManager to handle game physics and interactions.

        :param player: The Player instance to manage.
        :param player_bullets: A list of Bullet objects fired by the player.
        :param enemies: A list of Enemy objects in the game.
        :param moving_elements: A list of MovingElement objects (e.g., projectiles, platforms).
        """
        self.player: Player = player
        self.player_bullets: List[Bullet] = player_bullets
        self.enemies: List[Enemy] = enemies
        self.moving_elements: List[MovingElement] = moving_elements
        self.enemy_bullets: List[Bullet] = enemy_bullets 
        self.moving_elements: List[MovingElement] = moving_elements
        self.gravity: int = commons.GRAVITY_ACELERATION

    def update(self, delta_time, world):
        """
        Update the state of all managed elements.
        
        :param delta_time: Time elapsed since the last update (in seconds).
        """
        
        self.apply_gravity()
        self.move_entities_and_handle_world_collisions(world)
        self.handle_collisions()

        # Update player
        self.player.update(delta_time)

        # Update player bullets
        for bullet in self.player_bullets:
            bullet.update(delta_time)

        # Update enemies bullets
        for bullet in self.enemy_bullets:
            bullet.update(delta_time)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(delta_time)

        # Update other moving elements
        for element in self.moving_elements:
            element.update(delta_time)
    
    def apply_gravity(self):
        """
        Apply gravity to all entities affected by physics.
        """
        # Apply gravity to the player
        self._apply_gravity_to_entity(self.player)

        # Apply gravity to enemies
        for enemy in self.enemies:
            self._apply_gravity_to_entity(enemy)

        # Apply gravity to moving elements
        for element in self.moving_elements:
            self._apply_gravity_to_entity(element)
        
    def _apply_gravity_to_entity(self, entity: MovingElement):
        """
        Apply gravity to a single entity.

        :param entity: The entity to which gravity will be applied.
        """
        entity.velocity.y += self.gravity

    def handle_collisions(self):
        """
        Handle collisions between entities (e.g., player and enemies, bullets and enemies).
        """
        # Check collisions between player bullets and enemies
        for bullet in self.player_bullets:
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):  # Assuming entities have a `rect` attribute for collision
                    self._handle_bullet_hit_enemy(bullet, enemy)

        # Check collisions between player and enemies
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self._handle_player_enemy_collision(enemy)

        # Check collisions between player and moving elements (optional)
        for element in self.moving_elements:
            if self.player.rect.colliderect(element.rect):
                self._handle_player_element_collision(element)

    def _handle_bullet_hit_enemy(self, bullet, enemy):
        """
        Handle the event where a bullet hits an enemy.

        :param bullet: The Bullet instance that collided with the enemy.
        :param enemy: The Enemy instance that was hit.
        """
        enemy.take_damage(bullet.damage)  # Assuming `take_damage()` exists in the Enemy class
        bullet.destroy()  # Assuming bullets have a `destroy()` method

    def _handle_player_enemy_collision(self, enemy):
        """
        Handle the event where the player collides with an enemy.

        :param enemy: The Enemy instance that collided with the player.
        """
        #self.player.take_damage(enemy.collision_damage)  # Assuming `collision_damage` attribute
        #enemy.handle_collision_with_player()  # Optional behavior for enemy
        pass

    def _handle_player_element_collision(self, element):
        """
        Handle the event where the player collides with a moving element.

        :param element: The MovingElement instance that collided with the player.
        """
        # Example: Reduce player's life, or trigger a specific effect
        # self.player.take_damage(element.collision_damage)
        pass
    
    def move_entities_and_handle_world_collisions(self, world):
        """
        Move all entities and handle their collisions with the world.

        :param world: The World instance to check for collisions.
        """
        # Move player and check collisions
        self._move_entity_and_handle_collision(self.player, world)

        # Move player bullets
        for bullet in self.player_bullets:
            self._move_entity_and_handle_collision(bullet, world)

        # Move enemies
        for enemy in self.enemies:
            self._move_entity_and_handle_collision(enemy, world)

        # Move enemy bullets
        for bullet in self.enemy_bullets:  # Added handling for enemy bullets
            self._move_entity_and_handle_collision(bullet, world)

        # Move other moving elements
        for element in self.moving_elements:
            self._move_entity_and_handle_collision(element, world)

    def _move_entity_and_handle_collision(self, entity, world):
        """
        Move a single entity and handle its collisions with the world.

        :param entity: The entity to move (e.g., Player, Bullet, Enemy, MovingElement).
        :param world: The World instance to check for collisions.
        """

        # Get nearby blocks that may collide with the entity
        collision_blocks = world.get_collision_blocks_around(entity.rect.center, entity.rect.size)

        # Move the entity
        entity.move(collision_blocks)
