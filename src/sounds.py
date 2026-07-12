import pygame
import os

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.enabled = True
        except:
            self.enabled = False
        self.sounds = {}
        
    def load_sound(self, name, filename):
        if not self.enabled: return
        try:
            self.sounds[name] = pygame.mixer.Sound(filename)
        except FileNotFoundError:
            # Silently fail so the game runs even without sound files
            self.sounds[name] = None
        except pygame.error:
            self.sounds[name] = None
            
    def play(self, name, loops=0):
        if not self.enabled: return
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play(loops)
            
    def play_music(self, filename):
        if not self.enabled: return
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play(-1)
        except (FileNotFoundError, pygame.error):
            pass
