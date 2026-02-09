import random
import pygame

from base_settings import resource_path


class AudioManager:
    """
    Central sound/music manager for the game.

    - Loads all SFX/music into a key -> [Sound variants] dict
    - Plays by key, with a simple priority system that can pre-empt lower priority sounds
    - Tracks a few long-running \"music\" channels so they can be faded out cleanly
    """

    def __init__(self, settings):
        self.settings = settings

        # Sound registry: {key: [Sound variants]}
        self.sounds = {}

        # Track lasertanker firing sounds (alien_ref -> channel mapping)
        self.lasertanker_firing_sound_channels = {}

        # Sound priority system - lower number = higher priority
        self.SOUND_PRIORITY = {
            "announce": 1,  # Game announcements
            "player": 2,    # Player sounds
            "powerup": 3,   # Powerup sounds
            "hum": 4,       # Alien hum sounds
            "death": 5,     # Alien death sounds (level-based sub-priority)
            "shield": 6,    # Shield sounds
            "alien_fire": 7,  # Alien firing
            "squadron_shot": 7.3,  # Squadron firing sounds
            "player_shot": 7.5,  # Player shot sounds
            "bullet_hit": 8,  # Bullet impact
        }

        # Track active sound channels and their priorities for channel management
        self.active_sound_channels = {}  # {channel: priority}

        # Music channel tracking
        self.nyancat_music_channel = None
        self.defeat_music_channel = None
        self.victory_music_channel = None

    def load_sounds(self):
        """Load sound variants into self.sounds dict."""

        def _load_variants(key, base_name, count):
            self.sounds[key] = []
            for var_num in range(1, count + 1):
                try:
                    sound_path = resource_path(f"sounds/{base_name}_{var_num}.wav")
                    sound = pygame.mixer.Sound(sound_path)
                    self.sounds[key].append(sound)
                except (pygame.error, FileNotFoundError):
                    print(f"Warning: Could not load sound: sounds/{base_name}_{var_num}.wav")

        # Fire / bullet sounds
        _load_variants("player_shot", "player_shot", 5)
        _load_variants("alien_lvl1_shot", "alien_lvl1_shot", 5)
        _load_variants("alien_lvl2_shot", "alien_lvl2_shot", 5)
        _load_variants("alien_lvl3_shot", "alien_lvl3_shot", 3)
        _load_variants("alien_laserminion_shot", "alien_laserminion_shot", 3)

        # Alien death sounds
        _load_variants("alien_lvl1to3_death", "alien_lvl1to3_death", 4)
        _load_variants("alien_lvl4_collision", "alien_lvl4_collision", 1)
        _load_variants("alien_lvl4_hum", "alien_lvl4_hum", 1)

        # Shield sounds
        _load_variants("shield_hit_small_bullet", "shield_hit_small_bullet", 2)
        _load_variants("shield_hit_big_bullet", "shield_hit_big_bullet", 2)
        _load_variants("shield_collide_small_alien", "shield_collide_small_alien", 3)
        _load_variants("shield_collide_large_alien", "shield_collide_large_alien", 2)
        _load_variants("shield_collide_tanker", "shield_collide_tanker", 2)
        _load_variants("shield_recharge", "shield_recharge", 2)

        # Alien firing sounds for higher level aliens
        _load_variants("alien_destroyer_shot", "alien_destroyer_shot", 5)
        _load_variants("alien_cruiser_center_shot", "alien_cruiser_center_shot", 3)
        _load_variants("alien_cruiser_wing_shot", "alien_cruiser_wing_shot", 3)
        _load_variants("alien_laztanker_shot", "alien_laztanker_shot", 2)

        # Alien hum sounds (ambient)
        _load_variants("alien_destroyer_hum", "alien_destroyer_hum", 1)
        _load_variants("alien_cruiser_hum", "alien_cruiser_hum", 1)
        _load_variants("alien_tanker_hum", "alien_tanker_hum", 1)

        # Big alien deaths
        _load_variants("alien_destroyer_death", "alien_destroyer_death", 2)
        _load_variants("alien_cruiser_death", "alien_cruiser_death", 2)
        _load_variants("alien_laztanker_death", "alien_laztanker_death", 2)

        # Bullet hit
        _load_variants("bullet_hit", "bullet_hit", 4)

        # Powerups
        _load_variants("powerup_railgun_charge", "powerup_railgun_charge", 3)
        _load_variants("powerup_railgun_fire", "powerup_railgun_fire", 3)
        _load_variants("powerup_shockwave", "powerup_shockwave", 2)
        _load_variants("powerup_emp", "powerup_emp", 3)
        _load_variants("powerup_nanites", "powerup_nanites", 4)
        _load_variants("powerup_squadron_hello", "powerup_squadron_hello", 3)
        _load_variants("powerup_grab", "powerup_grab", 1)
        _load_variants("squadron_shot", "squadron_shot", 2)
        _load_variants("powerup_squadron_death", "powerup_squadron_death", 1)

        # Player voice lines
        _load_variants("player_life_lost", "player_life_lost", 2)
        _load_variants("player_respawn", "player_respawn", 2)
        _load_variants("player_death", "player_death", 2)
        _load_variants("lifepod_shot", "lifepod_shot", 2)
        _load_variants("player_level_up", "player_level_up", 3)
        _load_variants("player_collide", "player_collide", 3)

        # Announcements / music
        _load_variants("announce_game_opens", "announce_game_opens", 3)
        _load_variants("announce_game_start", "announce_game_start", 1)
        _load_variants("announce_wave_clear", "announce_wave_clear", 1)
        _load_variants("announce_new_wave", "announce_new_wave", 1)
        _load_variants("alien_breach", "alien_breach", 1)
        _load_variants("announce_defeat", "announce_defeat", 2)
        _load_variants("announce_victory", "announce_victory", 2)
        _load_variants("countdown", "countdown", 1)

        # Bonus wave sounds
        _load_variants("secret_menu_music", "secret_menu_music", 1)
        _load_variants("nyan_cat_music", "nyan_cat_music", 1)
        _load_variants("longcat_music", "longcat_music", 1)
        _load_variants("transcendence_cat_music", "transcendence_cat_music", 1)
        _load_variants("dad_shockwave", "dad_shockwave", 2)

        # Menu music and sounds
        _load_variants("menu_music", "menu_music", 3)
        _load_variants("menu_selection_change", "menu_selection_change", 1)
        _load_variants("menu_selection_confirm", "menu_selection_confirm", 1)
        _load_variants("menu_selection_toggle", "menu_selection_toggle", 1)

        # Defeat and victory background music
        _load_variants("music_defeat_normal", "music_defeat_normal", 1)
        _load_variants("music_defeat_bonus", "music_defeat_bonus", 1)
        _load_variants("music_kiddie_victory", "music_kiddie_victory", 1)
        _load_variants("music_easy_victory", "music_easy_victory", 1)
        _load_variants("music_normal_victory", "music_normal_victory", 1)
        _load_variants("music_victory_hard", "music_victory_hard", 1)

        _load_variants("music_waves_1to3", "music_waves_1to3", 1)
        _load_variants("music_waves_4to6", "music_waves_4to5", 1)
        _load_variants("music_waves_7to9", "music_waves_7to9", 1)
        _load_variants("music_wave_10", "music_wave_10", 1)

    def play(self, key, loop=0, priority=None):
        """Play a random variant of a sound category, if available."""
        if not getattr(self.settings, "sounds_enabled", True):
            return None

        key_lower = key.lower()
        is_music = "music" in key_lower or key_lower.startswith("music_")
        if is_music and not getattr(self.settings, "music_enabled", True):
            return None

        variants = self.sounds.get(key)
        if not variants:
            return None

        if priority is None:
            priority = self.get_sound_priority(key)

        sound = random.choice(variants)

        num_channels = pygame.mixer.get_num_channels()
        busy_channels = sum(1 for i in range(num_channels) if pygame.mixer.Channel(i).get_busy())
        if busy_channels >= num_channels:
            self.free_channel_for_priority(priority)

        channel = sound.play(loops=loop)
        if channel:
            self.active_sound_channels[channel] = priority
        return channel

    def get_sound_priority(self, key):
        """Determine priority for a sound key based on naming patterns."""
        key_lower = key.lower()

        if key_lower.startswith("announce_") or key_lower in ("countdown", "victory", "defeat"):
            return self.SOUND_PRIORITY["announce"]

        if key_lower.startswith("player_death") or "level_up" in key_lower or "life_lost" in key_lower or "respawn" in key_lower:
            return self.SOUND_PRIORITY["player"]

        if key_lower == "squadron_shot":
            return self.SOUND_PRIORITY["squadron_shot"]

        if key_lower.startswith("powerup_"):
            return self.SOUND_PRIORITY["powerup"]

        if "hum" in key_lower:
            return self.SOUND_PRIORITY["hum"]

        if "death" in key_lower or key_lower == "alien_lvl4_collision":
            base_priority = self.SOUND_PRIORITY["death"]
            if "destroyer_death" in key_lower or "lvl5" in key_lower:
                return base_priority + 0.5
            if "cruiser_death" in key_lower or "lvl6" in key_lower:
                return base_priority + 0.6
            if "laztanker_death" in key_lower or "lvl7" in key_lower:
                return base_priority + 0.7
            if "lvl4" in key_lower:
                return base_priority + 0.4
            return base_priority + 0.3

        if key_lower.startswith("shield_"):
            return self.SOUND_PRIORITY["shield"]

        if key_lower.startswith("alien_") and ("shot" in key_lower or "fire" in key_lower or "laserminion" in key_lower):
            return self.SOUND_PRIORITY["alien_fire"]

        if key_lower == "player_shot":
            return self.SOUND_PRIORITY["player_shot"]

        if "bullet_hit" in key_lower:
            return self.SOUND_PRIORITY["bullet_hit"]

        return 7

    def free_channel_for_priority(self, required_priority):
        """Find and stop the lowest priority playing sound to free a channel."""
        if not self.active_sound_channels:
            return

        lowest_priority = max(self.active_sound_channels.values())
        if lowest_priority > required_priority:
            for channel, priority in list(self.active_sound_channels.items()):
                if priority == lowest_priority:
                    if channel and channel.get_busy():
                        channel.stop()
                    del self.active_sound_channels[channel]
                    break

    def stop_channel(self, channel):
        """Stop a sound channel if it's playing."""
        if not channel:
            return

        is_music_channel = (
            channel == self.nyancat_music_channel
            or channel == self.defeat_music_channel
            or channel == self.victory_music_channel
        )

        if is_music_channel and channel.get_busy():
            channel.fadeout(2500)
        else:
            channel.stop()

        if channel in self.active_sound_channels:
            del self.active_sound_channels[channel]

    def stop_music_channel(self, channel):
        """Stop a music channel with 2.5 second fade-out."""
        if channel and channel.get_busy():
            channel.fadeout(2500)

    def stop_hum_channel(self, channel):
        """Stop a hum sound channel with 2.5 second fade-out."""
        if channel and channel.get_busy():
            channel.fadeout(2500)

    def stop_all(self):
        """Stop all mixer playback and clear tracked channels."""
        pygame.mixer.stop()

        for channel in list(self.active_sound_channels.keys()):
            if channel:
                channel.stop()
        self.active_sound_channels.clear()

        for _alien, channel in list(self.lasertanker_firing_sound_channels.items()):
            if channel:
                channel.stop()
        self.lasertanker_firing_sound_channels.clear()

        self.nyancat_music_channel = None
        self.defeat_music_channel = None
        self.victory_music_channel = None




