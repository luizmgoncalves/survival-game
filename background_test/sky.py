import pygame

class Sky:
    def __init__(self, image_path, width, height, speed):
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.width = width
        self.height = height
        self.speed = speed
        self.pos_x = 0

    def update(self, direction):
        if direction == "left":
            self.pos_x += self.speed
        elif direction == "right":
            self.pos_x -= self.speed
        self.pos_x %= self.width

    def draw(self, screen, blended_color):
        tinted_image = self.image.copy()
        tinted_image.fill(blended_color, special_flags=pygame.BLEND_MULT)
        screen.blit(tinted_image, (self.pos_x - self.width, 0))
        screen.blit(tinted_image, (self.pos_x, 0))
