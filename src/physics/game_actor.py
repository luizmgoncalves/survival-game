import pygame
from itertools import cycle
from .moving_element import CollidableMovingElement
from rendering.animation import Animation
from pygame.math import Vector2 as v2
from pygame.rect import Rect
from images.image_loader import IMAGE_LOADER
from typing import List

class GameActor(CollidableMovingElement):
    def __init__(self, pos: v2, size: v2, life: float, max_vel: float, jump_strength: float,
                 walk_right: Animation = None, walk_left: Animation = None,
                 run_right: Animation = None, run_left: Animation = None,
                 idle_right: Animation = None, idle_left: Animation = None,
                 jump_right: Animation = None, jump_left: Animation = None,
                 attack_right: Animation = None, attack_left: Animation = None,
                 dying_right: Animation = None, dying_left: Animation = None):
        super().__init__(pos, size)
        self.jumping      : bool  = False
        self.facing_left  : bool  = False
        self.life         : float = life
        self.attacking    : bool  = False
        self.dying        : bool = False
        self.dying_time = 0.0
        self.dying_duration = 2.0  # 1 second of invulnerability

        self.attack_area  : Rect  = pygame.Rect(0, 0, size[0] * 1.5, size[1])
        self.attack_time  : float = 0
        self.max_vel      : float = max_vel
        self.jump_strength: float = jump_strength

        # Animations
        self.walk_anim_right : Animation = walk_right
        self.run_anim_right  : Animation = run_right
        self.idle_anim_right : Animation = idle_right
        self.jump_anim_right : Animation = jump_right
        self.attack_anim_right : Animation = attack_right
        self.dying_anim_right: Animation = dying_right

        self.walk_anim_left  : Animation = walk_left
        self.run_anim_left   : Animation = run_left
        self.idle_anim_left  : Animation = idle_left
        self.jump_anim_left  : Animation = jump_left
        self.attack_anim_left : Animation = attack_left
        self.dying_anim_left: Animation = dying_left

        # Default animation
        self._current_anim   : Animation = self.idle_anim_right

        # Set the image based on the current animation or default to None
        self.image : str = self._current_anim.get_current_frame()

        # State variables
        self.w_left  = False
        self.w_right = False
        self.running = False

        # Invulnerability state
        self.invulnerable = False
        self.invulnerability_time = 0.0
        self.invulnerability_duration = 1.0  # 1 second of invulnerability

        self.attack_cooldown: float = 1.0  # Cooldown time in seconds
        self.time_since_last_attack: float = 0.0  # Time since the last attack
    
    def move(self, colliding_rects: List[pygame.Rect], delta_time: float):
        if not self.dying:
            super().move(colliding_rects, delta_time)

    @property
    def current_animation(self) -> Animation:
        """
        Getter for the current animation.

        :return: The current animation object.
        """
        return self._current_anim

    @current_animation.setter
    def current_animation(self, new_anim: Animation):
        """
        Setter for the current animation. Resets the new animation if it's different.

        :param new_anim: The new animation to set.
        """
        if self._current_anim is not new_anim and new_anim:
            self._current_anim = new_anim
            self._current_anim.reset()

    def update(self, delta_time: float):
        if abs(self.velocity.x) < 30:  # Threshold for stopping
            self.stop_moving()

        if self.time_since_last_attack < self.attack_cooldown:
            self.time_since_last_attack += delta_time

        # Handle attack timing
        if self.attacking:
            self.attack_time -= delta_time
            if self.attack_time <= 0:
                self.attacking = False
        
        # Handle invulnerability timer
        if self.invulnerable:
            self.invulnerability_time -= delta_time
            if self.invulnerability_time <= 0:
                self.invulnerable = False

        # If the actor is dying, play the dying animation
        if self.dying:
            self.dying_time -= delta_time
            self.current_animation = self.dying_anim_left if self.facing_left else self.dying_anim_right
            if self.current_animation:
                self.current_animation.update(delta_time)
                self.image = self.current_animation.get_current_frame()

                # Check if the dying animation is completed
            if self.dying_time <= 0:
                self.dying = False
            return  # Skip further updates while dying


        # Update attack area position
        if self.facing_left:
            self.attack_area.midright = self.rect.midleft
        else:
            self.attack_area.midleft = self.rect.midright


        # Choose the correct animation based on state
        if self.attacking:
            self.current_animation = self.attack_anim_left if self.facing_left else self.attack_anim_right
        elif self.jumping:
            self.current_animation = self.jump_anim_left if self.facing_left else self.jump_anim_right
        elif self.w_left or self.w_right:
            if self.running:
                self.current_animation = self.run_anim_left if self.facing_left else self.run_anim_right
            else:
                self.current_animation = self.walk_anim_left if self.facing_left else self.walk_anim_right
        else:
            self.current_animation = self.idle_anim_left if self.facing_left else self.idle_anim_right

        # Update the current animation
        if self.current_animation:
            self.current_animation.update(delta_time)
            self.image = self.current_animation.get_current_frame()

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
        if self.is_falling:
            self.velocity.x = max(-self.max_vel / 2, self.velocity.x - self.max_vel / 20)
        else:
            self.velocity.x = -self.max_vel / 2
        self.facing_left = True
        self.w_left = True
        self.w_right = False

    def walk_right(self):
        """
        Move the actor to the right by setting horizontal velocity.

        :return: None
        """
        if self.is_falling:
            self.velocity.x = min(self.max_vel / 2, self.velocity.x + self.max_vel / 20)
        else:
            self.velocity.x = self.max_vel / 2
        self.facing_left = False
        self.w_right = True
        self.w_left = False

    def run_left(self):
        """
        Make the actor run to the left by increasing horizontal velocity.

        :return: None
        """
        self.velocity.x = -self.max_vel
        self.facing_left = True
        self.w_left = True
        self.w_right = False
        self.running = True

    def run_right(self):
        """
        Make the actor run to the right by increasing horizontal velocity.

        :return: None
        """
        self.velocity.x = self.max_vel
        self.facing_left = False
        self.w_right = True
        self.w_left = False
        self.running = True

    def stop_moving(self):
        """
        Stop the actor's horizontal movement.

        :return: None
        """
        self.velocity.x = 0
        self.w_left = False
        self.w_right = False
        self.running = False

    def attack(self):
        """
        Start an attack action by setting the attack state.

        :return: None
        """
        if not self.attacking and self.time_since_last_attack >= self.attack_cooldown:
            self.attacking = True
            self.attack_time = 0.3  # Attack lasts for 0.3 seconds by default
            self.time_since_last_attack = 0.0  # Reset the cooldown timer
            
            # Define the attack area if necessary (position can depend on facing direction)
            self.attack_area = pygame.Rect(self.rect.centerx, self.rect.centery, 50, 30)
            if self.facing_left:
                self.attack_area = pygame.Rect(self.rect.centerx - 50, self.rect.centery, 50, 30)
            
            return True
        
        return False

    def take_damage(self, amount, direction='left'):
        """
        Reduce the actor's life by a given amount, if not invulnerable.

        :param amount: The damage amount to apply.
        """
        if not self.invulnerable:
            self.life -= amount
            if self.life <= 0:
                self.life = 0
                self.die()  # Trigger dying state

            # Trigger invulnerability
            self.invulnerable = True
            self.invulnerability_time = self.invulnerability_duration

            if direction == 'left':
                self.velocity.x = -700 * amount/30
                self.velocity.y = -500 * amount/30
            else:
                self.velocity.x = 700 * amount/30
                self.velocity.y = -500 * amount/30

    def die(self):
        """
        Transition to the dying state.

        :return: None
        """
        if not self.dying:
            self.dying = True
            self.dying_time = self.dying_duration
            self.velocity.x = 0  # Stop movement
            self.velocity.y = 0
            self.current_animation = self.dying_anim_left if self.facing_left else self.dying_anim_right
            if self.current_animation:
                self.current_animation.reset()

    def is_alive(self):
        """
        Check if the actor is still alive.

        :return: True if the actor's life is greater than zero, False otherwise.
        """
        return self.life > 0 and not self.dying
