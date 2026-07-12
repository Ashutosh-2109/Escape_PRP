import pygame
import pytmx
from settings import *

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class ExitZone(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.exits
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        
class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def make_map(self):
        # Attempt to load the realistic image-based map
        try:
            temp_surface = pygame.image.load('assets/images/background_map.png').convert()
            # Override map dimensions to perfectly match the image
            self.width = temp_surface.get_width()
            self.height = temp_surface.get_height()
        except FileNotFoundError:
            # Fallback to a simple surface if the user hasn't saved the image yet
            temp_surface = pygame.Surface((self.width, self.height))
            temp_surface.fill((20, 20, 20)) # Dark environment
        return temp_surface
