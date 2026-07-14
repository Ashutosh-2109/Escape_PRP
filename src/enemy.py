import pygame
import math
from settings import *

class ShadowWalker(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Load the custom monster sprite sheet
        try:
            full_sheet = pygame.image.load('assets/images/monster.png').convert_alpha()
            # Remove white boundaries/backgrounds
            full_sheet.set_colorkey((255, 255, 255))
            
            # Dynamically calculate frame size (4 cols, 4 rows)
            w = full_sheet.get_width() // 4
            h = full_sheet.get_height() // 4
            frame = pygame.Surface((w, h), pygame.SRCALPHA)
            frame.blit(full_sheet, (0, 0), (0, 0, w, h))
            self.image = pygame.transform.scale(frame, (TILESIZE, TILESIZE))
            self.image.set_colorkey((255, 255, 255))
        except Exception:
            self.image = pygame.Surface((TILESIZE, TILESIZE))
            self.image.fill((150, 0, 0)) # Dark red color
            
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 280 # Increased speed to force player to sprint
        self.state = "Idle"
        self.attack_damage = 25 # 25% of 100 max health
        self.attack_cooldown = 1.0
        self.last_attack_time = 0

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = min([wall.rect.left for wall in hits]) - self.rect.width / 2
                if self.vel.x < 0:
                    self.pos.x = max([wall.rect.right for wall in hits]) + self.rect.width / 2
                self.vel.x = 0
                self.rect.centerx = self.pos.x
        if dir == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = min([wall.rect.top for wall in hits]) - self.rect.height / 2
                if self.vel.y < 0:
                    self.pos.y = max([wall.rect.bottom for wall in hits]) + self.rect.height / 2
                self.vel.y = 0
                self.rect.centery = self.pos.y

    def update(self, dt):
        if dt > 0.05:
            dt = 0.05
            
        is_lit = self.game.flashlight.is_point_illuminated(self.pos.x, self.pos.y)
        
        if self.state == "Idle":
            # Check if illuminated by flashlight
            if is_lit:
                self.state = "Chase"
                
        elif self.state == "Chase":
            if not is_lit:
                self.state = "Idle"
                return
                
            # Move towards player
            player_pos = self.game.player.pos
            direction = player_pos - self.pos
            if direction.length() > 0:
                direction = direction.normalize()
            self.vel = direction * self.speed
            
            # Apply movement and collision
            self.pos.x += self.vel.x * dt
            self.rect.centerx = self.pos.x
            self.collide_with_walls('x')
            
            self.pos.y += self.vel.y * dt
            self.rect.centery = self.pos.y
            self.collide_with_walls('y')
            
            # Check attack
            if self.rect.colliderect(self.game.player.rect):
                self.state = "Attack"
                
        elif self.state == "Attack":
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self.last_attack_time > self.attack_cooldown:
                self.game.player.health -= self.attack_damage
                self.game.damage_overlay_alpha = 150 # Trigger blood effect
                self.last_attack_time = current_time
            
            # If player moves away, go back to chase
            if not self.rect.colliderect(self.game.player.rect):
                self.state = "Chase"
