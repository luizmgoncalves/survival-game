import pygame
import sys
from skyc import Sky
from mountain import Mountain
from color_filter import ColorFilter

def main():
    # Inicializar Pygame
    pygame.init()
    WIDTH, HEIGHT = 1000, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ciclo de Dia e Noite com Movimento Contínuo")

    # Criar objetos
    sky = Sky("sky.jpg", WIDTH, HEIGHT, speed=2)
    mountain = Mountain("mountain.png", WIDTH, 200, HEIGHT - 200, speed=5)
    color_filter = ColorFilter(seconds_in_full_day=50)

    clock = pygame.time.Clock()
    running = True

    while running:
        delta_time = clock.get_time() / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Checar teclas pressionadas
        keys = pygame.key.get_pressed()
        direction = None
        if keys[pygame.K_LEFT]:
            direction = "left"
        elif keys[pygame.K_RIGHT]:
            direction = "right"

        # Atualizar componentes
        if direction:
            sky.update(direction)
            mountain.update(direction)

        # Atualizar cor do filtro
        blended_color = color_filter.get_color(delta_time)

        # Desenhar tela
        screen.fill((0, 0, 0))
        sky.draw(screen, blended_color)
        mountain.draw(screen)

        # Atualizar display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
