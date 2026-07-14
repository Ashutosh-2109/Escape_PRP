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
from leaderboard import Leaderboard

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
        
        # Load door image if available
        try:
            self.door_img = pygame.image.load('assets/images/door.png').convert_alpha()
        except Exception:
            self.door_img = None
            
        # Load club logo
        try:
            self.logo_img = pygame.image.load('assets/images/logo.png').convert_alpha()
            self.logo_img = pygame.transform.scale(self.logo_img, (120, 120))
        except Exception:
            self.logo_img = None
        
        # Initialize leaderboard
        self.leaderboard = Leaderboard()

    def new(self):
        # Initialize all variables and do all the setup for a new game
        self.state = "INPUT_NAME"
        self.player_name = ""
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.exits = pygame.sprite.Group()
        
        self.items = pygame.sprite.Group()
        self.exits = pygame.sprite.Group()
        
        self.start_time = 0
        self.completion_time = 0.0
        
        # Blood effect variables
        self.damage_overlay_alpha = 0
        
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
                    
                # Handle text input for name entry
                if self.state == "INPUT_NAME":
                    if event.key == pygame.K_RETURN:
                        if self.player_name.strip() != "":
                            self.state = "PLAYING"
                            self.start_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        # Limit name length
                        if len(self.player_name) < 15 and event.unicode.isprintable():
                            self.player_name += event.unicode

    def update(self):
        # Update game logic here
        if self.state == "PLAYING":
            self.all_sprites.update(self.dt)
            self.camera.update(self.player)
            self.flashlight.update(self.dt)
            
            # Fade out damage overlay
            if self.damage_overlay_alpha > 0:
                self.damage_overlay_alpha = max(0, self.damage_overlay_alpha - 300 * self.dt)
            
            # Check Win condition
            if pygame.sprite.spritecollideany(self.player, self.exits):
                self.state = "VICTORY"
                self.completion_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
                self.leaderboard.add_score(self.player_name, self.completion_time)
                
            # Check Lose condition
            if self.player.health <= 0 or self.flashlight.battery <= 0:
                self.state = "GAME_OVER"

    def draw(self):
        # Draw everything here
        self.screen.fill(BLACK)
        
        if self.state == "INPUT_NAME":
            font = pygame.font.SysFont(None, 64)
            title = font.render('ENTER YOUR NAME', True, WHITE)
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
            
            # Draw text box
            box_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 25, 400, 50)
            pygame.draw.rect(self.screen, (50, 50, 50), box_rect)
            pygame.draw.rect(self.screen, WHITE, box_rect, 2)
            
            name_surf = font.render(self.player_name, True, GREEN)
            self.screen.blit(name_surf, (box_rect.x + 10, box_rect.y + 5))
            
            prompt = pygame.font.SysFont(None, 36).render('Press ENTER to start', True, (200, 200, 200))
            self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 50))
            
        elif self.state == "PLAYING":
            # Draw the map background
            map_rect = self.map_img.get_rect()
            self.screen.blit(self.map_img, self.camera.apply_rect(map_rect))
            
            # Debug: draw walls as red rectangles so we can see what we collide with
            for wall in self.walls:
                wall_rect = self.camera.apply_rect(wall.rect)
                pygame.draw.rect(self.screen, RED, wall_rect)
                
            # Draw exit zone as a door
            for e in self.exits:
                rect = self.camera.apply_rect(e.rect)
                if self.door_img:
                    scaled_door = pygame.transform.scale(self.door_img, (e.rect.width, e.rect.height))
                    self.screen.blit(scaled_door, rect)
                else:
                    # Draw a 3D beveled wooden door
                    # 1. Drop shadow (draw a slightly larger offset black rectangle with transparency)
                    shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
                    shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    shadow_surf.fill((0, 0, 0, 100)) # Semi-transparent black shadow
                    self.screen.blit(shadow_surf, shadow_rect)
                    
                    # 2. Main door body (Base wood color)
                    pygame.draw.rect(self.screen, (120, 60, 15), rect) # Rich brown
                    
                    # 3. 3D Bevel Highlights (Light on top/left, Shadow on bottom/right)
                    pygame.draw.line(self.screen, (180, 100, 40), (rect.x, rect.y), (rect.x + rect.width, rect.y), 3) # Top highlight
                    pygame.draw.line(self.screen, (180, 100, 40), (rect.x, rect.y), (rect.x, rect.y + rect.height), 3) # Left highlight
                    pygame.draw.line(self.screen, (60, 30, 5), (rect.x + rect.width, rect.y), (rect.x + rect.width, rect.y + rect.height), 3) # Right shadow
                    pygame.draw.line(self.screen, (60, 30, 5), (rect.x, rect.y + rect.height), (rect.x + rect.width, rect.y + rect.height), 3) # Bottom shadow
                    
                    # 4. Inset wood panels for realistic texture
                    panel_width = rect.width - 16
                    if panel_width > 10:
                        panel1_rect = pygame.Rect(rect.x + 8, rect.y + 12, panel_width, rect.height // 2 - 16)
                        panel2_rect = pygame.Rect(rect.x + 8, rect.y + rect.height // 2 + 4, panel_width, rect.height // 2 - 16)
                        
                        for p_rect in [panel1_rect, panel2_rect]:
                            if p_rect.height > 5:
                                # Inset background
                                pygame.draw.rect(self.screen, (90, 45, 10), p_rect)
                                # Inset shadow (top/left inside the panel)
                                pygame.draw.line(self.screen, (50, 25, 5), (p_rect.x, p_rect.y), (p_rect.x + p_rect.width, p_rect.y), 1)
                                pygame.draw.line(self.screen, (50, 25, 5), (p_rect.x, p_rect.y), (p_rect.x, p_rect.y + p_rect.height), 1)
                                # Inset highlight (bottom/right inside the panel)
                                pygame.draw.line(self.screen, (150, 80, 25), (p_rect.x + p_rect.width, p_rect.y), (p_rect.x + p_rect.width, p_rect.y + p_rect.height), 1)
                                pygame.draw.line(self.screen, (150, 80, 25), (p_rect.x, p_rect.y + p_rect.height), (p_rect.x + p_rect.width, p_rect.y + p_rect.height), 1)
                    
                    # 5. Draw a 3D Gold Doorknob
                    knob_x = rect.x + rect.width - 15 if rect.width > 30 else rect.x + rect.width // 2
                    knob_y = rect.y + rect.height // 2
                    # Knob shadow
                    pygame.draw.circle(self.screen, (40, 20, 0), (int(knob_x) + 2, int(knob_y) + 2), 7)
                    # Main knob
                    pygame.draw.circle(self.screen, (230, 190, 0), (int(knob_x), int(knob_y)), 6)
                    # Knob highlight
                    pygame.draw.circle(self.screen, (255, 240, 150), (int(knob_x) - 2, int(knob_y) - 2), 2)

            # Draw all sprites with camera offset
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
                
            # Draw flashlight effect over everything
            self.flashlight.draw(self.screen, self.camera)
            
            # Draw blood overlay if taking damage
            if self.damage_overlay_alpha > 0:
                blood_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                blood_surface.fill((255, 0, 0, int(self.damage_overlay_alpha)))
                self.screen.blit(blood_surface, (0, 0))
            
            # Draw UI
            self.ui.draw()
            
        elif self.state == "GAME_OVER":
            font = pygame.font.SysFont(None, 72)
            text = font.render('GAME OVER', True, RED)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 200))
            
            font_medium = pygame.font.SysFont(None, 48)
            
            # Display Leaderboard
            lb_title = font_medium.render('TOP 3 FASTEST TIMES', True, (255, 215, 0)) # Gold
            self.screen.blit(lb_title, (WIDTH//2 - lb_title.get_width()//2, HEIGHT//2 - 50))
            
            top_scores = self.leaderboard.get_top_3()
            for i, score in enumerate(top_scores):
                score_text = font_medium.render(f"{i+1}. {score['name']} - {score['time']:.2f}s", True, WHITE)
                self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + (i * 40)))
            
            font_small = pygame.font.SysFont(None, 36)
            text_small = font_small.render('Press R to Restart', True, WHITE)
            self.screen.blit(text_small, (WIDTH//2 - text_small.get_width()//2, HEIGHT//2 + 150))
            
        elif self.state == "VICTORY":
            font = pygame.font.SysFont(None, 72)
            text = font.render('YOU ESCAPED!', True, GREEN)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 200))
            
            font_medium = pygame.font.SysFont(None, 48)
            time_text = font_medium.render(f'Your Time: {self.completion_time:.2f} seconds', True, (200, 200, 255))
            self.screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, HEIGHT//2 - 130))
            
            # Display Leaderboard
            lb_title = font_medium.render('TOP 3 FASTEST TIMES', True, (255, 215, 0)) # Gold
            self.screen.blit(lb_title, (WIDTH//2 - lb_title.get_width()//2, HEIGHT//2 - 50))
            
            top_scores = self.leaderboard.get_top_3()
            for i, score in enumerate(top_scores):
                score_text = font_medium.render(f"{i+1}. {score['name']} - {score['time']:.2f}s", True, WHITE)
                self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + (i * 40)))
            
            font_small = pygame.font.SysFont(None, 36)
            text_small = font_small.render('Press R to Play Again', True, WHITE)
            self.screen.blit(text_small, (WIDTH//2 - text_small.get_width()//2, HEIGHT//2 + 150))
            
        # Draw the club logo and text on any ending screen
        if self.state in ["GAME_OVER", "VICTORY"] and getattr(self, 'logo_img', None):
            logo_x = WIDTH - 150
            logo_y = 30
            self.screen.blit(self.logo_img, (logo_x, logo_y))
            
            font_logo = pygame.font.SysFont(None, 28)
            logo_text = font_logo.render('The AI ML Club', True, WHITE)
            text_x = logo_x + (120 // 2) - (logo_text.get_width() // 2)
            self.screen.blit(logo_text, (text_x, logo_y + 130))

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    # Create the game object
    g = Game()
    while g.running:
        g.new()
