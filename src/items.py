import pygame
from settings import *

class Battery(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((32, 32))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        
    def update(self, dt):
        # Check collision with player
        if self.rect.colliderect(self.game.player.rect):
            # Recharge flashlight battery
            self.game.flashlight.battery = min(100.0, self.game.flashlight.battery + 40.0)
            self.kill() # Remove from game

class MedKit(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 255, 0)) # Green for health
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        
    def update(self, dt):
        # Check collision with player
        if self.rect.colliderect(self.game.player.rect):
            # Heal player
            self.game.player.health = min(self.game.player.max_health, self.game.player.health + 40.0)
            self.kill() # Remove from game
