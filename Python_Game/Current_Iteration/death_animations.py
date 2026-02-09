import pygame

from base_settings import resource_path


# Lasertanker death animation sprite
class LazertankerDeathAnimation(pygame.sprite.Sprite):
    """Animation sprite for lasertanker death sequence"""

    def __init__(self, settings, screen, center_pos, size):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.size = size

        # Load death animation images
        self.death_images = []
        for i in range(0, 5):
            try:
                img_path = resource_path(f"img/laz0rtanker_death{i}.png")
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.smoothscale(img, size)
                self.death_images.append(img)
            except Exception:
                # Fallback: create a colored rectangle if image missing
                img = pygame.Surface(size, pygame.SRCALPHA)
                img.fill((255, 0, 0, 200))
                self.death_images.append(img)

        self.current_frame = 0
        self.image = self.death_images[0]
        self.rect = self.image.get_rect(center=center_pos)
        self.start_time = pygame.time.get_ticks()
        self.frame_duration_ms = 1000  # 1 second per frame

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        frame_index = int(elapsed / self.frame_duration_ms)

        if frame_index >= len(self.death_images):
            self.kill()  # Animation complete
        else:
            self.current_frame = frame_index
            self.image = self.death_images[frame_index]
            self.rect = self.image.get_rect(center=self.rect.center)


# Cruiser death animation sprite
class CruiserDeathAnimation(pygame.sprite.Sprite):
    """Animation sprite for cruiser death sequence"""

    def __init__(self, settings, screen, center_pos, size):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.size = size

        # Load death animation images (3 frames)
        self.death_images = []
        for i in range(0, 4):
            try:
                img_path = resource_path(f"img/cruiser_death{i}.png")
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.smoothscale(img, size)
                self.death_images.append(img)
            except Exception:
                # Fallback: create a colored rectangle if image missing
                img = pygame.Surface(size, pygame.SRCALPHA)
                img.fill((0, 255, 0, 200))
                self.death_images.append(img)

        self.current_frame = 0
        self.image = self.death_images[0]
        self.rect = self.image.get_rect(center=center_pos)
        self.start_time = pygame.time.get_ticks()
        self.frame_duration_ms = 1000  # 1 second per frame

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        frame_index = int(elapsed / self.frame_duration_ms)

        if frame_index >= len(self.death_images):
            self.kill()  # Animation complete
        else:
            self.current_frame = frame_index
            self.image = self.death_images[frame_index]
            self.rect = self.image.get_rect(center=self.rect.center)


# Destroyer death animation sprite
class DestroyerDeathAnimation(pygame.sprite.Sprite):
    """Animation sprite for destroyer death sequence"""

    def __init__(self, settings, screen, center_pos, size):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.size = size

        # Load death animation images (2 frames)
        self.death_images = []
        for i in range(0, 3):
            try:
                img_path = resource_path(f"img/destroyer_death{i}.png")
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.smoothscale(img, size)
                self.death_images.append(img)
            except Exception:
                # Fallback: create a colored rectangle if image missing
                img = pygame.Surface(size, pygame.SRCALPHA)
                img.fill((255, 255, 0, 200))
                self.death_images.append(img)

        self.current_frame = 0
        self.image = self.death_images[0]
        self.rect = self.image.get_rect(center=center_pos)
        self.start_time = pygame.time.get_ticks()
        self.frame_duration_ms = 1000  # 1 second per frame

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        frame_index = int(elapsed / self.frame_duration_ms)

        if frame_index >= len(self.death_images):
            self.kill()  # Animation complete
        else:
            self.current_frame = frame_index
            self.image = self.death_images[frame_index]
            self.rect = self.image.get_rect(center=self.rect.center)




