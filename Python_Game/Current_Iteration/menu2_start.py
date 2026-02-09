# menu2_start.py
# This file holds the class that works the start menu, and calls the various sub-menus..
# Returns a dict like: {"starting_wave": 1..5, "num_players": 1..4, "confirmed": True}
# ESC returns {"confirmed": False} so MenuMain can go back.

import pygame
import os
from base_settings import resource_path

class MenuStart:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, settings, play_sound_callback=None):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.play_sound_callback = play_sound_callback

        font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf')) 
        try:
            self.title_font = pygame.font.Font(font_path, 72)
            self.item_font = pygame.font.Font(font_path, 40)
            self._update_menu_font_sizes()  # Scale subtitle and hint fonts based on resolution
        except:
            self.title_font = pygame.font.SysFont(None, 72)
            self.item_font = pygame.font.SysFont(None, 40)
            self._update_menu_font_sizes()  # Scale subtitle and hint fonts based on resolution

        # Starting defaults (you can change these if you want)
        self.starting_wave = 1
        self.num_players = 1

        # Selected row in this submenu:
        # 0 = starting wave, 1 = players, 2 = confirm
        self.selected_index = 0
    
    def _update_menu_font_sizes(self):
        """Update menu font sizes based on current resolution - scales proportionally to screen size"""
        # Base font size for Normal resolution (1200x580)
        base_size = 22
        # Reference resolution (Normal)
        reference_width = 1200
        # Scale factor is proportional to screen width relative to reference
        scale = self.settings.screen_width / reference_width
        font_size = int(base_size * scale)
        self.subtitle_font = pygame.font.SysFont(None, font_size)
        self.hint_font = pygame.font.SysFont(None, font_size)

        # Optional: load a background image for the menu once (not every frame)
        self._bg = None
        try:
            self._bg = pygame.image.load(self.settings.startscreen_path).convert()
        except Exception:
            self._bg = None  # fallback: just fill the screen

    # ---------- Drawing helpers ----------
    def _draw_text(self, text, font, x, y, color=(255, 255, 255), center=True):
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surf, rect)

    def _draw_background(self):
        # Step-by-step “blit an image”:
        # 1) Have an image Surface (loaded once): self._bg
        # 2) Scale it to the current screen size
        # 3) blit() it onto the screen at (0, 0)
        if self._bg:
            w, h = self.screen.get_size()
            scaled = pygame.transform.smoothscale(self._bg, (w, h))
            self.screen.blit(scaled, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

    def _draw_menu(self):
        w, h = self.screen.get_size()

        # Background first (bottom-most layer)
        self._draw_background()

        # Title
        self._draw_text("START GAME?", self.title_font, w // 2, int(h * 0.10))
        self._draw_text("NOW THAT THE GAME HAS SOUND... Check Settings if you want to toggle the sound on and off.", self.subtitle_font, w // 2, int(h * 0.18))
        self._draw_text("Any luck with that secret password yet? ", self.subtitle_font, w // 2, int(h * 0.22))
        self._draw_text("If not... Hard Mode now gives you DOUBLE-SIZED inventories, and the ability to have up to 4 squadrons...", self.subtitle_font, w // 2, int(h * 0.28))
        self._draw_text("Next projects: I will be working on getting the MAC/Railgun powerup and EMP powerups functional; plus BOMBARDER ALIENS.", self.subtitle_font, w // 2, int(h * 0.60))

        # Menu rows (excluding secret password - drawn separately)
        # Wave selection: show individual options 1-5
        wave_options_text = "Pick Starting Wave: "
        for wave_num in range(1, 6):  # Waves 1-5
            if wave_num == self.starting_wave:
                wave_options_text += f"[{wave_num}] "
            else:
                wave_options_text += f"{wave_num} "
        
        menu_rows = [
            wave_options_text,
            f"Pick Number of Players(1-4):        < {self.num_players} >",
            "START GAME",
        ]

        base_y = int(h * 0.35)
        row_gap = 55

        for row, label in enumerate(menu_rows):
            y = base_y + row * row_gap

            # Highlight selected row
            if row == self.selected_index:
                # Draw a subtle selection bar behind the text
                bar_rect = pygame.Rect(0, 0, int(w * 0.70), 44)
                bar_rect.center = (w // 2, y)
                pygame.draw.rect(self.screen, (35, 35, 35), bar_rect, border_radius=8)

                text_color = (255, 255, 120)
            else:
                text_color = (230, 230, 230)

            self._draw_text(label, self.item_font, w // 2, y, color=text_color)
        
        # Draw SECRET PASSWORD option separately - only visible when selected
        if self.selected_index == 3:  # SECRET PASSWORD is index 3
            secret_y = int(h * 0.80)
            # Use smaller font (half size of other menu items)
            secret_font = pygame.font.Font(resource_path(os.path.join('assets', 'BAUHS93.ttf')), 20)
            # Render text to get its size for the rectangle
            secret_text_surf = secret_font.render("SECRET PASSWORD", True, (255, 255, 120))
            secret_text_rect = secret_text_surf.get_rect(center=(w // 2, secret_y))
            # Draw selection bar - just big enough to fit the text with some padding
            bar_padding = 8
            bar_rect = pygame.Rect(
                secret_text_rect.left - bar_padding,
                secret_text_rect.top - bar_padding,
                secret_text_rect.width + (bar_padding * 2),
                secret_text_rect.height + (bar_padding * 2)
            )
            pygame.draw.rect(self.screen, (35, 35, 35), bar_rect, border_radius=8)
            # Draw text
            self.screen.blit(secret_text_surf, secret_text_rect)

        # Hints at the bottom
        hint = "UP/DOWN: select    LEFT/RIGHT: change    ENTER: confirm    ESC: back"
        self._draw_text(hint, self.hint_font, w // 2, int(h * 0.92), color=(180, 180, 180))

        pygame.display.flip()

    # These functions help handle input to make the menu work:
    def _toggle_keydown(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            if self.play_sound_callback:
                self.play_sound_callback("menu_selection_confirm")
            return {"confirmed": False}

        if key in (pygame.K_UP, pygame.K_w):
            self.selected_index = (self.selected_index - 1) % 4  # 4 menu items total
            if self.play_sound_callback:
                self.play_sound_callback("menu_selection_change")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index = (self.selected_index + 1) % 4  # 4 menu items total
            if self.play_sound_callback:
                self.play_sound_callback("menu_selection_change")

        elif key in (pygame.K_LEFT, pygame.K_a):
            if self.selected_index == 0:
                self.starting_wave = max(1, self.starting_wave - 1)
                if self.play_sound_callback:
                    self.play_sound_callback("menu_selection_toggle")
            elif self.selected_index == 1:
                self.num_players = max(1, self.num_players - 1)
                if self.play_sound_callback:
                    self.play_sound_callback("menu_selection_toggle")

        elif key in (pygame.K_RIGHT, pygame.K_d):
            if self.selected_index == 0:
                self.starting_wave = min(5, self.starting_wave + 1)
                if self.play_sound_callback:
                    self.play_sound_callback("menu_selection_toggle")
            elif self.selected_index == 1:
                self.num_players = min(4, self.num_players + 1)
                if self.play_sound_callback:
                    self.play_sound_callback("menu_selection_toggle")

        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.play_sound_callback:
                self.play_sound_callback("menu_selection_confirm")
            if self.selected_index == 2:  # START GAME
                return {
                    "confirmed": True,
                    "starting_wave": self.starting_wave,
                    "num_players": self.num_players,
                }
            elif self.selected_index == 3:  # SECRET PASSWORD
                return {"secret_password": True}

        return None

    # ---------- Public runner ----------
    def run(self):
        """
        Main submenu loop.

        Step-by-step “blit text” inside _draw_text:
        1) font.render(text, antialias, color) -> returns a Surface (the text image)
        2) get_rect() to position it
        3) screen.blit(text_surface, text_rect)
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return {"confirmed": False}

                if event.type == pygame.KEYDOWN:
                    result = self._toggle_keydown(event.key)
                    if result is not None:
                        return result

            self._draw_menu()
            self.clock.tick(60)
