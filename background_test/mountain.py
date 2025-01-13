import pygame

class Mountain:
    def __init__(self, image_path, width, height, y_position, speed):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.width = width
        self.height = height
        self.y_position = y_position
        self.speed = speed
        self.pos_x = 0

    def update(self, direction):
        if direction == "left":
            self.pos_x += self.speed
        elif direction == "right":
            self.pos_x -= self.speed
        self.pos_x %= self.width

    def draw(self, screen):
        screen.blit(self.image, (self.pos_x - self.width, self.y_position))
        screen.blit(self.image, (self.pos_x, self.y_position))
