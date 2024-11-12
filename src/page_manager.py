# src/page_manager.py
class PageManager:
    def __init__(self):
        self.pages = {}
        self.current_page = None

    def add_page(self, name, page):
        self.pages[name] = page

    def set_page(self, name):
        self.current_page = self.pages.get(name)

    def handle_events(self, event):
        if self.current_page:
            self.current_page.handle_events(event)

    def update(self):
        if self.current_page:
            self.current_page.update()

    def draw(self, screen):
        if self.current_page:
            self.current_page.draw(screen)
