# menu_settings.py
# Settings menu: Resolution and Player Keys display

import pygame
import os
from base_settings import resource_path

class MenuSettings:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, settings, play_sound_callback=None, stop_sound_callback=None):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.play_sound_callback = play_sound_callback
        self.stop_sound_callback = stop_sound_callback
        self._keys_changed = False

        font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf')) 
        try:
            self.title_font = pygame.font.Font(font_path, 72)
            self.item_font = pygame.font.Font(font_path, 40)
            self._update_menu_font_sizes()  # Scale subtitle, hint, and key fonts based on resolution
        except:
            self.title_font = pygame.font.SysFont(None, 72)
            self.item_font = pygame.font.SysFont(None, 40)
            self._update_menu_font_sizes()  # Scale subtitle, hint, and key fonts based on resolution

        # Italic fonts for key listing labels (e.g., "Up:", "Down:", etc.)
        # Use SysFont so we can reliably request italic even if the custom font has no italic face.
        self.item_font_italic = pygame.font.SysFont(None, 40, italic=True)

        self.items = ["Resolution", "Sound", "Player Keys", "Back"]  # "Music" commented out temporarily
        self.selected_index = 0
        
        # Track sound and music enabled states
        self.sound_enabled = settings.sounds_enabled
        self.music_enabled = getattr(settings, 'music_enabled', True)  # Default to True if not set

        # Resolution options (current 1200x580 is "Normal", middle option)
        self.resolutions = [
            {"name": "Small", "width": 1000, "height": 483},  # ~0.83x scale
            {"name": "Normal", "width": 1200, "height": 580},   # current (1.0x)
            {"name": "Large", "width": 1440, "height": 696},  # ~1.2x scale
            {"name": "Biggest", "width": 1920, "height": 928},  # ~1.6x scale
            {"name": "Ultra", "width": 2560, "height": 1440}  # ~2.13x scale
    ]
        # Find current resolution index
        self.current_res_index = 1  # Default to "Normal" (matches base_settings default)
        for i, res in enumerate(self.resolutions):
            if res["width"] == settings.screen_width and res["height"] == settings.screen_height:
                self.current_res_index = i
                break

        # Optional background image
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

        self._draw_text("SETTINGS", self.title_font, w // 2, int(h * 0.10))

        base_y = int(h * 0.30)
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

            if item == "Resolution":
                current_res = self.resolutions[self.current_res_index]
                display_text = f"Resolution (ENTER to select): < {current_res['name']} ({current_res['width']}x{current_res['height']}) >"
            elif item == "Sound":
                status = "ON" if self.sound_enabled else "OFF"
                display_text = f"Sound: < {status} >"
            # elif item == "Music":
            #     status = "ON" if self.music_enabled else "OFF"
            #     display_text = f"Music: < {status} >"
            elif item == "Player Keys":
                display_text = "Player Keys (Press ENTER to view)"
            else:
                display_text = item

            self._draw_text(display_text, self.item_font, w // 2, y, color=color)

        hint = "UP/DOWN: scroll    LEFT/RIGHT: change resolution/sound    ENTER: select/view    ESC: back"
        self._draw_text(hint, self.hint_font, w // 2, int(h * 0.92), color=(180, 180, 180))
        
        # Resolution change instruction note
        note_text = "NOTE: When resolution is selected, toggle left or right, and hit enter to change. Do not maximize the window."
        note_y = int(h * 0.85)
        self._draw_text(note_text, self.hint_font, w // 2, note_y, color=(150, 150, 150))
        
        pygame.display.flip()
    
    def _update_menu_font_sizes(self):
        """Update menu font sizes based on current resolution - scales proportionally to screen size"""
        # Base font sizes for Normal resolution (1200x580)
        base_hint_size = 22
        base_key_size = 20
        # Reference resolution (Normal)
        reference_width = 1200
        # Scale factor is proportional to screen width relative to reference
        scale = self.settings.screen_width / reference_width
        hint_font_size = int(base_hint_size * scale)
        key_font_size = int(base_key_size * scale)
        self.subtitle_font = pygame.font.SysFont(None, hint_font_size)
        self.hint_font = pygame.font.SysFont(None, hint_font_size)
        self.key_font = pygame.font.SysFont(None, key_font_size)
        self.key_font_italic = pygame.font.SysFont(None, key_font_size, italic=True)

    def _blit_segment_line(self, x: int, y: int, segments):
        """Blit a sequence of (text, font, color) segments left-to-right starting at (x, y)."""
        cur_x = x
        for text, font, color in segments:
            surf = font.render(text, True, color)
            self.screen.blit(surf, (cur_x, y))
            cur_x += surf.get_width()

    def _format_key_name(self, key_const: int) -> str:
        """
        Human-readable key label for UI.\n
        Note: this does NOT affect gameplay; it is display-only.
        """
        try:
            name = pygame.key.name(key_const)
        except Exception:
            return str(key_const)

        n = (name or "").strip().lower()
        if not n:
            return str(key_const)

        # Slight cleanup for common special keys
        specials = {
            "escape": "Escape",
            "return": "Enter",
            "kp enter": "Enter",
            "backspace": "Backspace",
            "space": "Space",
            "left ctrl": "Left Ctrl",
            "right ctrl": "Right Ctrl",
            "left shift": "Left Shift",
            "right shift": "Right Shift",
            "caps lock": "Caps Lock",
            "tab": "Tab",
            "backslash": "\\",
            "backquote": "`",
            "delete": "Delete",
        }
        if n in specials:
            return specials[n]

        # Single character keys (letters, digits, punctuation)
        if len(n) == 1:
            return n.upper()

        return n.title()

    def _draw_player_keys_overview(self, selected_index: int):
        """2x2 grid of player keybindings, plus a selectable 'Change Player N Keyset?' row under each player."""
        w, h = self.screen.get_size()
        self._draw_background()
        self._draw_text("PLAYER CONTROLS", self.title_font, w // 2, int(h * 0.08))

        # 2x2 grid layout
        grid_start_y = int(h * 0.20)
        grid_end_y = int(h * 0.85)
        grid_height = grid_end_y - grid_start_y

        grid_start_x = int(w * 0.10)
        grid_end_x = int(w * 0.90)
        grid_width = grid_end_x - grid_start_x

        cell_width = grid_width // 2
        cell_height = grid_height // 2
        cell_center_x1 = grid_start_x + cell_width // 2
        cell_center_x2 = grid_start_x + cell_width + cell_width // 2
        cell_center_y1 = grid_start_y + cell_height // 2
        cell_center_y2 = grid_start_y + cell_height + cell_height // 2

        grid_positions = [
            (cell_center_x1, cell_center_y1),  # Player 1
            (cell_center_x2, cell_center_y1),  # Player 2
            (cell_center_x1, cell_center_y2),  # Player 3
            (cell_center_x2, cell_center_y2),  # Player 4
        ]

        line_height = int(22 * (self.settings.screen_width / 1200))
        start_offset = -int(75 * (self.settings.screen_width / 1200))

        for player_num in range(1, 5):
            keys = getattr(self.settings, f"player{player_num}_keys")
            center_x, center_y = grid_positions[player_num - 1]
            current_y = center_y + start_offset

            # Player header (to the LEFT of the key listing, not above it)
            # Keep the same font/size as before (self.item_font).
            title_x = int(center_x - (cell_width * 0.48))
            lines_x = int(center_x - (cell_width * 0.10))
            self._draw_text(f"PLAYER {player_num}:", self.item_font, title_x, current_y, color=(255, 255, 120), center=False)

            # Movement keys
            value_color = (230, 230, 230)
            self._blit_segment_line(
                lines_x,
                current_y,
                [
                    ("Up:", self.key_font_italic, value_color),
                    (" ", self.key_font, value_color),
                    (self._format_key_name(keys["up"]), self.key_font, value_color),
                    ("   ", self.key_font, value_color),
                    ("Down:", self.key_font_italic, value_color),
                    (" ", self.key_font, value_color),
                    (self._format_key_name(keys["down"]), self.key_font, value_color),
                ],
            )
            current_y += line_height

            self._blit_segment_line(
                lines_x,
                current_y,
                [
                    ("Left:", self.key_font_italic, value_color),
                    (" ", self.key_font, value_color),
                    (self._format_key_name(keys["left"]), self.key_font, value_color),
                    ("   ", self.key_font, value_color),
                    ("Right:", self.key_font_italic, value_color),
                    (" ", self.key_font, value_color),
                    (self._format_key_name(keys["right"]), self.key_font, value_color),
                ],
            )
            current_y += int(line_height * 1.5)

            # Fire
            self._blit_segment_line(
                lines_x,
                current_y,
                [
                    ("Fire:", self.key_font_italic, value_color),
                    (" ", self.key_font, value_color),
                    (self._format_key_name(keys["fire"]), self.key_font, value_color),
                ],
            )
            current_y += int(line_height * 1.5)

            # Powerups
            self._blit_segment_line(
                lines_x,
                current_y,
                [
                    ("Squadron:", self.key_font_italic, value_color),
                    (" ", self.key_font, value_color),
                    (self._format_key_name(keys["squadron"]), self.key_font, value_color),
                    ("   ", self.key_font, value_color),
                    ("Nanites:", self.key_font_italic, value_color),
                    (" ", self.key_font, value_color),
                    (self._format_key_name(keys["nanites"]), self.key_font, value_color),
                ],
            )
            current_y += line_height

            self._blit_segment_line(
                lines_x,
                current_y,
                [
                    ("Shockwave:", self.key_font_italic, value_color),
                    (" ", self.key_font, value_color),
                    (self._format_key_name(keys["shockwave"]), self.key_font, value_color),
                ],
            )
            current_y += line_height

            self._draw_text("EMP: coming soon!     Railgun: coming soon!", self.key_font, lines_x, current_y, color=(150, 150, 150), center=False)
            current_y += int(line_height * 1.8)

            # Change keyset row (selectable)
            row_text = f"Change Player {player_num} Keyset?"
            is_selected = (selected_index == (player_num - 1))
            color = (255, 255, 120) if is_selected else (200, 200, 200)
            if is_selected:
                bar = pygame.Rect(0, 0, int(cell_width * 0.82), int(line_height * 1.6))
                bar.center = (center_x, current_y)
                pygame.draw.rect(self.screen, (35, 35, 35), bar, border_radius=10)
            self._draw_text(row_text, self.key_font, center_x, current_y, color=color)

        # Back row (selectable)
        back_selected = (selected_index == 4)
        back_y = int(h * 0.93)
        if back_selected:
            bar = pygame.Rect(0, 0, int(w * 0.30), int(line_height * 1.8))
            bar.center = (w // 2, back_y)
            pygame.draw.rect(self.screen, (35, 35, 35), bar, border_radius=10)
        self._draw_text("Back", self.item_font, w // 2, back_y, color=(255, 255, 120) if back_selected else (230, 230, 230))

        hint = "UP/DOWN: select    ENTER: change keyset    ESC: back"
        self._draw_text(hint, self.hint_font, w // 2, int(h * 0.97), color=(180, 180, 180))

    def _draw_player_keys_rebind(self, player_num: int, action_index: int, working_keys: dict):
        """Rebind flow UI: instruction at top + 8-action column with highlight."""
        w, h = self.screen.get_size()
        self._draw_background()

        self._draw_text(f"PLAYER {player_num} KEYSET", self.title_font, w // 2, int(h * 0.08))

        # Bold instruction line (use SysFont so we can force bold reliably)
        scale = self.settings.screen_width / 1200
        instr_font = pygame.font.SysFont(None, int(36 * scale), bold=True)
        instr = "Hit the key you would like to use for the highlighted function:"
        self._draw_text(instr, instr_font, w // 2, int(h * 0.18), color=(255, 255, 255))

        actions = ["up", "down", "right", "left", "fire", "squadron", "nanites", "shockwave"]
        labels = {
            "up": "Up",
            "down": "Down",
            "right": "Right",
            "left": "Left",
            "fire": "Fire",
            "squadron": "Squadron",
            "nanites": "Nanites",
            "shockwave": "Shockwave",
        }

        start_y = int(h * 0.30)
        row_h = int(48 * scale)
        x_left = int(w * 0.25)
        x_right = int(w * 0.62)

        for i, action in enumerate(actions):
            y = start_y + i * row_h
            is_selected = (i == action_index)
            if is_selected:
                bar = pygame.Rect(0, 0, int(w * 0.70), int(row_h * 0.85))
                bar.center = (w // 2, y)
                pygame.draw.rect(self.screen, (35, 35, 35), bar, border_radius=10)

            label = f"{labels[action]}:"
            value = self._format_key_name(working_keys.get(action, 0))
            color = (255, 255, 120) if is_selected else (230, 230, 230)
            # Italicize the label (e.g., "Up:") but keep values in the current font/size.
            self._draw_text(label, self.item_font_italic, x_left, y, color=color, center=False)
            self._draw_text(value, self.item_font, x_right, y, color=color, center=False)

        hint = "Press ESC to cancel"
        self._draw_text(hint, self.hint_font, w // 2, int(h * 0.95), color=(180, 180, 180))

    def _draw_keys_menu(self):
        """
        Player Keys menu:\n
        - Overview shows keybindings and lets you pick 'Change Player N Keyset?'\n
        - Rebind flow captures keys in sequence for gameplay only.\n
        Note: menu navigation keys remain fixed and are not affected by rebinding.
        """
        selected_index = 0  # 0-3 => players 1-4, 4 => Back
        mode = "overview"  # or "rebind"

        rebind_player_num = 1
        rebind_action_index = 0
        rebind_original_keys = {}
        rebind_working_keys = {}

        actions = ["up", "down", "right", "left", "fire", "squadron", "nanites", "shockwave"]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                if event.type != pygame.KEYDOWN:
                    continue

                # Always allow backing out of this menu with ESC
                if mode == "overview":
                    if event.key == pygame.K_ESCAPE:
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_confirm")
                        return

                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_index = (selected_index - 1) % 5
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_change")
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_index = (selected_index + 1) % 5
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_change")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_confirm")

                        if selected_index == 4:
                            return

                        # Enter rebind flow for player N
                        rebind_player_num = selected_index + 1
                        target_dict = getattr(self.settings, f"player{rebind_player_num}_keys")
                        rebind_original_keys = dict(target_dict)
                        rebind_working_keys = dict(target_dict)
                        rebind_action_index = 0
                        mode = "rebind"

                else:
                    # Rebind mode: bind any key EXCEPT ESCAPE.
                    if event.key == pygame.K_ESCAPE:
                        # Cancel: restore original mapping (in-place)
                        target_dict = getattr(self.settings, f"player{rebind_player_num}_keys")
                        target_dict.clear()
                        target_dict.update(rebind_original_keys)
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_confirm")
                        mode = "overview"
                        continue

                    # Capture key for current action
                    action = actions[rebind_action_index]
                    rebind_working_keys[action] = event.key

                    # Move to next action
                    rebind_action_index += 1
                    if rebind_action_index >= len(actions):
                        # Commit: copy into settings dict in-place
                        target_dict = getattr(self.settings, f"player{rebind_player_num}_keys")
                        target_dict.clear()
                        target_dict.update(rebind_working_keys)
                        self._keys_changed = True
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_confirm")
                        mode = "overview"
                    else:
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_change")

            if mode == "overview":
                self._draw_player_keys_overview(selected_index)
            else:
                self._draw_player_keys_rebind(rebind_player_num, rebind_action_index, rebind_working_keys)

            pygame.display.flip()
            self.clock.tick(60)

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
                        return {"keys_changed": True} if self._keys_changed else None
                    
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.selected_index = (self.selected_index - 1) % len(self.items)
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_change")

                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected_index = (self.selected_index + 1) % len(self.items)
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_change")

                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if self.items[self.selected_index] == "Resolution":
                            self.current_res_index = (self.current_res_index - 1) % len(self.resolutions)
                            if self.play_sound_callback:
                                self.play_sound_callback("menu_selection_toggle")
                        elif self.items[self.selected_index] == "Sound":
                            self.sound_enabled = False
                            self.settings.sounds_enabled = False
                            # Stop all currently playing sounds
                            pygame.mixer.stop()
                            if self.play_sound_callback:
                                self.play_sound_callback("menu_selection_toggle")
                        # elif self.items[self.selected_index] == "Music":
                        #     self.music_enabled = False
                        #     self.settings.music_enabled = False
                        #     # Stop all music channels (would need game instance access)
                        #     # For now, just stop menu music via callback if available
                        #     if self.play_sound_callback:
                        #         self.play_sound_callback("menu_selection_toggle")

                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if self.items[self.selected_index] == "Resolution":
                            self.current_res_index = (self.current_res_index + 1) % len(self.resolutions)
                            if self.play_sound_callback:
                                self.play_sound_callback("menu_selection_toggle")
                        elif self.items[self.selected_index] == "Sound":
                            self.sound_enabled = True
                            self.settings.sounds_enabled = True
                            if self.play_sound_callback:
                                self.play_sound_callback("menu_selection_toggle")
                        # elif self.items[self.selected_index] == "Music":
                        #     self.music_enabled = True
                        #     self.settings.music_enabled = True
                        #     if self.play_sound_callback:
                        #         self.play_sound_callback("menu_selection_toggle")

                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if self.play_sound_callback:
                            self.play_sound_callback("menu_selection_confirm")
                        
                        choice = self.items[self.selected_index]

                        if choice == "Resolution":
                            # Apply resolution change
                            new_res = self.resolutions[self.current_res_index]
                            self.settings.screen_width = new_res["width"]
                            self.settings.screen_height = new_res["height"]
                            # Recalculate derived values
                            self.settings.play_height = self.settings.screen_height
                            self.settings.screen_height_total = self.settings.play_height + self.settings.hud_strip_height
                            # Resize screen
                            self.screen = pygame.display.set_mode((new_res["width"], self.settings.screen_height_total), pygame.RESIZABLE)
                            return {"resolution_changed": True, "new_resolution": new_res}

                        elif choice == "Player Keys":
                            self._draw_keys_menu()

                        elif choice == "Back":
                            return {"keys_changed": True} if self._keys_changed else None

            self._draw_menu()
            self.clock.tick(60)

