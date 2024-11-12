import pygame

pygame.init()

win = pygame.display.set_mode((1000, 500))
bg_img = pygame.image.load('akdi31.jpg')
bg = pygame.transform.scale(bg_img, (1000, 500))  
width = 1000

pos_x = 0
velocidade = 5
escurecimento = 0
escurecimento_max = 200  # Valor máximo de escurecimento
distancia_total = 0  
distancia_para_escurecer = 50  # A cada 50 pixels, o escurecimento muda
distancia_para_clarear = 50  # A cada 50 pixels, o clareamento ocorre
escurecendo = False  # Começa claro
clock = pygame.time.Clock()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Checa se as teclas estão pressionadas para mover o fundo
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
        pos_x += velocidade if keys[pygame.K_LEFT] else -velocidade
        distancia_total += velocidade  # Conta a distância percorrida

    # Corrige o posicionamento para transição contínua
    pos_x = pos_x % width

    # Controla o ciclo de escurecimento
    if escurecendo and distancia_total >= distancia_para_escurecer:
        escurecimento += 1
        distancia_total = 0  # Reinicia a contagem de distância
        if escurecimento >= escurecimento_max:
            escurecendo = False  # Inicia o ciclo clareamento

    # Controla o ciclo de clareamento
    if not escurecendo and distancia_total >= distancia_para_clarear:
        escurecimento -= 1
        distancia_total = 0  # Reinicia a contagem distância
        if escurecimento <= 0:
            escurecendo = True  # Inicia o ciclo escurecimento

    # Continuidade de imagem
    win.fill((0, 0, 0))
    win.blit(bg, (pos_x - width, 0))
    win.blit(bg, (pos_x, 0))
    
    # Adiciona uma camada de escuridão 
    overlay = pygame.Surface((1000, 500))  
    overlay.set_alpha(escurecimento)  # Define o nível de transparência
    overlay.fill((0, 0, 0))  # Preenche a superfície com preto para escurecimento
    win.blit(overlay, (0, 0))  # Sobrepõe o escurecimento na tela

    pygame.display.update()
    clock.tick(60)

pygame.quit()
