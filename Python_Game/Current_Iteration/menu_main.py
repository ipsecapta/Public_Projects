# menu_main.py
#This handles displaying the main menu.
# Top-level menu: START / OPTIONS / SETTINGS.
# For now:
#  - START launches MenuStart and returns its chosen config.

import pygame
from menu2_start import MenuStart
from menu_settings import MenuSettings
from menu_options import MenuOptions
from menu_secret import MenuSecretPassword, MenuSecretWave
import os
from base_settings import resource_path

class MenuMain:
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
            self._update_menu_font_sizes()  # Scale subtitle and hint fonts based on resolution
        except:
            self.title_font = pygame.font.SysFont(None, 72)
            self.item_font = pygame.font.SysFont(None, 40)
            self._update_menu_font_sizes()  # Scale subtitle and hint fonts based on resolution

        self.items = ["START", "OPTIONS", "SETTINGS", "QUIT"]
        self.selected_index = 0
        
        # Store the music channel so we can stop it later
        self.music_channel = None
    
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

        # Optional background image (loaded once)
        self._bg = None
        try:
            self._bg = pygame.image.load(self.settings.startscreen_path).convert()
        except Exception:
            self._bg = None

    def _draw_text(self, text, font, x, y, color=(255, 255, 255), center=True):
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        rect.center = (x, y) if center else rect.topleft
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

        self._draw_text("SPACE INVADER DEFENSE!", self.title_font, w // 2, int(h * 0.10))
        self._draw_text("To my nieces and nephews: Enjoy the game!", self.subtitle_font, w // 2, int(h * 0.18))
        self._draw_text("Latest Updates: More detailed (and fun) Victory/Defeat Credits, Background music included. Tell me about any glitches that happen!",  self.subtitle_font, w // 2, int(h * 0.22))
        self._draw_text("I've finished the art for the Railgun/MAC powerups - just have to program the spaceships!",  self.subtitle_font, w // 2, int(h * 0.26))
        self._draw_text("And if you have ideas for MORE or DIFFERENT sounds... just record them, and I'll have a listen to see where they might fit!", self.subtitle_font, w // 2, int(h * 0.30))

        base_y = int(h * 0.38)
        gap = 60

        for i, item in enumerate(self.items):
            y = base_y + i * gap

            if i == self.selected_index:
                bar = pygame.Rect(0, 0, int(w * 0.45), 48)
                bar.center = (w // 2, y)
                pygame.draw.rect(self.screen, (35, 35, 35), bar, border_radius=10)
                color = (255, 255, 120)
            else:
                color = (230, 230, 230)

            self._draw_text(item, self.item_font, w // 2, y, color=color)

        hint = "UP/DOWN: scroll through menu    ENTER: select    ESC: quit"
        self._draw_text(hint, self.hint_font, w // 2, int(h * 0.92), color=(180, 180, 180))

        pygame.display.flip()

    def _coming_soon(self, title: str):
        # Simple placeholder screen
        w, h = self.screen.get_size()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    # any key returns
                    return

            self._draw_background()
            self._draw_text(title, self.title_font, w // 2, int(h * 0.35))
            self._draw_text("Coming soon. Press any key.", self.item_font, w // 2, int(h * 0.52))
            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        """
        Returns:
          - None if user quits the menu (ESC or QUIT)
          - dict if user chooses START and confirms:
                {"starting_wave": 1..5, "num_players": 1..4}
        """
        # Start playing menu music when menu opens
        if self.play_sound_callback:
            self.music_channel = self.play_sound_callback("menu_music", loop=-1)
        
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # Fade out menu music before returning
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
                            # Fade out menu music before returning
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

                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            if self.play_sound_callback:
                                self.play_sound_callback("menu_selection_confirm")
                            
                            choice = self.items[self.selected_index]

                            if choice == "START":
                                start_menu = MenuStart(self.screen, self.clock, self.settings, play_sound_callback=self.play_sound_callback)
                                result = start_menu.run()
                                if result.get("confirmed"):
                                    # Stop music before starting game
                                    if self.music_channel:
                                        # Fade out menu music like other background tracks (2.5s)
                                        try:
                                            self.music_channel.fadeout(2500)
                                        except Exception:
                                            # Fallback to existing stop callback if fadeout unavailable
                                            if self.stop_sound_callback:
                                                self.stop_sound_callback(self.music_channel)
                                    return {
                                        "starting_wave": result["starting_wave"],
                                        "num_players": result["num_players"],
                                    }
                                elif result.get("secret_password"):
                                    # Password entry
                                    password_menu = MenuSecretPassword(self.screen, self.clock, self.settings)
                                    if password_menu.run():
                                        # Password correct, stop main menu music before showing secret wave menu
                                        if self.music_channel:
                                            try:
                                                self.music_channel.fadeout(2500)
                                            except Exception:
                                                if self.stop_sound_callback:
                                                    self.stop_sound_callback(self.music_channel)
                                            self.music_channel = None
                                        # Show secret wave menu (it will start its own music)
                                        secret_menu = MenuSecretWave(self.screen, self.clock, self.settings, 
                                                                     self.play_sound_callback, self.stop_sound_callback)
                                        secret_result = secret_menu.run()
                                        if secret_result and secret_result.get("secret_wave"):
                                            # Secret menu music already stopped by MenuSecretWave
                                            return secret_result
                                        # If user went back from secret menu, restart main menu music
                                        if self.play_sound_callback:
                                            self.music_channel = self.play_sound_callback("menu_music", loop=-1)
                                # else go back to main menu

                            elif choice == "OPTIONS":
                                options_menu = MenuOptions(self.screen, self.clock, self.settings, play_sound_callback=self.play_sound_callback)
                                options_menu.run()
                                # Options are applied directly to settings, no return needed

                            elif choice == "SETTINGS":
                                settings_menu = MenuSettings(self.screen, self.clock, self.settings, play_sound_callback=self.play_sound_callback, stop_sound_callback=self.stop_sound_callback)
                                result = settings_menu.run()
                                if result and result.get("resolution_changed"):
                                    # Screen was resized, update our screen reference
                                    self.screen = pygame.display.get_surface()
                                # Stop menu music if music was toggled off
                                if not getattr(self.settings, 'music_enabled', True) and self.music_channel:
                                    try:
                                        self.music_channel.fadeout(2500)
                                    except Exception:
                                        if self.stop_sound_callback:
                                            self.stop_sound_callback(self.music_channel)
                                    self.music_channel = None
                                # Restart menu music if music was toggled back on
                                elif getattr(self.settings, 'music_enabled', True) and self.play_sound_callback:
                                    if not self.music_channel or not self.music_channel.get_busy():
                                        self.music_channel = self.play_sound_callback("menu_music", loop=-1)

                            elif choice == "QUIT":
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
