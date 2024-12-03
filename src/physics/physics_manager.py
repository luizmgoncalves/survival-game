import commons
from .player import Player
from .enemy import Enemy
from .bullet import Bullet
from .moving_element import MovingElement, CollidableMovingElement
from .item import Item
from typing import List
from math import ceil
from random import random
from pygame.math import Vector2 as v2

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
        self.gravity: int = commons.GRAVITY_ACELERATION
    
    def spawn_item(self, item_id, pos):
        r_angle = -180 * random()
        init_vel = v2.from_polar((commons.ITEM_INITIAL_VELOCITY, r_angle))

        new_item = Item(item_id,pos, init_vel)
        
        self.moving_elements.append(new_item)
    
    def get_renderable_elements(self):
        return self.moving_elements


    def update(self, delta_time, world):
        """
        Update the state of all managed elements.
        
        :param delta_time: Time elapsed since the last update (in seconds).
        """
        
        self.apply_gravity(delta_time)
        self.move_entities_and_handle_world_collisions(world, delta_time)
        self.handle_collisions()

        # Update player
        if self.player:
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
    
    def apply_gravity(self, delta_time):
        """
        Apply gravity to all entities affected by physics.
        """
        # Apply gravity to the player
        if self.player:
            self._apply_gravity_to_entity(self.player, delta_time)

        # Apply gravity to enemies
        for enemy in self.enemies:
            self._apply_gravity_to_entity(enemy, delta_time)

        # Apply gravity to moving elements
        for element in self.moving_elements:
            self._apply_gravity_to_entity(element, delta_time)
        
    def _apply_gravity_to_entity(self, entity: MovingElement, delta_time):
        """
        Apply gravity to a single entity.

        :param entity: The entity to which gravity will be applied.
        """
        if entity.does_fall:
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
            if self.player and self.player.rect.colliderect(enemy.rect):
                self._handle_player_enemy_collision(enemy)

        # Check collisions between player and moving elements (optional)
        for element in self.moving_elements:
            if self.player and self.player.rect.colliderect(element.rect):
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
    
    def move_entities_and_handle_world_collisions(self, world, delta_time):
        """
        Move all entities and handle their collisions with the world.

        :param world: The World instance to check for collisions.
        """
        # Move player and check collisions
        if self.player:
            self._move_entity_and_handle_collision(self.player, world, delta_time)

        # Move player bullets
        for bullet in self.player_bullets:
            self._move_entity_and_handle_collision(bullet, world, delta_time)

        # Move enemies
        for enemy in self.enemies:
            self._move_entity_and_handle_collision(enemy, world, delta_time)

        # Move enemy bullets
        for bullet in self.enemy_bullets:  # Added handling for enemy bullets
            self._move_entity_and_handle_collision(bullet, world, delta_time)

        # Move other moving elements
        for element in self.moving_elements:
            self._move_entity_and_handle_collision(element, world, delta_time)

    def _move_entity_and_handle_collision(self, entity: MovingElement, world, delta_time):
        """
        Move a single entity and handle its collisions with the world.

        :param entity: The entity to move (e.g., Player, Bullet, Enemy, MovingElement).
        :param world: The World instance to check for collisions.
        """

        # Get nearby blocks that may collide with the entity
        x_dist = abs(ceil(entity.velocity.x * delta_time)) + entity.rect.width
        y_dist = abs(ceil(entity.velocity.y * delta_time)) + entity.rect.height
        collision_blocks = world.get_collision_blocks_around(entity.rect.center, (x_dist, y_dist))

        # Move the entity
        entity.move(collision_blocks, delta_time)
