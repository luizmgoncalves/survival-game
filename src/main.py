# src/main.py
import pygame
from page_manager import PageManager
from pages import EntryMenu, WorldsPage, SettingsPage
import commons

pygame.init()
screen = pygame.display.set_mode((1920/2, 1080/2), pygame.RESIZABLE)

page_manager = PageManager()
page_manager.add_page("entry", EntryMenu())
page_manager.add_page("worlds_page", WorldsPage())
page_manager.add_page("settings", SettingsPage())

page_manager.set_page("entry")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        page_manager.handle_events(event)

    page_manager.update()
    page_manager.draw(screen)
    pygame.time.delay(20)

pygame.quit()
