# src/main.py
import pygame
import commons
from page_manager import PageManager
from pages import EntryMenu, WorldsPage, SettingsPage, WorldPage, CreatingPage, GamePage
import commons
import images.image_loader as image_loader

pygame.init()
screen = pygame.display.set_mode((commons.WIDTH, commons.HEIGHT), pygame.RESIZABLE)

image_loader.IMAGE_LOADER.init()

page_manager = PageManager()
page_manager.add_page("entry", EntryMenu())
page_manager.add_page("worlds_page", WorldsPage())
page_manager.add_page("settings", SettingsPage())
page_manager.add_page("world", WorldPage())
page_manager.add_page("create", CreatingPage())
page_manager.add_page("game", GamePage())

page_manager.set_page("entry")

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        page_manager.handle_events(event)
        
        if event.type == pygame.WINDOWRESIZED:
            commons.WIDTH, commons.HEIGHT = pygame.display.get_window_size()
        if event.type == pygame.QUIT:
            running = False
        
        

    
    delta_time = clock.tick(50) / 1000
    page_manager.update(delta_time)
    page_manager.draw(screen)
    pygame.time.delay(20)

pygame.quit()
