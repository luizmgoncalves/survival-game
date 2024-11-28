import pygame
from .game_actor import GameActor

P = './game_images/previous/'

# Load sprite images
walking_sprites = [pygame.image.load(P + f"d{x}.png") for x in range(1, 7)]
running_sprites = [pygame.image.load(P + f"d{x}.png") for x in range(1, 7)]
jumping_sprites = [pygame.image.load(P + f"d{x}.png") for x in range(3, 4)]
idle_sprites =  [pygame.image.load(P + f"d{x}.png") for x in range(1, 2)]

# Create a GameActor
actor = GameActor(
    position=(0, 0),
    size=(32, 48),
    life=100,
    max_vel=200,
    walking_sprites_right=walking_sprites,
    running_sprites_right=running_sprites,
    jumping_sprites_right=jumping_sprites,
    idle_sprites_right=idle_sprites,
)

ground = pygame.Rect(0, 400, 500, 100)

running = True
clock = pygame.time.Clock()

screen = pygame.display.set_mode((800, 800))

while running:
    delta_time = clock.tick(60) / 1000.0  # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Example movement logic
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        actor.walk_left()
    elif keys[pygame.K_RIGHT]:
        actor.walk_right()
    elif keys[pygame.K_a]:  # Run left
        actor.run_left()
    elif keys[pygame.K_d]:  # Run right
        actor.run_right()
    
    actor.velocity.x *= 0.8

    actor.velocity.y += 1000 * delta_time
    
    actor.move([ground], delta_time)

    # Jumping
    if keys[pygame.K_SPACE]:  # Jump
        actor.jump()

    # Handle attack
    if keys[pygame.K_f]:  # Attack
        actor.attack()

    # Update actor
    actor.update(delta_time)

    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (255, 0, 0), ground)
    pygame.draw.rect(screen, (0, 255, 0), actor.rect)
    screen.blit(actor.image, actor.rect)
    pygame.display.flip()
