# src/page_manager.py
import pygame
import commons

class PageManager:
    def __init__(self):
        self.pages = {}
        self.current_page = None

    def add_page(self, name, page):
        self.pages[name] = page

    def set_page(self, name):
        self.current_page = self.pages.get(name)

    def handle_events(self, event: pygame.event.Event):
        if event.type == pygame.VIDEORESIZE:
            for page in self.pages.values():
                page.resize(event.size)

        if event.type == commons.CHANGE_PAGE_EVENT:
            self.set_page(event.page)
            self.current_page.reset(**event.dict)

        if self.current_page:
            self.current_page.handle_events(event)

    def update(self, delta_time):
        if self.current_page:
            self.current_page.update(delta_time)

    def draw(self, screen):
        if self.current_page:
            self.current_page.draw(screen)
