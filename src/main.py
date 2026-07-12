import pygame
import sys
from settings import *
from player import Player
from camera import Camera
from map import TiledMap, Obstacle, ExitZone
from flashlight import Flashlight
from enemy import ShadowWalker
from items import Battery, MedKit
from ui import UI
from sounds import SoundManager

class Game:
    def __init__(self):
        # Initialize pygame and create the window
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize sounds
        self.sound = SoundManager()
        self.sound.load_sound('footstep', 'assets/sounds/footstep.wav')
        self.sound.load_sound('flashlight', 'assets/sounds/flashlight.wav')
        self.sound.load_sound('growl', 'assets/sounds/growl.wav')
        self.sound.load_sound('heartbeat', 'assets/sounds/heartbeat.wav')
        self.sound.play_music('assets/music/bgm.ogg')

    def new(self):
        # Initialize all variables and do all the setup for a new game
        self.state = "PLAYING"
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.exits = pygame.sprite.Group()
        
        self.start_time = pygame.time.get_ticks()
        self.completion_time = 0.0
        
        # Map setup
        self.map = TiledMap('assets/maps/map.tmx')
        self.map_img = self.map.make_map()
        import math
        # Load obstacles and spawn game elements dynamically from map
        for tile_object in self.map.tmxdata.objects:
            # If the object is named "Wall", or it has no name at all (which happens when you just draw a new rectangle in Tiled)
            if tile_object.name == 'Wall' or tile_object.name is None or tile_object.name == '':
                x = tile_object.x
                y = tile_object.y
                w = tile_object.width
                h = tile_object.height
                rot = getattr(tile_object, 'rotation', 0)
                
                if rot != 0:
                    # Calculate bounding box of rotated rectangle (Pygame Rect needs AABB)
                    rad = math.radians(rot)
                    cos_r = math.cos(rad)
                    sin_r = math.sin(rad)
                    
                    corners = [(0, 0), (w, 0), (w, h), (0, h)]
                    rotated_corners = []
                    for cx, cy in corners:
                        rx = cx * cos_r - cy * sin_r
                        ry = cx * sin_r + cy * cos_r
                        rotated_corners.append((x + rx, y + ry))
                        
                    min_x = min([c[0] for c in rotated_corners])
                    max_x = max([c[0] for c in rotated_corners])
                    min_y = min([c[1] for c in rotated_corners])
                    max_y = max([c[1] for c in rotated_corners])
                    
                    x, y = min_x, min_y
                    w, h = max_x - min_x, max_y - min_y
                    
                Obstacle(self, x, y, w, h)
            elif tile_object.name == 'player':
                self.player = Player(self, tile_object.x + tile_object.width // 2, tile_object.y + tile_object.height // 2)
                self.all_sprites.add(self.player)
            elif tile_object.name == 'monster':
                ShadowWalker(self, tile_object.x + tile_object.width // 2, tile_object.y + tile_object.height // 2)
            elif tile_object.name == 'battery':
                Battery(self, tile_object.x + tile_object.width // 2, tile_object.y + tile_object.height // 2)
            elif tile_object.name == 'medkit':
                MedKit(self, tile_object.x + tile_object.width // 2, tile_object.y + tile_object.height // 2)
            elif tile_object.name == 'exit':
                ExitZone(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
        
        # Flashlight setup
        self.flashlight = Flashlight(self)
        
        # UI setup
        self.ui = UI(self)
        
        # Camera setup
        self.camera = Camera(self.map.width, self.map.height)
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()

    def events(self):
        # Catch all events here
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                if event.key == pygame.K_f and self.state == "PLAYING":
                    self.sound.play('flashlight')
                    self.flashlight.toggle()
                if event.key == pygame.K_r and self.state in ["GAME_OVER", "VICTORY"]:
                    self.new()

    def update(self):
        # Update game logic here
        if self.state == "PLAYING":
            self.all_sprites.update(self.dt)
            self.camera.update(self.player)
            self.flashlight.update(self.dt)
            
            # Check Win condition
            if pygame.sprite.spritecollideany(self.player, self.exits):
                self.state = "VICTORY"
                self.completion_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
                
            # Check Lose condition
            if self.player.health <= 0 or self.flashlight.battery <= 0:
                self.state = "GAME_OVER"

    def draw(self):
        # Draw everything here
        self.screen.fill(BLACK)
        
        if self.state == "PLAYING":
            # Draw the map background
            map_rect = self.map_img.get_rect()
            self.screen.blit(self.map_img, self.camera.apply_rect(map_rect))
            
            # Debug: draw walls as red rectangles so we can see what we collide with
            for wall in self.walls:
                wall_rect = self.camera.apply_rect(wall.rect)
                pygame.draw.rect(self.screen, RED, wall_rect)
                
            # Draw exit zone as yellow
            for e in self.exits:
                pygame.draw.rect(self.screen, (255, 255, 0), self.camera.apply_rect(e.rect))

            # Draw all sprites with camera offset
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
                
            # Draw flashlight effect over everything
            self.flashlight.draw(self.screen, self.camera)
            
            # Draw UI
            self.ui.draw()
            
        elif self.state == "GAME_OVER":
            font = pygame.font.SysFont(None, 72)
            text = font.render('GAME OVER', True, RED)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            font_small = pygame.font.SysFont(None, 36)
            text_small = font_small.render('Press R to Restart', True, WHITE)
            self.screen.blit(text_small, (WIDTH//2 - text_small.get_width()//2, HEIGHT//2 + 50))
            
        elif self.state == "VICTORY":
            font = pygame.font.SysFont(None, 72)
            text = font.render('YOU ESCAPED!', True, GREEN)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2 - 30))
            
            font_medium = pygame.font.SysFont(None, 48)
            time_text = font_medium.render(f'Time: {self.completion_time:.2f} seconds', True, (200, 200, 255))
            self.screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, HEIGHT//2 + 20))
            
            font_small = pygame.font.SysFont(None, 36)
            text_small = font_small.render('Press R to Play Again', True, WHITE)
            self.screen.blit(text_small, (WIDTH//2 - text_small.get_width()//2, HEIGHT//2 + 80))

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    # Create the game object
    g = Game()
    while g.running:
        g.new()
