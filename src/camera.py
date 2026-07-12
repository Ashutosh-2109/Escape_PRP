import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        # The camera Rect defines the offset we apply to all sprites/elements
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Move the entity's rect by the camera's offset
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        # Move a raw rect by the camera's offset
        return rect.move(self.camera.topleft)

    def update(self, target):
        # Center the target (player) on the screen
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        
        # We will clamp this in the next steps when the map is loaded
        # For now, it stays centered anywhere the player moves
        self.camera = pygame.Rect(x, y, self.width, self.height)
