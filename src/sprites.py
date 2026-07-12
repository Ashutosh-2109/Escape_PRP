import pygame

class SpriteSheet:
    """Utility class to load and parse sprite sheets."""
    def __init__(self, filename):
        try:
            self.sprite_sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def get_image(self, x, y, width, height, scale=1):
        """Extracts a single image from the spritesheet."""
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        return image

    def get_animation_frames(self, start_x, start_y, width, height, frames, scale=1):
        """Extracts a full row/sequence of animation frames."""
        frame_list = []
        for i in range(frames):
            frame = self.get_image(start_x + (i * width), start_y, width, height, scale)
            frame_list.append(frame)
        return frame_list
