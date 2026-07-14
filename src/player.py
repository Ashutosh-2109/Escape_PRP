import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        
        # Load the custom player sprite sheet
        try:
            full_sheet = pygame.image.load('assets/images/player.png').convert_alpha()
            # Remove white boundaries/backgrounds
            full_sheet.set_colorkey((255, 255, 255))
            
            # Dynamically calculate frame size (4 cols, 4 rows)
            w = full_sheet.get_width() // 4
            h = full_sheet.get_height() // 4
            frame = pygame.Surface((w, h), pygame.SRCALPHA)
            frame.blit(full_sheet, (0, 0), (0, 0, w, h))
            self.image = pygame.transform.scale(frame, (TILESIZE, TILESIZE))
            self.image.set_colorkey((255, 255, 255)) # Double ensure no white border
        except Exception:
            self.image = pygame.Surface((TILESIZE, TILESIZE))
            self.image.fill(GREEN)
            
        self.rect = self.image.get_rect()
        
        # Health System
        self.health = 100.0
        self.max_health = 100.0
        
        # Position and movement using vectors for smooth movement
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.rect.center = self.pos
        
        self.speed = PLAYER_SPEED
        
    def get_keys(self):
        self.vel = pygame.math.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        
        # Sprint mechanics
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.speed = PLAYER_SPRINT_SPEED
        else:
            self.speed = PLAYER_SPEED
            
        # Movement directions
        if keys[pygame.K_w]:
            self.vel.y = -self.speed
        if keys[pygame.K_s]:
            self.vel.y = self.speed
        if keys[pygame.K_a]:
            self.vel.x = -self.speed
        if keys[pygame.K_d]:
            self.vel.x = self.speed
            
        # Normalize vector so diagonal movement isn't faster
        if self.vel.magnitude() != 0:
            self.vel = self.vel.normalize() * self.speed
            
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    # Moving right, snap to the left edge of the leftmost wall we hit
                    self.pos.x = min([wall.rect.left for wall in hits]) - self.rect.width / 2
                if self.vel.x < 0:
                    # Moving left, snap to the right edge of the rightmost wall we hit
                    self.pos.x = max([wall.rect.right for wall in hits]) + self.rect.width / 2
                self.vel.x = 0
                self.rect.centerx = self.pos.x
        if dir == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    # Moving down, snap to the top edge of the topmost wall we hit
                    self.pos.y = min([wall.rect.top for wall in hits]) - self.rect.height / 2
                if self.vel.y < 0:
                    # Moving up, snap to the bottom edge of the bottommost wall we hit
                    self.pos.y = max([wall.rect.bottom for wall in hits]) + self.rect.height / 2
                self.vel.y = 0
                self.rect.centery = self.pos.y

    def update(self, dt):
        self.get_keys()
        
        # Prevent high-speed tunneling through thin walls by clamping delta time
        if dt > 0.05:
            dt = 0.05
            
        # Update X position and resolve X collisions
        self.pos.x += self.vel.x * dt
        self.rect.centerx = self.pos.x
        self.collide_with_walls('x')
        
        # Update Y position and resolve Y collisions
        self.pos.y += self.vel.y * dt
        self.rect.centery = self.pos.y
        self.collide_with_walls('y')
        
        # Play footstep sounds when moving
        if self.vel.magnitude() > 0:
            if not hasattr(self, 'last_footstep'):
                self.last_footstep = 0
            now = pygame.time.get_ticks()
            delay = 300 if self.speed == PLAYER_SPRINT_SPEED else 500
            if now - self.last_footstep > delay:
                self.game.sound.play('footstep')
                self.last_footstep = now
