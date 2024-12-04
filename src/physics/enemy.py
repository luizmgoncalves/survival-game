import random
import json
import pygame
from .game_actor import GameActor
from images.image_loader import ImageLoader  # Importando o ImageLoader

class EnemyManager:
    def __init__(self, spawn_interval=5):
        self.enemies = []  # Lista de inimigos ativos
        self.spawn_interval = spawn_interval  # Intervalo para gerar novos inimigos (em segundos)
        self.last_spawn_time = 0  # Tempo de última geração de inimigos
        self.enemy_types = ["spear_enemy", "arrow_enemy", "axe_enemy", "viking_enemy"]
        
        # Carregar os dados do JSON
        with open('assets/metadata/images_metadata.json') as f:
            self.animations_data = json.load(f)["ENEMIES"]

        # Instância do ImageLoader
        self.image_loader = ImageLoader()

    def update(self, dt, player):
        # Atualiza o temporizador para criação de novos inimigos
        self.last_spawn_time += dt
        if self.last_spawn_time > self.spawn_interval:
            self.spawn_enemy()  # Cria um novo inimigo
            self.last_spawn_time = 0  # Reinicia o contador de tempo

        # Atualiza todos os inimigos existentes
        for enemy in self.enemies:
            enemy.update(player, dt)

        # Remove inimigos mortos
        self.enemies = [enemy for enemy in self.enemies if not enemy.is_dead]

    def spawn_enemy(self):
        # Escolhe aleatoriamente um inimigo para criar
        enemy_name = random.choice(self.enemy_types)
        enemy_data = self.animations_data[enemy_name]
        frames = enemy_data["animations"]

        # Define o dano e o dano necessário para morrer de acordo com o tipo de inimigo
        if enemy_name == "spear_enemy":
            damage = 10
            damage_to_die = 50
        elif enemy_name == "arrow_enemy":
            damage = 15
            damage_to_die = 80
        elif enemy_name == "axe_enemy":
            damage = 25
            damage_to_die = 120
        elif enemy_name == "viking_enemy":
            damage = 20
            damage_to_die = 150

        # Criação do inimigo com dados aleatórios
        new_enemy = Enemy(
            name=enemy_name,
            x=random.randint(100, 800),  # Posição aleatória no eixo X
            y=random.randint(100, 600),  # Posição aleatória no eixo Y
            health=100,
            damage=damage,
            frames=frames,
            damage_to_die=damage_to_die  # Dano necessário para iniciar a animação de morte
        )
        self.enemies.append(new_enemy)  # Adiciona o novo inimigo à lista

    def draw(self, screen):
        # Desenha todos os inimigos na tela
        for enemy in self.enemies:
            enemy.draw(screen)

class Enemy(GameActor):
    def __init__(self, name, x, y, health, damage, frames, attack_range=100, attack_damage=10, damage_to_die=50):
        super().__init__(x, y, health)
        self.name = name
        self.damage = damage
        self.attack_range = attack_range
        self.attack_damage = attack_damage
        self.damage_to_die = damage_to_die  # Quantidade de dano para iniciar a animação de morte

        # As animações serão passadas por frames (como do json)
        self.frames = frames
        self.current_frame_index = 0
        self.animation_timer = 0
        self.is_attacking = False
        self.is_dying = False
        self.is_dead = False  # Para verificar se o inimigo está morto

        # Variáveis para animações
        self.current_animation = "walking"
        self.walking_direction = "right"  # O movimento é sempre da esquerda para a direita
        self.image_loader = ImageLoader()  # Instância do ImageLoader
    
    def update(self, player, dt):
        # Atualiza o movimento e animação do inimigo
        if not self.is_dead:
            self.move_towards_player(player)
            self.animate(dt)

            # Se a distância do player for suficiente, inicia o ataque
            if self.distance_to_player(player) < self.attack_range and not self.is_attacking:
                self.is_attacking = True
                self.attack(player)

            # Se a saúde do inimigo for zero ou abaixo, inicia a animação de morte
            if self.health <= 0 and not self.is_dying:
                self.is_dying = True
                self.animate_dying()

    def distance_to_player(self, player):
        # Calcula a distância entre o inimigo e o jogador
        return ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5

    def move_towards_player(self, player):
        # O inimigo começa a andar para o player se a distância for maior que o alcance de ataque
        if not self.is_dying and not self.is_attacking:
            if self.distance_to_player(player) > self.attack_range:
                if self.walking_direction == "right":
                    self.x += 2  # Ajuste a velocidade do movimento
                else:
                    self.x -= 2

    def attack(self, player):
        # Aplica dano ao jogador
        player.health -= self.attack_damage

    def animate(self, dt):
        if self.is_attacking:
            self.play_attack_animation(dt)
        elif self.is_dying:
            self.play_dying_animation(dt)
        else:
            self.play_walking_animation(dt)

    def play_walking_animation(self, dt):
        if self.distance_to_player(None) > self.attack_range:  # Só anima se o inimigo não estiver atacando
            walking_frames = self.frames.get("walking", {}).get("frames", [])
            self.play_animation(walking_frames, dt)

    def play_attack_animation(self, dt):
        # Joga a animação de ataque
        attacking_frames = self.frames.get("attacking", {}).get("frames", [])
        self.play_animation(attacking_frames, dt)

    def play_dying_animation(self, dt):
        # Joga a animação de morte
        dying_frames = self.frames.get("dying", {}).get("frames", [])
        self.play_animation(dying_frames, dt)

    def play_animation(self, frames, dt):
        if frames:
            self.animation_timer += dt
            if self.animation_timer > 0.1:  # Ajuste o tempo entre os frames
                self.animation_timer = 0
                self.current_frame_index += 1

                if self.current_frame_index >= len(frames):
                    self.current_frame_index = 0  # Volta ao primeiro frame

                frame = frames[self.current_frame_index]
                image = self.image_loader.load_image(frame['path'])  # Usando o ImageLoader para carregar a imagem
                if image:
                    self.image = image
                    self.rect = self.image.get_rect(topleft=(self.x, self.y))

                # Se o inimigo acabou de morrer (animação de morte completada)
                if self.is_dying and self.current_frame_index == len(dying_frames) - 1:
                    self.is_dead = True
                    self.remove_enemy()  # Método para remover o inimigo do jogo

    def remove_enemy(self):
        # Remove o inimigo do jogo (pode ser implementado de acordo com a lógica do jogo)
        print(f"{self.name} foi removido do jogo após morrer.")
        # Aqui, você pode removê-lo da lista de inimigos ou da cena, dependendo do seu sistema.
