import pygame
import sys
import time

class ColorFilter:
    def __init__(self, seconds_in_full_day):
        self.seconds_in_full_day = seconds_in_full_day
        self.time_elapsed = 0
        self.dawn_time = 0.2
        self.day_time = 0.3
        self.dusk_time = 0.7
        self.night_time = 0.75
        self.colors = {
            "dawn": pygame.Color(255, 170, 100),
            "day": pygame.Color(255, 255, 255),
            "dusk": pygame.Color(255, 100, 50),
            "night": pygame.Color(20, 20, 60),
        }

    def set_period_colors(self, dawn_color, day_color, dusk_color, night_color):
        self.colors["dawn"] = pygame.Color(*dawn_color)
        self.colors["day"] = pygame.Color(*day_color)
        self.colors["dusk"] = pygame.Color(*dusk_color)
        self.colors["night"] = pygame.Color(*night_color)

    def blend_color(self, color1, color2, blend_factor):
        r = (color1.r * (1 - blend_factor)) + (color2.r * blend_factor)
        g = (color1.g * (1 - blend_factor)) + (color2.g * blend_factor)
        b = (color1.b * (1 - blend_factor)) + (color2.b * blend_factor)
        return pygame.Color(int(r), int(g), int(b))

    def get_color(self, delta_time):
        self.time_elapsed += delta_time
        current_time = (self.time_elapsed % self.seconds_in_full_day) / self.seconds_in_full_day

        if current_time <= self.dawn_time:
            return self.blend_color(self.colors["night"], self.colors["dawn"], current_time / self.dawn_time)
        elif current_time <= self.day_time:
            return self.blend_color(self.colors["dawn"], self.colors["day"], 
                                    (current_time - self.dawn_time) / (self.day_time - self.dawn_time))
        elif current_time <= self.dusk_time:
            return self.blend_color(self.colors["day"], self.colors["dusk"], 
                                    (current_time - self.day_time) / (self.dusk_time - self.day_time))
        else:
            return self.blend_color(self.colors["dusk"], self.colors["night"], 
                                    (current_time - self.dusk_time) / (1 - self.dusk_time))

