import pygame
import math
import random
from settings import *

class Flashlight:
    def __init__(self, game):
        self.game = game
        self.active = True
        self.battery = 100.0
        self.drain_rate = 100.0 / 25.0 # Exactly 25 seconds of battery life
        self.radius = 450
        self.angle_spread = math.radians(50) # 50 degrees spread
        
    def update(self, dt):
        if self.active:
            self.battery -= self.drain_rate * dt
            if self.battery <= 0:
                self.battery = 0
                self.active = False
                
    def toggle(self):
        if self.battery > 0:
            self.active = not self.active
            
    def is_point_illuminated(self, point_x, point_y):
        if not self.active or self.battery <= 0:
            return False
            
        player_world_pos = self.game.player.pos
        
        # Get mouse pos in world coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_world_x = mouse_x - self.game.camera.camera.x
        mouse_world_y = mouse_y - self.game.camera.camera.y
        
        # angle to mouse
        dx_mouse = mouse_world_x - player_world_pos.x
        dy_mouse = mouse_world_y - player_world_pos.y
        light_angle = math.atan2(dy_mouse, dx_mouse)
        
        # angle to point
        dx_point = point_x - player_world_pos.x
        dy_point = point_y - player_world_pos.y
        point_angle = math.atan2(dy_point, dx_point)
        
        # Distance check
        dist_sq = dx_point**2 + dy_point**2
        if dist_sq > self.radius**2:
            return False
            
        # Angle check
        angle_diff = (point_angle - light_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(angle_diff) <= self.angle_spread / 2:
            return True
            
        return False
            
    def draw(self, surface, camera):
        # We draw a darkness overlay
        darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        darkness.fill((0, 0, 0, 245)) # deep darkness
        
        if self.active and self.battery > 0:
            # Flicker effect when battery is low
            if self.battery < 20:
                if random.random() < 0.1: # 10% chance to flicker off for a frame
                    surface.blit(darkness, (0, 0))
                    return
                    
            # Get screen positions
            player_pos = camera.apply_rect(self.game.player.rect).center
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Angle from player to mouse
            dx = mouse_x - player_pos[0]
            dy = mouse_y - player_pos[1]
            angle = math.atan2(dy, dx)
            
            # Points for polygon
            points = [player_pos]
            num_segments = 20
            start_angle = angle - self.angle_spread / 2
            end_angle = angle + self.angle_spread / 2
            
            for i in range(num_segments + 1):
                current_angle = start_angle + (end_angle - start_angle) * (i / num_segments)
                point_x = player_pos[0] + math.cos(current_angle) * self.radius
                point_y = player_pos[1] + math.sin(current_angle) * self.radius
                points.append((point_x, point_y))
                
            # Cut out the light cone by drawing transparent shape on darkness overlay
            # Using blend mode to clear alpha
            pygame.draw.polygon(darkness, (0, 0, 0, 0), points)
            
        surface.blit(darkness, (0, 0))
