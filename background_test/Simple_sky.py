mport pygame

pygame.init()

win = pygame.display.set_mode((1000, 500))
bg_img = pygame.image.load('floresta_fundo.jpg')
bg = pygame.transform.scale(bg_img, (1000, 500))
width = 1000

pos_x = 0
velocidade = 5  # Velocidade do movimento do fundo
clock = pygame.time.Clock()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    # Checa se as teclas estão pressionadas para mover o fundo
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        pos_x += velocidade  # Movimenta o fundo para a direita ao pressionar LEFT
    if keys[pygame.K_RIGHT]:
        pos_x -= velocidade  # Movimenta o fundo para a esquerda ao pressionar RIGHT

    pos_x = pos_x % width  # Garante que a posição sempre fique dentro do ciclo de -width a width

    win.fill((0, 0, 0))
    win.blit(bg, (pos_x - width, 0)) 
    win.blit(bg, (pos_x, 0))          

    pygame.display.update()
    clock.tick(60)  # Controle de FPS

pygame.quit()
