import pygame
from settings import *

def draw_bar(surface, x, y, pct, color, width=200, height=20):
    if pct < 0:
        pct = 0
    fill = (pct / 100.0) * width
    outline_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, color, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)
        
    def draw(self):
        # Draw Health Bar
        draw_bar(self.game.screen, 10, 10, self.game.player.health, (180, 0, 0))
        health_text = self.font.render("HEALTH", True, WHITE)
        self.game.screen.blit(health_text, (220, 12))
        
        # Draw Battery Bar
        draw_bar(self.game.screen, 10, 40, self.game.flashlight.battery, (0, 120, 255))
        battery_text = self.font.render("BATTERY", True, WHITE)
        self.game.screen.blit(battery_text, (220, 42))
