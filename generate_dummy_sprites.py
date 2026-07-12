import pygame
import os

def create_dummy_sprite(filename, color, width=64, height=64, rows=4, cols=4):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    surf = pygame.Surface((width * cols, height * rows), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0)) # Transparent background
    
    # 4 rows: Down, Left, Up, Right
    # 4 cols: Idle/Walk cycle (Frame 1, 2, 3, 4)
    
    for r in range(rows):
        for c in range(cols):
            x = c * width
            y = r * height
            
            # Draw base body
            pygame.draw.rect(surf, color, (x + 16, y + 16, 32, 48))
            # Draw head
            pygame.draw.circle(surf, (200, 150, 100) if color == (0,255,0) else (100,0,0), (x + 32, y + 16), 16)
            
            # Draw simple eyes based on direction
            # r: 0=Down, 1=Left, 2=Up, 3=Right
            eye_color = (255, 255, 255)
            if r == 0: # Down
                pygame.draw.circle(surf, eye_color, (x + 24, y + 12), 4)
                pygame.draw.circle(surf, eye_color, (x + 40, y + 12), 4)
            elif r == 1: # Left
                pygame.draw.circle(surf, eye_color, (x + 20, y + 12), 4)
            elif r == 3: # Right
                pygame.draw.circle(surf, eye_color, (x + 44, y + 12), 4)
                
            # Draw legs moving based on frame
            if c % 2 != 0: # Walk frames
                pygame.draw.rect(surf, (0,0,0), (x+20, y+50, 8, 14))
                pygame.draw.rect(surf, (0,0,0), (x+36, y+40, 8, 14))
            else:
                pygame.draw.rect(surf, (0,0,0), (x+20, y+40, 8, 14))
                pygame.draw.rect(surf, (0,0,0), (x+36, y+50, 8, 14))
                
    pygame.image.save(surf, filename)
    print(f"Generated {filename}")

if __name__ == "__main__":
    pygame.init()
    create_dummy_sprite("assets/images/player.png", (0, 255, 0)) # Green player
    create_dummy_sprite("assets/images/monster.png", (150, 0, 0)) # Red monster
    pygame.quit()
