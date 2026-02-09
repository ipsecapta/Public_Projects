# menu_secret.py
# Secret password entry and secret wave menu

import pygame
import os
from base_settings import resource_path

class MenuSecretPassword:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, settings):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        
        font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
        try:
            self.title_font = pygame.font.Font(font_path, 72)
            self.item_font = pygame.font.Font(font_path, 40)
            self.input_font = pygame.font.Font(font_path, 36)
            self._update_menu_font_sizes()  # Scale hint font based on resolution
        except:
            self.title_font = pygame.font.SysFont(None, 72)
            self.item_font = pygame.font.SysFont(None, 40)
            self.input_font = pygame.font.SysFont(None, 36)
            self._update_menu_font_sizes()  # Scale hint font based on resolution
        
        self.password = "meowmeowMEOW"
        self.input_text = ""
        self.message = ""
        self.message_time = 0
    
    def _update_menu_font_sizes(self):
        """Update menu font sizes based on current resolution - scales proportionally to screen size"""
        # Base font size for Normal resolution (1200x580)
        base_size = 22
        # Reference resolution (Normal)
        reference_width = 1200
        # Scale factor is proportional to screen width relative to reference
        scale = self.settings.screen_width / reference_width
        font_size = int(base_size * scale)
        self.hint_font = pygame.font.SysFont(None, font_size)
        self.message_type = None  # "denied" or "unlocking"
        self.unlock_countdown = 5
        
        self._bg = None
        try:
            self._bg = pygame.image.load(self.settings.startscreen_path).convert()
        except Exception:
            self._bg = None
    
    def _draw_text(self, text, font, x, y, color=(255, 255, 255), center=True):
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surf, rect)
    
    def _draw_background(self):
        if self._bg:
            w, h = self.screen.get_size()
            scaled = pygame.transform.smoothscale(self._bg, (w, h))
            self.screen.blit(scaled, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
    
    def _draw_menu(self):
        w, h = self.screen.get_size()
        self._draw_background()
        
        self._draw_text("SECRET PASSWORD", self.title_font, w // 2, int(h * 0.15))
        
        # Password input field
        input_y = int(h * 0.35)
        input_label = self.hint_font.render("Enter Password:", True, (255, 255, 255))
        self.screen.blit(input_label, (w // 2 - 150, input_y - 30))
        
        # Input box
        input_box = pygame.Rect(w // 2 - 200, input_y, 400, 50)
        pygame.draw.rect(self.screen, (255, 255, 255), input_box, 2)
        
        # Display input text (masked)
        display_text = "*" * len(self.input_text)
        input_surf = self.input_font.render(display_text, True, (255, 255, 255))
        input_rect = input_surf.get_rect(center=input_box.center)
        self.screen.blit(input_surf, input_rect)
        
        # Messages
        now = pygame.time.get_ticks()
        if self.message_type == "denied" and now < self.message_time:
            # Flashing red ACCESS DENIED
            blink = ((now // 200) % 2 == 0)
            if blink:
                msg_rect = pygame.Rect(w // 2 - 150, int(h * 0.50), 300, 50)
                pygame.draw.rect(self.screen, (255, 0, 0), msg_rect)
            msg = self.item_font.render("ACCESS DENIED", True, (255, 255, 255))
            msg_rect = msg.get_rect(center=(w // 2, int(h * 0.525)))
            self.screen.blit(msg, msg_rect)
        
        elif self.message_type == "unlocking":
            # Flashing green UNLOCKING message with countdown
            blink = ((now // 200) % 2 == 0)
            if blink:
                msg_rect = pygame.Rect(w // 2 - 250, int(h * 0.50), 500, 50)
                pygame.draw.rect(self.screen, (0, 255, 0), msg_rect)
            countdown = max(0, self.unlock_countdown - ((now - self.message_time) // 1000))
            msg_text = f"UNLOCKING SECRET MENU IN {countdown}"
            msg = self.item_font.render(msg_text, True, (255, 255, 255))
            msg_rect = msg.get_rect(center=(w // 2, int(h * 0.525)))
            self.screen.blit(msg, msg_rect)
        
        hint = "Type password and press ENTER    ESC: back"
        self._draw_text(hint, self.hint_font, w // 2, int(h * 0.85), color=(180, 180, 180))
        pygame.display.flip()
    
    def run(self):
        """Returns True if password correct and countdown complete, None if cancelled"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # MenuSecretPassword doesn't have play_sound_callback, but check if it exists
                        if hasattr(self, 'play_sound_callback') and self.play_sound_callback:
                            self.play_sound_callback("menu_selection_confirm")
                        return None
                    
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if self.input_text == self.password:
                            # Start unlock countdown
                            self.message_type = "unlocking"
                            self.message_time = pygame.time.get_ticks()
                        else:
                            # Show denied message
                            self.message_type = "denied"
                            self.message_time = pygame.time.get_ticks() + 3000
                            self.input_text = ""  # Clear input
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    
                    else:
                        # Add character (only alphanumeric)
                        if event.unicode.isalnum():
                            self.input_text += event.unicode
            
            # Check if countdown complete
            if self.message_type == "unlocking":
                now = pygame.time.get_ticks()
                elapsed = (now - self.message_time) // 1000
                if elapsed >= 5:
                    return True
            
            self._draw_menu()
            self.clock.tick(60)


class MenuSecretWave:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, settings, play_sound_callback=None, stop_sound_callback=None):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.play_sound_callback = play_sound_callback
        self.stop_sound_callback = stop_sound_callback
        
        font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
        try:
            self.title_font = pygame.font.Font(font_path, 72)
            self.item_font = pygame.font.Font(font_path, 40)
            self.hint_font = pygame.font.SysFont(None, 22)
        except:
            self.title_font = pygame.font.SysFont(None, 72)
            self.item_font = pygame.font.SysFont(None, 40)
            self.hint_font = pygame.font.SysFont(None, 22)
        
        self.num_players = 1
        self.items = ["Number of Players", "START SECRET WAVE", "Back"]
        self.selected_index = 0
        self.current_wave_number = 0
        
        self._bg = None
        try:
            self._bg = pygame.image.load(self.settings.secret_menu_bg_path).convert()
        except Exception:
            self._bg = None
        
        # Store the music channel so we can stop it later
        self.music_channel = None
    
    def _draw_text(self, text, font, x, y, color=(255, 255, 255), center=True):
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surf, rect)
    
    def _draw_background(self):
        if self._bg:
            w, h = self.screen.get_size()
            scaled = pygame.transform.smoothscale(self._bg, (w, h))
            self.screen.blit(scaled, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
    
    def _draw_menu(self):
        w, h = self.screen.get_size()
        self._draw_background()
        
        self._draw_text("SECRET MENU", self.title_font, w // 2, int(h * 0.10))
        
        base_y = int(h * 0.35)
        gap = 60
        
        for i, item in enumerate(self.items):
            y = base_y + i * gap
            
            if i == self.selected_index:
                bar = pygame.Rect(0, 0, int(w * 0.50), 48)
                bar.center = (w // 2, y)
                pygame.draw.rect(self.screen, (35, 35, 35), bar, border_radius=10)
                color = (255, 255, 120)
            else:
                color = (230, 230, 230)
            
            if item == "Number of Players":
                display_text = f"Number of Players: < {self.num_players} >"
            else:
                display_text = item
            
            self._draw_text(display_text, self.item_font, w // 2, y, color=color)
        
        hint = "UP/DOWN: scroll    LEFT/RIGHT: change players    ENTER: select    ESC: back"
        self._draw_text(hint, self.hint_font, w // 2, int(h * 0.92), color=(180, 180, 180))
        pygame.display.flip()
    
    def run(self):
        """Returns config dict or None"""
        # Start playing secret menu music when menu opens (if music is enabled)
        if self.play_sound_callback and getattr(self.settings, 'music_enabled', True):
            self.music_channel = self.play_sound_callback("secret_menu_music", loop=-1)
        
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # Stop music before returning
                        if self.music_channel:
                            try:
                                self.music_channel.fadeout(2500)
                            except Exception:
                                if self.stop_sound_callback:
                                    self.stop_sound_callback(self.music_channel)
                        return None
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            # Play confirm sound before exiting
                            if self.play_sound_callback:
                                self.play_sound_callback("menu_selection_confirm")
                            # Stop music before returning
                            if self.music_channel:
                                try:
                                    self.music_channel.fadeout(2500)
                                except Exception:
                                    if self.stop_sound_callback:
                                        self.stop_sound_callback(self.music_channel)
                            return None
                        
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.selected_index = (self.selected_index - 1) % len(self.items)
                            if self.play_sound_callback:
                                self.play_sound_callback("menu_selection_change")
                        
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.selected_index = (self.selected_index + 1) % len(self.items)
                            if self.play_sound_callback:
                                self.play_sound_callback("menu_selection_change")
                        
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            if self.items[self.selected_index] == "Number of Players":
                                self.num_players = max(1, self.num_players - 1)
                                if self.play_sound_callback:
                                    self.play_sound_callback("menu_selection_toggle")
                        
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            if self.items[self.selected_index] == "Number of Players":
                                self.num_players = min(4, self.num_players + 1)
                                if self.play_sound_callback:
                                    self.play_sound_callback("menu_selection_toggle")
                        
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            if self.play_sound_callback:
                                self.play_sound_callback("menu_selection_confirm")
                            if self.items[self.selected_index] == "START SECRET WAVE":
                                # Stop music before starting game
                                if self.music_channel:
                                    try:
                                        self.music_channel.fadeout(2500)
                                    except Exception:
                                        if self.stop_sound_callback:
                                            self.stop_sound_callback(self.music_channel)
                                return {
                                    "num_players": self.num_players,
                                    "secret_wave": True
                                }
                            elif self.items[self.selected_index] == "Back":
                                # Stop music before returning
                                if self.music_channel:
                                    try:
                                        self.music_channel.fadeout(2500)
                                    except Exception:
                                        if self.stop_sound_callback:
                                            self.stop_sound_callback(self.music_channel)
                                return None
                
                self._draw_menu()
                self.clock.tick(60)
        finally:
            # Ensure music stops even if there's an exception
            if self.music_channel:
                try:
                    self.music_channel.fadeout(2500)
                except Exception:
                    if self.stop_sound_callback:
                        self.stop_sound_callback(self.music_channel)

