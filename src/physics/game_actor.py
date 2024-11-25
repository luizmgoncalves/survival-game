import pygame
from itertools import cycle
from moving_element import CollidableMovingElement

class GameActor(CollidableMovingElement):
    """
    A class representing an actor in the game, such as a player or enemy.

    Attributes:
        facing_left (bool): Direction the actor is facing (True for left, False for right).
        walking_sprites_right (list[pygame.Surface]): Sprites for walking animations when facing right.
        running_sprites_right (list[pygame.Surface]): Sprites for running animations when facing right.
        idle_sprites_right (list[pygame.Surface]): Sprites for idle animations when facing right.
        jumping_sprites_right (list[pygame.Surface]): Sprites for jumping animations when facing right.
        walking_sprites_left (list[pygame.Surface]): Sprites for walking animations when facing left.
        running_sprites_left (list[pygame.Surface]): Sprites for running animations when facing left.
        idle_sprites_left (list[pygame.Surface]): Sprites for idle animations when facing left.
        jumping_sprites_left (list[pygame.Surface]): Sprites for jumping animations when facing left.
        life (float): The current life points of the actor.
        attacking (bool): Whether the actor is currently attacking.
        attack_area (pygame.Rect): The area of effect for the attack.
        attack_time (float): The duration of the attack.
        max_vel (float): The maximum velocity of the actor.
        velocity (pygame.math.Vector2): The actor's velocity, used for movement and jumping.
    """
    def __init__(self, position, size, life, max_vel, walking_sprites_right, running_sprites_right, idle_sprites_right, jumping_sprites_right):
        """
        Initialize a GameActor.

        :param position: A tuple (x, y) representing the starting position.
        :param size: A tuple (width, height) representing the actor's size.
        :param life: The initial life points of the actor.
        :param max_vel: The maximum velocity of the actor.
        :param walking_sprites_right: A list of sprites for walking animations when facing right.
        :param running_sprites_right: A list of sprites for running animations when facing right.
        :param idle_sprites_right: A list of sprites for idle animations when facing right.
        :param jumping_sprites_right: A list of sprites for jumping animations when facing right.
        """
        super().__init__(position, size)
        self.jumping = False
        self.facing_left = False  # False means facing right
        self.walking_sprites_right = cycle(walking_sprites_right)
        self.running_sprites_right = cycle(running_sprites_right)
        self.idle_sprites_right = cycle(idle_sprites_right)
        self.jumping_sprites_right = cycle(jumping_sprites_right)

        # Create left-facing sprite lists by flipping right-facing ones
        self.walking_sprites_left = cycle([pygame.transform.flip(sprite, True, False) for sprite in walking_sprites_right])
        self.running_sprites_left = cycle([pygame.transform.flip(sprite, True, False) for sprite in running_sprites_right])
        self.idle_sprites_left = cycle([pygame.transform.flip(sprite, True, False) for sprite in idle_sprites_right])
        self.jumping_sprites_left = cycle([pygame.transform.flip(sprite, True, False) for sprite in jumping_sprites_right])

        self.life = life
        self.attacking = False
        self.attack_area = pygame.Rect(0, 0, size[0] * 1.5, size[1])  # Example: 1.5x size
        self.attack_time = 0
        self.max_vel = max_vel
        self.jump_strength = 200  # Optional: you can adjust this if you want to tweak the jump height

        # Current sprite
        self.image = next(self.idle_sprites_right)  # Default to idle right
        self.animation_timer = 0  # Timer for switching animations
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.velocity = pygame.math.Vector2(0, 0)  # Add velocity for jump mechanics

    def update(self, delta_time):
        """
        Update the actor's position, animations, and attack state.

        :param delta_time: The time step for the update.
        """

        # Handle attack timing
        if self.attacking:
            self.attack_time -= delta_time
            if self.attack_time <= 0:
                self.attacking = False

        # Update attack area position
        if self.facing_left:
            self.attack_area.midright = self.rect.midleft
        else:
            self.attack_area.midleft = self.rect.midright

        # Update animation
        self.animation_timer += delta_time
        if self.animation_timer >= 0.1:  # Change frame every 0.1 seconds
            if self.jumping:  # Jumping
                self.image = next(self.jumping_sprites_right) if not self.facing_left else next(self.jumping_sprites_left)
            elif abs(self.velocity.x) > 0.1:  # Moving (walking/running)
                if abs(self.velocity.x) > self.max_vel / 2:  # Running
                    self.image = next(self.running_sprites_right) if not self.facing_left else next(self.running_sprites_left)
                else:  # Walking
                    self.image = next(self.walking_sprites_right) if not self.facing_left else next(self.walking_sprites_left)
            else:  # Idle
                self.image = next(self.idle_sprites_right) if not self.facing_left else next(self.idle_sprites_left)

            self.animation_timer = 0

    def jump(self):
        """
        Make the actor jump by applying a vertical velocity.

        :return: None
        """
        if not self.jumping:
            self.jumping = True
            self.velocity.y = -self.jump_strength
    
    def collided_down(self):
        """
        Handle the collision when the object collides from below.
        
        :param rect: The rect the object collided with.
        """
        super().collided_down()
        self.jumping = False

    def walk_left(self):
        """
        Move the actor to the left by setting horizontal velocity.

        :return: None
        """
        self.velocity.x = -self.max_vel / 2
        self.facing_left = True

    def walk_right(self):
        """
        Move the actor to the right by setting horizontal velocity.

        :return: None
        """
        self.velocity.x = self.max_vel / 2
        self.facing_left = False

    def run_left(self):
        """
        Make the actor run to the left by increasing horizontal velocity.

        :return: None
        """
        self.velocity.x = -self.max_vel
        self.facing_left = True

    def run_right(self):
        """
        Make the actor run to the right by increasing horizontal velocity.

        :return: None
        """
        self.velocity.x = self.max_vel
        self.facing_left = False

    def attack(self):
        """
        Start an attack action by setting the attack state.

        :return: None
        """
        if not self.attacking:
            self.attacking = True
            self.attack_time = 0.5  # Attack lasts for 0.5 seconds by default
            # Define the attack area if necessary (position can depend on facing direction)
            self.attack_area = pygame.Rect(self.rect.centerx, self.rect.centery, 50, 30)
            if self.facing_left:
                self.attack_area = pygame.Rect(self.rect.centerx - 50, self.rect.centery, 50, 30)

    def take_damage(self, amount):
        """
        Reduce the actor's life by a given amount.

        :param amount: The damage amount to apply.
        """
        self.life -= amount
        if self.life <= 0:
            self.kill()  # Remove the sprite from the game

    def is_alive(self):
        """
        Check if the actor is still alive.

        :return: True if the actor's life is greater than zero, False otherwise.
        """
        return self.life > 0
