import commons
from .player import Player
from .enemy import Enemy
from .bullet import Bullet
from .moving_element import MovingElement, CollidableMovingElement
from .bullet import Arrow, Axe
from .enemy import Enemy
from .enemy import EnemyManager
from .item import Item
from typing import List
from math import ceil
from random import random
from pygame.math import Vector2 as v2
import pygame

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
        
        self.moving_elements: List[MovingElement] = moving_elements 
        self.itens: List[Item] = []
        self.enemy_bullets: List[Bullet] = enemy_bullets 
        self.enemy_manager = EnemyManager(5)
        self.enemies: List[Enemy] = self.enemy_manager.enemies
        self.gravity: int = commons.GRAVITY_ACELERATION
        self.terminal_speed = commons.TERMINAL_SPEED
    
    def enemy_throw(self, throwable: str, pos: v2):
        if not self.player:
            return
        
        dif = self.player.position - v2(0, abs(self.player.position.x-pos[0])/2) - pos

        _, angle = dif.as_polar()

        angle += (random() - 0.5)*40

        init_vel = v2.from_polar((commons.BULLET_INITIAL_VELOCITY, angle))

        match throwable:
            case "AXE":
                new_bullet = Axe(pos, init_vel)
            case "ARROW":
                new_bullet = Arrow(pos, init_vel)
            case _:
                return
            
        self.enemy_bullets.append(new_bullet)
    
    def spawn_item(self, item_id, pos):
        r_angle = -180 * random()
        init_vel = v2.from_polar((commons.ITEM_INITIAL_VELOCITY, r_angle))

        new_item = Item(item_id,pos, init_vel)
        
        self.moving_elements.append(new_item)
        self.itens.append(new_item)
    
    def get_renderable_elements(self):
        return self.moving_elements + [self.player] + self.player_bullets + self.enemy_bullets + self.enemies


    def update(self, delta_time, world):
        """
        Update the state of all managed elements.
        
        :param delta_time: Time elapsed since the last update (in seconds).
        """
        self.enemy_manager.update(delta_time, self.player)
        self.apply_gravity(delta_time)
        self.apply_player_attraction_force()
        self.move_entities_and_handle_world_collisions(world, delta_time)
        self.apply_friction()
        self.handle_collisions()

        # Update player
        if self.player:
            self.player.update(delta_time)
            if not self.player.is_alive() and not self.player.dying:
                self.player.respawn()
                pygame.event.post(pygame.event.Event(commons.RENDER_MANAGER_INIT))


        # Update player bullets
        for bullet in self.player_bullets:
            bullet.update(delta_time)
            if not bullet.is_alive():
                self.player_bullets.remove(bullet)

        # Update enemies bullets
        for bullet in self.enemy_bullets:
            bullet.update(delta_time)
            if not bullet.is_alive():
                self.enemy_bullets.remove(bullet)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(delta_time)
            if not enemy.is_alive() and not enemy.dying:
                self.player.kills += 1
                self.enemies.remove(enemy)

        # Update other moving elements
        for element in self.moving_elements:
            element.update(delta_time)
            if hasattr(element, "is_alive") and not element.is_alive():
                self.moving_elements.remove(element)
    
    def apply_friction(self):
        # Update player
        if self.player:
            if self.player.is_falling:
                self.player.velocity.x *= 0.97  # Apply lower friction when falling
            else:
                self.player.velocity.x *= 0.6  # Apply higher friction when on terrain

        # Update player bullets
        for bullet in self.player_bullets:
            # Bullets in motion typically experience minimal friction, if any
            bullet.velocity.x *= 0.99
            bullet.velocity.y *= 0.99  # Optional: Apply slight air resistance

        # Update enemy bullets
        for bullet in self.enemy_bullets:
            # Similar to player bullets, apply minimal friction
            bullet.velocity.x *= 0.99
            bullet.velocity.y *= 0.99

        # Update enemies
        for enemy in self.enemies:
            if enemy.is_falling:
                enemy.velocity.x *= 0.95  # Slightly reduce friction when falling
            else:
                enemy.velocity.x *= 0.6 # Apply more significant friction on the ground

        # Update other moving elements
        for element in self.moving_elements:
            if hasattr(element, 'is_falling') and element.is_falling:
                element.velocity.x *= 0.95  # Reduced friction for falling elements
            else:
                element.velocity.x *= 0.85  # Normal friction for grounded elements
    
    def apply_player_attraction_force(self):
        if not self.player:
            return
        
        for i in range(len(self.itens)):
            dif = self.player.position - self.itens[i].position
            if dif.length() <= commons.MAX_DISTANCE_OF_ITEM_ATTRACTION and dif.length() > 0:
                self.itens[i].velocity += dif.normalize() * commons.ITEM_ATTRACTION_FORCE
    
    def apply_gravity(self, delta_time):
        """
        Apply gravity to all entities affected by physics.
        """
        # Apply gravity to the player
        if self.player:
            self._apply_gravity_to_entity(self.player, delta_time)

        for bullet in self.player_bullets:
            self._apply_gravity_to_entity(bullet, delta_time)
        
        for bullet in self.enemy_bullets:
            self._apply_gravity_to_entity(bullet, delta_time)

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
        
        if entity.velocity.magnitude() > self.terminal_speed:
            entity.velocity.scale_to_length(self.terminal_speed)

    def handle_collisions(self):
        """
        Handle collisions between entities (e.g., player and enemies, bullets and enemies).
        """
        # Check collisions between player bullets and enemies
        for bullet in self.player_bullets:
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):  # Assuming entities have a `rect` attribute for collision
                    self._handle_bullet_hit_enemy(bullet, enemy)
        
        for bullet in self.enemy_bullets:
            if not self.player:
                break
            
            if self.player.rect.colliderect(bullet.rect):
                self.player.take_damage(bullet.damage, 'left' if self.player.rect.x < bullet.rect.x else 'right')
                bullet.collided_down()


        # Check collisions between player and enemies
        for enemy in self.enemies:
            if not self.player:
                break

            if self.player.rect.colliderect(enemy.rect) and enemy.is_alive():
                self.player.take_damage(5, 'left' if self.player.rect.x < enemy.rect.x else 'right')

            if enemy.attacking and self.player.rect.colliderect(enemy.attack_area):
                self.player.take_damage(20, 'left' if self.player.rect.x < enemy.attack_area.x else 'right')
            
            if self.player.attacking and enemy.rect.colliderect(self.player.attack_area):
                enemy.take_damage(20, 'left' if self.player.attack_area.x > enemy.rect.x else 'right')
        
        # Check collisions between player and itens (optional)
        for iten in self.itens:
            if self.player and self.player.rect.colliderect(iten.rect):
                self._handle_player_iten_collision(iten)

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
    
    def _handle_player_iten_collision(self, iten: Item):
        """
        Handle the event where the player collides with a moving element.

        :param element: The Item instance that collided with the player.
        """
        # Example: Reduce player's life, or trigger a specific effect
        # self.player.take_damage(element.collision_damage)

        if self.player.collect(iten.id):
            pygame.event.post(pygame.event.Event(commons.ITEM_COLLECT_EVENT, {'item': iten.id}))
            self.itens.remove(iten)
            self.moving_elements.remove(iten)

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
