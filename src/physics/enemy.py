import random
import json
import pygame
import commons
from rendering.animation import Animation
from pygame.math import Vector2 as v2
from .game_actor import GameActor
from images.image_loader import ImageLoader  # Importando o ImageLoader

class EnemyManager:
    def __init__(self, spawn_interval=5):
        self.enemies = []  # Lista de inimigos ativos
        self.spawn_interval = spawn_interval  # Intervalo para gerar novos inimigos (em segundos)
        self.last_spawn_time = 0  # Tempo de última geração de inimigos
        
        
        # Carregar os dados do JSON
        with open('assets/metadata/enemies_metadata.json') as f:
            self.enemies_data = json.load(f)

        self.enemy_types = list(self.enemies_data['ENEMIES'].keys())

        # Instância do ImageLoader
        self.image_loader = ImageLoader()

    def update(self, dt, player):
        # Atualiza o temporizador para criação de novos inimigos
        self.last_spawn_time += dt
        if self.last_spawn_time > self.spawn_interval:
            self.enemies.append(self.spawn_enemy())  # Cria um novo inimigo
            self.last_spawn_time = 0  # Reinicia o contador de tempo

        # Atualiza todos os inimigos existentes
        for enemy in self.enemies:
            enemy.update_ai(player)

        # Remove inimigos mortos
        #self.enemies = [enemy for enemy in self.enemies if not enemy.is_alive()]

    def spawn_enemy(self):
        """
        Spawn an enemy using data from the enemies_data dictionary.
        """
        # Randomly choose an enemy type
        enemy_name = random.choice(self.enemy_types)
        enemy_data = self.enemies_data["ENEMIES"][enemy_name]
        spr_num_data = enemy_data['num_sprites']

        # Create animations
        w_right = Animation([f"{enemy_name}.WALKING{i}" for i in range(spr_num_data['walking'])], 0.1, False)
        w_left = Animation([f"{enemy_name}.WALKING{i}.FLIPED_X" for i in range(spr_num_data['walking'])], 0.1, False)

        idle_right = Animation([f"{enemy_name}.IDLE{i}" for i in range(spr_num_data['idle'])], 0.5, False)
        idle_left = Animation([f"{enemy_name}.IDLE{i}.FLIPED_X" for i in range(spr_num_data['idle'])], 0.5, False)

        attack_right = Animation([f"{enemy_name}.ATTACKING{i}" for i in range(spr_num_data['attacking'])], 0.07, True)
        attack_left = Animation([f"{enemy_name}.ATTACKING{i}.FLIPED_X" for i in range(spr_num_data['attacking'])], 0.07, True)

        dying_right = Animation([f"{enemy_name}.DYING{i}" for i in range(spr_num_data['dying'])], 0.07, True)
        dying_left = Animation([f"{enemy_name}.DYING{i}.FLIPED_X" for i in range(spr_num_data['dying'])], 0.07, True)

        # Enemy attributes
        position = (random.randint(0, 800), random.randint(0, 600))  # Example random position
        size = (enemy_data['width'], enemy_data['height'])
        life = enemy_data['life']
        max_vel = enemy_data['max_vel']
        attack_range = enemy_data['attack_range']
        attack_damage = enemy_data['attack_damage']

        # Create the new enemy
        new_enemy = Enemy(
            pos=position,
            size=size,
            life=life,
            max_vel=max_vel,
            attack_range=attack_range,
            attack_damage=attack_damage,
            walk_right=w_right,
            walk_left=w_left,
            idle_right=idle_right,
            idle_left=idle_left,
            attack_right=attack_right,
            attack_left=attack_left,
            dying_right=dying_right,
            dying_left=dying_left,
        )

        # Add the new enemy to the enemies list
        self.enemies.append(new_enemy)
        return new_enemy

ENEMY_MANAGER = EnemyManager()

class Enemy(GameActor):
    def __init__(self, pos: v2, size: v2, life: float, max_vel: float, attack_range: float = 100, 
                 attack_damage: float = 10, walk_right: Animation = None, walk_left: Animation = None, 
                 idle_right: Animation = None, idle_left: Animation = None, 
                 attack_right: Animation = None, attack_left: Animation = None, 
                 dying_right: Animation = None, dying_left: Animation = None):
        """
        Initialize an Enemy instance.

        :param pos: Initial position of the enemy (x, y).
        :param size: Size of the enemy (width, height).
        :param life: Health points of the enemy.
        :param max_vel: Maximum velocity of the enemy.
        :param attack_range: The range within which the enemy can attack.
        :param attack_damage: Damage inflicted by the enemy's attack.
        """
        super().__init__(pos, size, life, max_vel, jump_strength=commons.DEFAULT_JUMP_STRENGHT,
                         walk_right=walk_right, walk_left=walk_left,
                         idle_right=idle_right, idle_left=idle_left,
                         attack_right=attack_right, attack_left=attack_left,
                         dying_right=dying_right, dying_left=dying_left)
        self.attack_range: float = attack_range
        self.attack_damage: float = attack_damage

    def update_ai(self, player):
        """
        Update the enemy's behavior and animation.

        :param player: The player instance to interact with.
        :param delta_time: Time elapsed since the last update.
        """
        if self.is_alive():
            # Move toward the player if not in attack range
            if self.distance_to_player(player) > self.attack_range:
                self.move_towards_player(player)
            else:
                # Attack the player if in range and not already attacking
                if not self.attacking:
                    self.attack()

    def distance_to_player(self, player) -> float:
        """
        Calculate the distance to the player.

        :param player: The player instance.
        :return: Euclidean distance to the player.
        """
        return ((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2) ** 0.5

    def move_towards_player(self, player):
        """
        Move the enemy toward the player.

        :param player: The player instance.
        """
        if player.rect.centerx < self.rect.centerx:
            self.walk_left()
        else:
            self.walk_right()

    def attack(self):
        """
        Start an attack action. Deals damage to the player if within range.
        """
        super().attack()
        # Additional logic to deal damage to the player can be added here.

    def die(self):
        """
        Transition to the dying state and perform additional logic if needed.
        """
        super().die()
        # Add any additional cleanup or effects for the enemy death here.

