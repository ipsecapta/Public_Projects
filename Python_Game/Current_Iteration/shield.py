import pygame


class Shield(pygame.sprite.Sprite):
    def __init__(self, settings, rect):
        super().__init__()
        self.settings = settings
        self.image = pygame.Surface((rect.width, rect.height)).convert()
        self.rect = rect.copy()

        # Shield stages use color indices defined on settings.shield_colors
        self.stage_index = self.settings.shield_start_index  # start from settings-defined index
        self.last_hit_time_ms = pygame.time.get_ticks()
        self.recharge_hit_counter = 0
        self.stage_improved = False  # Flag to track if stage improved (for sound)

        self._sync_color()

    def _sync_color(self):
        """Update shield color based on the current stage index."""
        # Safety check: clamp stage_index to valid range
        max_index = len(self.settings.shield_colors) - 1
        clamped_index = max(0, min(self.stage_index, max_index))
        color = self.settings.shield_colors[clamped_index]
        self.image.fill(color)

    def take_damage(self, amount: int):
        """Apply damage; advance stage and remove when exhausted."""
        self.stage_index += amount
        if self.stage_index >= len(self.settings.shield_colors):
            self.kill()
            return

        self._sync_color()
        self.last_hit_time_ms = pygame.time.get_ticks()

    def register_recharge_hit(self):
        """Track recharge hits; improve shield after enough hits per settings.
        Returns True if shield stage improved."""
        self.recharge_hit_counter += 1
        if self.recharge_hit_counter >= self.settings.shield_repair_hits_per_level:
            old_stage = self.stage_index
            self.stage_index = max(self.settings.shield_repair_cap_index, self.stage_index - 1)
            self.recharge_hit_counter = 0
            self._sync_color()
            return self.stage_index < old_stage  # Return True if stage improved
        return False
    
    def heal(self, amount: int):
        """Improve shield (lower stage_index) by amount, down to full (index 0).
        Returns True if shield stage improved."""
        old_stage = self.stage_index
        self.stage_index = max(0, self.stage_index - amount)
        self._sync_color()
        self.last_hit_time_ms = pygame.time.get_ticks()
        return self.stage_index < old_stage  # Return True if stage improved

    def update(self):
        """Regenerate over time down to the regen cap. Also track player if assigned."""
        # Track player movement if this shield is attached to a player (bonus wave mom powerup)
        if hasattr(self, 'tracked_player') and self.tracked_player and self.tracked_player.alive():
            # Update shield position to stay above player
            # Offset matches shield height (10px for mom shields)
            shield_height = self.rect.height
            self.rect.left = self.tracked_player.rect.left
            self.rect.top = self.tracked_player.rect.top - shield_height
            # Update shield width to match player width
            self.rect.width = self.tracked_player.rect.width
            # Resize image if needed
            if self.image.get_size() != (self.rect.width, self.rect.height):
                self.image = pygame.Surface((self.rect.width, self.rect.height)).convert()
                self._sync_color()
        elif hasattr(self, 'tracked_player') and (not self.tracked_player or not self.tracked_player.alive()):
            # Player is dead, remove shield
            self.kill()
            return
        
        now = pygame.time.get_ticks()
        if now - self.last_hit_time_ms >= self.settings.shield_regen_delay:
            if self.stage_index > self.settings.shield_regen_cap_index:
                old_stage = self.stage_index
                self.stage_index -= 1
                self._sync_color()
                self.last_hit_time_ms = now
                self.stage_improved = (self.stage_index < old_stage)  # Flag for main file to check
            else:
                self.stage_improved = False
        else:
            self.stage_improved = False
