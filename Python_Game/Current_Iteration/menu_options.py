# menu_options.py
# Options menu: Powerups frequency, toggles, and difficulty

import pygame
import os
from base_settings import resource_path

class MenuOptions:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, settings, play_sound_callback=None):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.play_sound_callback = play_sound_callback

        font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf')) 
        try:
            self.title_font = pygame.font.Font(font_path, 72)
            self.column_title_font = pygame.font.Font(font_path, 54)  # 25% smaller than OPTIONS (72 * 0.75)
            self.item_font = pygame.font.Font(font_path, 36)  # 50% smaller than OPTIONS (72 * 0.5)
            self.subtitle_font = pygame.font.SysFont(None, 22)
            self.hint_font = pygame.font.SysFont(None, 22)
        except:
            self.title_font = pygame.font.SysFont(None, 72)
            self.column_title_font = pygame.font.SysFont(None, 54)
            self.item_font = pygame.font.SysFont(None, 36)
            self.subtitle_font = pygame.font.SysFont(None, 22)
            self.hint_font = pygame.font.SysFont(None, 22)

        # Powerup frequency options (High = 0.06, Normal = 0.022, Rare = 0.01)
        self.powerup_frequencies = [
            {"name": "High", "chance": 0.06},
            {"name": "Normal", "chance": 0.022},  # ~2.2%
            {"name": "Rare", "chance": 0.01}      # 1%
        ]
        # Find current frequency index
        self.current_freq_index = 0  # Default to Common
        for i, freq in enumerate(self.powerup_frequencies):
            if abs(freq["chance"] - settings.powerup_drop_chance) < 0.001:
                self.current_freq_index = i
                break

        # Difficulty options
        self.difficulties = ["Easy", "Normal", "Hard", "Kiddie"]
        self.current_difficulty_index = 0  # Default to Easy
        if hasattr(settings, "difficulty_mode"):
            try:
                self.current_difficulty_index = self.difficulties.index(settings.difficulty_mode.capitalize())
            except:
                pass

        # Menu items organized by column
        self.powerups_items = [
            "Powerups",  # Frequency selector
            "Nanites",
            "Squadrons", 
            "Shockwaves",
            "MAC (railgun): <i>coming soon</i>",  # Non-selectable
            "EMP: <i>coming soon</i>",  # Non-selectable
            "Ramming Shields: <i>coming soon</i>"  # Non-selectable
        ]
        self.features_items = [
            "Difficulty",
            "Lifepods",
            "Final Battle Wave: <i>coming... someday</i>"  # Non-selectable
        ]
        
        # Track which column (0 = Powerups, 1 = Features) and item index within column
        # -1 means column title is selected, 0+ means item index within column
        self.selected_column = 0  # 0 = Powerups, 1 = Features
        self.selected_index = -1  # -1 = column title selected, 0+ = item index

        # Optional background image
        self._bg = None
        try:
            self._bg = pygame.image.load(self.settings.startscreen_path).convert()
        except Exception:
            self._bg = None

        # Powerup icons (static) for Options menu (25x25)
        self.powerup_icons = {}
        icon_size = (25, 25)
        icon_paths = {
            "Nanites": os.path.join("img", "powerup_nanite.png"),
            "Squadrons": os.path.join("img", "powerup_squadron.png"),
            "Shockwaves": os.path.join("img", "powerup_shockwave.png"),
        }
        for label, rel_path in icon_paths.items():
            try:
                img = pygame.image.load(resource_path(rel_path)).convert_alpha()
                self.powerup_icons[label] = pygame.transform.smoothscale(img, icon_size)
            except Exception:
                self.powerup_icons[label] = None

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

        # Main title
        self._draw_text("OPTIONS", self.title_font, w // 2, int(h * 0.10))

        # Column layout: two columns side by side
        column_width = w * 0.40
        left_column_x = w * 0.25
        right_column_x = w * 0.75
        base_y = int(h * 0.25)
        gap = 45

        # Draw Powerups column
        # Check if Powerups title is selected
        powerups_title_selected = (self.selected_column == 0 and self.selected_index == -1)
        if powerups_title_selected:
            bar = pygame.Rect(0, 0, int(column_width), 50)
            bar.center = (left_column_x, base_y)
            pygame.draw.rect(self.screen, (35, 35, 35), bar, border_radius=10)
            title_color = (255, 255, 120)
        else:
            title_color = (255, 255, 255)
        self._draw_text("Powerups", self.column_title_font, left_column_x, base_y, color=title_color)
        powerups_start_y = base_y + 60
        
        for i, item in enumerate(self.powerups_items):
            y = powerups_start_y + i * gap
            
            # Check if this item is selected
            is_selected = (self.selected_column == 0 and i == self.selected_index)
            
            # Check if item is selectable (not "coming soon" items)
            is_selectable = not ("coming soon" in item.lower() or "coming... someday" in item.lower())
            
            if is_selected and is_selectable:
                bar = pygame.Rect(0, 0, int(column_width), 40)
                bar.center = (left_column_x, y)
                pygame.draw.rect(self.screen, (35, 35, 35), bar, border_radius=10)
                color = (255, 255, 120)
            elif is_selected:
                # Selected but not selectable - dimmed highlight
                color = (150, 150, 150)
            elif not is_selectable:
                color = (120, 120, 120)  # Dimmed for non-selectable items
            else:
                color = (230, 230, 230)

            # Format display text based on item
            if item == "Powerups":
                freq_name = self.powerup_frequencies[self.current_freq_index]["name"]
                display_text = f"Powerups: < {freq_name} >"
            elif item == "Nanites":
                status = "ON" if self.settings.powerup_enable_nanites else "OFF"
                display_text = f"Nanites: < {status} >"
            elif item == "Squadrons":
                status = "ON" if self.settings.powerup_enable_squadron else "OFF"
                display_text = f"Squadrons: < {status} >"
            elif item == "Shockwaves":
                status = "ON" if self.settings.powerup_enable_shockwave else "OFF"
                display_text = f"Shockwaves: < {status} >"
            else:
                # Non-selectable items or other items
                display_text = item.replace("<i>", "").replace("</i>", "")  # Remove HTML-like tags for display

            # Draw icon (left of text) for specific powerups
            if item in ("Nanites", "Squadrons", "Shockwaves"):
                text_surf = self.item_font.render(display_text, True, color)
                text_rect = text_surf.get_rect()
                text_rect.center = (left_column_x, y)

                icon = self.powerup_icons.get(item)
                if icon is not None:
                    icon_gap = 10
                    icon_x = text_rect.left - icon_gap - 25
                    icon_y = y - (25 // 2)
                    self.screen.blit(icon, (icon_x, icon_y))

                self.screen.blit(text_surf, text_rect)
            else:
                self._draw_text(display_text, self.item_font, left_column_x, y, color=color)

        # Draw Features column
        # Check if Features title is selected
        features_title_selected = (self.selected_column == 1 and self.selected_index == -1)
        if features_title_selected:
            bar = pygame.Rect(0, 0, int(column_width), 50)
            bar.center = (right_column_x, base_y)
            pygame.draw.rect(self.screen, (35, 35, 35), bar, border_radius=10)
            title_color = (255, 255, 120)
        else:
            title_color = (255, 255, 255)
        self._draw_text("Features", self.column_title_font, right_column_x, base_y, color=title_color)
        features_start_y = base_y + 60
        
        for i, item in enumerate(self.features_items):
            y = features_start_y + i * gap
            
            # Check if this item is selected
            is_selected = (self.selected_column == 1 and i == self.selected_index)
            
            # Check if item is selectable
            is_selectable = not ("coming... someday" in item.lower())
            
            if is_selected and is_selectable:
                bar = pygame.Rect(0, 0, int(column_width), 40)
                bar.center = (right_column_x, y)
                pygame.draw.rect(self.screen, (35, 35, 35), bar, border_radius=10)
                color = (255, 255, 120)
            elif is_selected:
                color = (150, 150, 150)
            elif not is_selectable:
                color = (120, 120, 120)
            else:
                color = (230, 230, 230)

            # Format display text based on item
            if item == "Difficulty":
                diff_name = self.difficulties[self.current_difficulty_index]
                display_text = f"Difficulty: < {diff_name} >"
            elif item == "Lifepods":
                status = "ON" if getattr(self.settings, 'enable_escape_pods', True) else "OFF"
                display_text = f"Lifepods: < {status} >"
            else:
                display_text = item.replace("<i>", "").replace("</i>", "")

            self._draw_text(display_text, self.item_font, right_column_x, y, color=color)

        hint = "UP/DOWN: scroll    LEFT/RIGHT: toggle/change/switch columns    TAB: switch columns    ENTER/ESC: back"
        self._draw_text(hint, self.hint_font, w // 2, int(h * 0.92), color=(180, 180, 180))
        pygame.display.flip()

    def _apply_difficulty(self):
        """Apply difficulty settings to spawn intervals and speeds"""
        diff = self.difficulties[self.current_difficulty_index]
        
        # Store base fire intervals and bullet speed if not already stored (do this once)
        if not hasattr(self.settings, '_base_alien1_min_fire_interval'):
            self.settings._base_alien1_min_fire_interval = self.settings.alien1_min_fire_interval
            self.settings._base_alien1_max_fire_interval = self.settings.alien1_max_fire_interval
            self.settings._base_alien2_min_fire_interval = self.settings.alien2_min_fire_interval
            self.settings._base_alien2_max_fire_interval = self.settings.alien2_max_fire_interval
            self.settings._base_alien3_min_fire_interval = self.settings.alien3_min_fire_interval
            self.settings._base_alien3_max_fire_interval = self.settings.alien3_max_fire_interval
            self.settings._base_destroyer_min_fire_interval = self.settings.destroyer_min_fire_interval
            self.settings._base_destroyer_max_fire_interval = self.settings.destroyer_max_fire_interval
            self.settings._base_cruiser_min_fire_interval = self.settings.cruiser_min_fire_interval
            self.settings._base_cruiser_max_fire_interval = self.settings.cruiser_max_fire_interval
            self.settings._base_laztanker_min_fire_interval = self.settings.laztanker_min_fire_interval
            self.settings._base_laztanker_max_fire_interval = self.settings.laztanker_max_fire_interval
            self.settings._base_alien_bullet_speed = self.settings.alien_bullet_speed
        
        # Base values (Easy - these are the default values from base_settings.py)
        base_spawn_intervals = {
            "alien2_min": 5000, "alien2_max": 10000,
            "alien3_min": 10000, "alien3_max": 18000,
            "alien4_min": 18000, "alien4_max": 18001,
            "destroyer_min": 30000, "destroyer_max": 40000,
            "cruiser_min": 40000, "cruiser_max": 80000,
            "laztanker_min": 80000, "laztanker_max": 120000
        }
        
        base_speeds = {
            "alien1_strafe": 0.5,
            "alien2": 0.22,
            "alien3": 2.3,
            "alien4": 1.65,
            "destroyer": 0.5,
            "cruiser": 0.25,
            "laztanker": 0.25,
            "fleet_advance": 0.02
        }
        
        if diff == "Normal":
            # Spawn faster, move faster
            spawn_scale = 0.85  # 15% faster spawning (lower interval = faster)
            speed_scale = 1.15   # 15% faster movement
        elif diff == "Hard":
            # Spawn same as Normal, move faster
            spawn_scale = 0.85  # Same as Normal
            speed_scale = 1.25  # 25% faster movement (10% faster than Normal)
        elif diff == "Kiddie":
            # Same stats as Easy mode
            spawn_scale = 1.4   # 40% slower spawning (longer intervals = easier)
            speed_scale = 0.85   # 15% slower movement (easier)
            fire_scale = 1.25    # 25% slower firing (longer intervals = easier)
            bullet_speed_scale = 0.85  # 15% slower alien bullets (easier to dodge)
        else:  # Easy
            spawn_scale = 1.4   # 40% slower spawning (longer intervals = easier) - increased from 1.3
            speed_scale = 0.85   # 15% slower movement (easier)
            fire_scale = 1.25    # 25% slower firing (longer intervals = easier) - new for easy mode
            bullet_speed_scale = 0.85  # 15% slower alien bullets (easier to dodge) - new for easy mode

        # Apply to spawn intervals (lower = faster)
        self.settings.alien2_min_spawn_interval = int(base_spawn_intervals["alien2_min"] * spawn_scale)
        self.settings.alien2_max_spawn_interval = int(base_spawn_intervals["alien2_max"] * spawn_scale)
        self.settings.alien3_min_spawn_interval = int(base_spawn_intervals["alien3_min"] * spawn_scale)
        self.settings.alien3_max_spawn_interval = int(base_spawn_intervals["alien3_max"] * spawn_scale)
        self.settings.alien4_min_spawn_interval = int(base_spawn_intervals["alien4_min"] * spawn_scale)
        self.settings.alien4_max_spawn_interval = int(base_spawn_intervals["alien4_max"] * spawn_scale)
        self.settings.destroyer_min_spawn_interval = int(base_spawn_intervals["destroyer_min"] * spawn_scale)
        self.settings.destroyer_max_spawn_interval = int(base_spawn_intervals["destroyer_max"] * spawn_scale)
        self.settings.cruiser_min_spawn_interval = int(base_spawn_intervals["cruiser_min"] * spawn_scale)
        self.settings.cruiser_max_spawn_interval = int(base_spawn_intervals["cruiser_max"] * spawn_scale)
        self.settings.laztanker_min_spawn_interval = int(base_spawn_intervals["laztanker_min"] * spawn_scale)
        self.settings.laztanker_max_spawn_interval = int(base_spawn_intervals["laztanker_max"] * spawn_scale)

        # Apply to movement speeds
        self.settings.alien1_strafe_speed = base_speeds["alien1_strafe"] * speed_scale
        self.settings.alien2_speed = base_speeds["alien2"] * speed_scale
        self.settings.alien3_speed = base_speeds["alien3"] * speed_scale
        self.settings.alien4_speed = base_speeds["alien4"] * speed_scale
        self.settings.destroyer_speed = base_speeds["destroyer"] * speed_scale
        self.settings.cruiser_speed = base_speeds["cruiser"] * speed_scale
        self.settings.laztanker_speed = base_speeds["laztanker"] * speed_scale
        self.settings.fleet_advance_speed = base_speeds["fleet_advance"] * speed_scale

        # Apply fire interval scaling for Easy and Kiddie modes (make aliens fire less frequently)
        if diff in ("Easy", "Kiddie"):
            # Apply fire interval scaling (longer intervals = slower firing)
            self.settings.alien1_min_fire_interval = int(self.settings._base_alien1_min_fire_interval * fire_scale)
            self.settings.alien1_max_fire_interval = int(self.settings._base_alien1_max_fire_interval * fire_scale)
            self.settings.alien2_min_fire_interval = int(self.settings._base_alien2_min_fire_interval * fire_scale)
            self.settings.alien2_max_fire_interval = int(self.settings._base_alien2_max_fire_interval * fire_scale)
            self.settings.alien3_min_fire_interval = int(self.settings._base_alien3_min_fire_interval * fire_scale)
            self.settings.alien3_max_fire_interval = int(self.settings._base_alien3_max_fire_interval * fire_scale)
            self.settings.destroyer_min_fire_interval = int(self.settings._base_destroyer_min_fire_interval * fire_scale)
            self.settings.destroyer_max_fire_interval = int(self.settings._base_destroyer_max_fire_interval * fire_scale)
            self.settings.cruiser_min_fire_interval = int(self.settings._base_cruiser_min_fire_interval * fire_scale)
            self.settings.cruiser_max_fire_interval = int(self.settings._base_cruiser_max_fire_interval * fire_scale)
            self.settings.laztanker_min_fire_interval = int(self.settings._base_laztanker_min_fire_interval * fire_scale)
            self.settings.laztanker_max_fire_interval = int(self.settings._base_laztanker_max_fire_interval * fire_scale)
            
            # Apply alien bullet speed scaling (slower bullets = easier to dodge)
            if not hasattr(self.settings, '_base_alien_bullet_speed'):
                self.settings._base_alien_bullet_speed = self.settings.alien_bullet_speed
            self.settings.alien_bullet_speed = self.settings._base_alien_bullet_speed * bullet_speed_scale
        elif diff in ("Normal", "Hard"):
            # Restore base fire intervals and bullet speed for Normal/Hard
            if hasattr(self.settings, '_base_alien1_min_fire_interval'):
                self.settings.alien1_min_fire_interval = self.settings._base_alien1_min_fire_interval
                self.settings.alien1_max_fire_interval = self.settings._base_alien1_max_fire_interval
                self.settings.alien2_min_fire_interval = self.settings._base_alien2_min_fire_interval
                self.settings.alien2_max_fire_interval = self.settings._base_alien2_max_fire_interval
                self.settings.alien3_min_fire_interval = self.settings._base_alien3_min_fire_interval
                self.settings.alien3_max_fire_interval = self.settings._base_alien3_max_fire_interval
                self.settings.destroyer_min_fire_interval = self.settings._base_destroyer_min_fire_interval
                self.settings.destroyer_max_fire_interval = self.settings._base_destroyer_max_fire_interval
                self.settings.cruiser_min_fire_interval = self.settings._base_cruiser_min_fire_interval
                self.settings.cruiser_max_fire_interval = self.settings._base_cruiser_max_fire_interval
                self.settings.laztanker_min_fire_interval = self.settings._base_laztanker_min_fire_interval
                self.settings.laztanker_max_fire_interval = self.settings._base_laztanker_max_fire_interval
            if hasattr(self.settings, '_base_alien_bullet_speed'):
                self.settings.alien_bullet_speed = self.settings._base_alien_bullet_speed

        self.settings.difficulty_mode = diff.lower()

    def run(self):
        """Returns updated settings or None if cancelled"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_confirm")
                        return None

                    # Get current column's items
                    current_items = self.powerups_items if self.selected_column == 0 else self.features_items
                    
                    # Handle column title selection (-1) vs item selection (0+)
                    if self.selected_index == -1:
                        # Column title is selected
                        if event.key in (pygame.K_UP, pygame.K_w):
                            # Move to last selectable item in current column
                            for i in range(len(current_items) - 1, -1, -1):
                                item = current_items[i]
                                if not ("coming soon" in item.lower() or "coming... someday" in item.lower()):
                                    self.selected_index = i
                                    break
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            # Move to first selectable item in current column
                            for i in range(len(current_items)):
                                item = current_items[i]
                                if not ("coming soon" in item.lower() or "coming... someday" in item.lower()):
                                    self.selected_index = i
                                    break
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            # Switch to other column's title
                            self.selected_column = 1 - self.selected_column
                            self.selected_index = -1
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            # Switch to other column's title
                            self.selected_column = 1 - self.selected_column
                            self.selected_index = -1
                    else:
                        # An item is selected
                        current_item = current_items[self.selected_index]
                        
                        # Check if current item is selectable
                        is_selectable = not ("coming soon" in current_item.lower() or "coming... someday" in current_item.lower())

                        if event.key in (pygame.K_UP, pygame.K_w):
                            # Move up within current column, skipping non-selectable items
                            old_index = self.selected_index
                            new_index = self.selected_index - 1
                            while new_index >= 0:
                                item = current_items[new_index]
                                if not ("coming soon" in item.lower() or "coming... someday" in item.lower()):
                                    self.selected_index = new_index
                                    break
                                new_index -= 1
                            if new_index < 0:
                                # Wrap to column title
                                self.selected_index = -1
                            # Play sound if selection actually changed
                            if self.selected_index != old_index and self.play_sound_callback:
                                self.play_sound_callback("menu_selection_change")

                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            # Move down within current column, skipping non-selectable items
                            old_index = self.selected_index
                            new_index = self.selected_index + 1
                            while new_index < len(current_items):
                                item = current_items[new_index]
                                if not ("coming soon" in item.lower() or "coming... someday" in item.lower()):
                                    self.selected_index = new_index
                                    break
                                new_index += 1
                            if new_index >= len(current_items):
                                # Wrap to column title
                                self.selected_index = -1
                            # Play sound if selection actually changed
                            if self.selected_index != old_index and self.play_sound_callback:
                                self.play_sound_callback("menu_selection_change")

                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            if is_selectable:
                                # Handle toggle/change for selectable items
                                if current_item == "Powerups":
                                    self.current_freq_index = (self.current_freq_index - 1) % len(self.powerup_frequencies)
                                    self.settings.powerup_drop_chance = self.powerup_frequencies[self.current_freq_index]["chance"]
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Nanites":
                                    self.settings.powerup_enable_nanites = not self.settings.powerup_enable_nanites
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Squadrons":
                                    self.settings.powerup_enable_squadron = not self.settings.powerup_enable_squadron
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Shockwaves":
                                    self.settings.powerup_enable_shockwave = not self.settings.powerup_enable_shockwave
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Difficulty":
                                    self.current_difficulty_index = (self.current_difficulty_index - 1) % len(self.difficulties)
                                    self._apply_difficulty()
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Lifepods":
                                    self.settings.enable_escape_pods = not getattr(self.settings, 'enable_escape_pods', True)
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")

                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            if is_selectable:
                                # Handle toggle/change for selectable items
                                if current_item == "Powerups":
                                    self.current_freq_index = (self.current_freq_index + 1) % len(self.powerup_frequencies)
                                    self.settings.powerup_drop_chance = self.powerup_frequencies[self.current_freq_index]["chance"]
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Nanites":
                                    self.settings.powerup_enable_nanites = not self.settings.powerup_enable_nanites
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Squadrons":
                                    self.settings.powerup_enable_squadron = not self.settings.powerup_enable_squadron
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Shockwaves":
                                    self.settings.powerup_enable_shockwave = not self.settings.powerup_enable_shockwave
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Difficulty":
                                    self.current_difficulty_index = (self.current_difficulty_index + 1) % len(self.difficulties)
                                    self._apply_difficulty()
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")
                                elif current_item == "Lifepods":
                                    self.settings.enable_escape_pods = not getattr(self.settings, 'enable_escape_pods', True)
                                    if self.play_sound_callback:
                                        self.play_sound_callback("menu_selection_toggle")

                    # TAB key to switch columns (alternative to arrow keys on titles)
                    if event.key == pygame.K_TAB:
                        self.selected_column = 1 - self.selected_column
                        self.selected_index = -1  # Select the column title

                    # ENTER key confirms and returns
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_confirm")
                        return None

            self._draw_menu()
            self.clock.tick(60)


