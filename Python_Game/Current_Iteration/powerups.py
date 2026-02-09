#powerups.py
#powerup logic and behavior lives here; information on drop probabilities, specs, etc is in base_settings. 

import math
import random
import pygame

from bullet import Bullet, VictoryFireworkShellSmall  # uses your existing Bullet class
from shield import Shield  # or wherever your Shield class actually lives


def choose_powerup_type(settings, is_bonus_wave=False) -> str | None:
    """Return a powerup type string based on enabled toggles + weights.
    In bonus wave mode, only returns 'dad' or 'mom'."""
    if not settings.powerups_enabled:
        return None
    
    # Bonus wave: only dad and mom powerups
    if is_bonus_wave:
        return random.choice(["dad", "mom"])

    candidates = []
    for ptype, w in settings.powerup_weights.items():
        if ptype == "squadron" and not settings.powerup_enable_squadron:
            continue
        if ptype == "shockwave" and not settings.powerup_enable_shockwave:
            continue
        if ptype == "nanites" and not settings.powerup_enable_nanites:
            continue
        if w > 0:
            candidates.append((ptype, float(w)))

    if not candidates:
        return None

    total = sum(w for _, w in candidates)
    r = random.random() * total
    acc = 0.0
    for ptype, w in candidates:
        acc += w
        if r <= acc:
            return ptype
    return candidates[-1][0]


class PowerUpPickup(pygame.sprite.Sprite):
    """A drifting pickup that increments a player's inventory on collision."""
    def __init__(self, settings, screen, ptype: str, centerx: int, centery: int):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.ptype = ptype

        path_map = {
            "squadron": settings.powerup_squadron_path,
            "nanites": settings.powerup_nanite_path,
            "shockwave": settings.powerup_shockwave_path,
            "dad": settings.powerup_dad_path,
            "mom": settings.powerup_mom_path,
        }
        path = path_map.get(ptype)
        if not path:
            raise ValueError(f"Unknown powerup type: {ptype}")

        self.image = pygame.image.load(path).convert_alpha()
        # Mom and dad powerups are 44% larger (1.44x = 20% larger than current 20%)
        if ptype == "flyby":
            base_size = 55

        elif ptype in ("dad", "mom"):
            base_size = round(30 * 1.44)  # 44% larger = 43
        else:
            base_size = 30
        self.image = pygame.transform.smoothscale(self.image, (round(self.settings.multiplayer_resizer*base_size), round(self.settings.multiplayer_resizer*base_size)))
        self.rect = self.image.get_rect(center=(centerx, centery))

        self.spawn_x = float(self.rect.centerx)
        self.y = float(self.rect.y)
        self.t0 = pygame.time.get_ticks()
        self.phase = random.random() * math.tau
        
        # Mom and dad powerups use slower movement
        if ptype in ("dad", "mom"):
            self.fall_speed = self.settings.powerup_fall_speed * 0.5  # 50% slower fall
            self.zigzag_freq = self.settings.powerup_zigzag_freq * 0.3  # 70% slower zigzag (much slower)
        else:
            self.fall_speed = self.settings.powerup_fall_speed
            self.zigzag_freq = self.settings.powerup_zigzag_freq

    def update(self):
        now = pygame.time.get_ticks()
        t = (now - self.t0)

        self.y += self.fall_speed
        zig = math.sin(self.phase + t * self.zigzag_freq) * self.settings.powerup_zigzag_amp

        self.rect.y = int(self.y)
        self.rect.centerx = int(self.spawn_x + zig)

        # kill when below playfield (don't live in HUD strip)
        if self.rect.top > self.settings.play_height:
            self.kill()


class SquadronShip(pygame.sprite.Sprite):
    """Sidecar ship that tracks a specific player and fires with them."""
    def __init__(self, settings, screen, owner_ship, side: str):
        super().__init__()
        
        
        self.settings = settings
        self.screen = screen
        self.owner = owner_ship
        self.side = side  # "left" or "right"
        
        is_hard = getattr(self.settings, "difficulty_mode", "easy").lower() == "hard"

        self.image_normal = pygame.image.load(settings.squadron_ship_path).convert_alpha()
        self.image_normal = pygame.transform.smoothscale(self.image_normal, (round(self.settings.multiplayer_resizer*40), round(self.settings.multiplayer_resizer*40)))
        self.image_hurt = pygame.image.load(settings.squadron_hurt_path).convert_alpha()
        self.image_hurt= pygame.transform.smoothscale(self.image_hurt, (round(self.settings.multiplayer_resizer*40), round(self.settings.multiplayer_resizer*40)))

        self.image = self.image_normal

        # Start offscreen below the visible window (true "flies in")
        w, h = self.image.get_size()
        start_y = settings.screen_height_total + h + 10
        self.rect = self.image.get_rect(center=(owner_ship.rect.centerx, start_y))
        self.max_hp = settings.squadron_hits_to_die
        self.hp = self.max_hp

        if is_hard: #squadrons are stronger in hard mode. 
            self.base_speed = settings.squadron_speed_hardmode
            self.max_bullets = settings.squadron_max_bullets_hardmode
            self.speed_modifier_increment = settings.squadron_speed_increment_hardmode
        else:
            self.base_speed = settings.squadron_speed  # Store original speed
            self.max_bullets = settings.squadron_max_bullets
            self.speed_modifier_increment = settings.squadron_speed_increment

        self.speed_modifier = 0.0  # Speed reduction from damage

        self.y = float(self.rect.centery)

    def take_hit(self, dmg=1):
        self.hp -= dmg
        if self.hp <= 0:
            self.kill()
            return

        # Apply speed reduction based on damage taken (softened)
        if self.hp == 2:  # First hit (assuming starts with 3 HP)
            self.speed_modifier += self.speed_modifier_increment  # increment differs in normal and hard mode.
        elif self.hp == 1:  # Second hit
            self.speed_modifier = self.speed_modifier_increment

        # After 2 hits total (i.e. hp == 1 if starting at 3), swap sprite:
        if self.hp <= (self.settings.squadron_hits_to_die - self.settings.squadron_hits_to_hurt):
            self.image = self.image_hurt

    def heal(self, amount: int = 1):
        """Heal squadron by increasing hp up to max_hp; restore sprite if no longer in hurt state."""
        if not self.alive():
            return
        try:
            amt = int(amount)
        except Exception:
            amt = 1
        if amt <= 0:
            return

        self.hp = min(int(getattr(self, "max_hp", self.settings.squadron_hits_to_die)), self.hp + amt)
        # If healed above hurt threshold, restore normal sprite
        hurt_threshold = (self.settings.squadron_hits_to_die - self.settings.squadron_hits_to_hurt)
        if self.hp > hurt_threshold:
            self.image = self.image_normal

    def _target_pos(self):
        if self.side == "front":
            # Position directly in front of player: 5 pixels above player's top, aligned centerx
            tx = self.owner.rect.centerx
            ty = self.owner.rect.top - 5 - self.rect.height // 2
            return tx, ty
        elif self.side == "back":
            # Position directly behind player: 5 pixels below player's bottom, aligned centerx
            tx = self.owner.rect.centerx
            ty = self.owner.rect.bottom + 5 + self.rect.height // 2
            return tx, ty
        elif self.side == "right":
            # Position to the right of player
            oy = self.owner.rect.centery
            tx = self.owner.rect.right + self.settings.squadron_offset_px + self.rect.width // 2
            return tx, oy
        elif self.side == "left":
            # Position to the left of player
            oy = self.owner.rect.centery
            tx = self.owner.rect.left - self.settings.squadron_offset_px - self.rect.width // 2
            return tx, oy
        else:
            # Fallback: default to left if side is unrecognized
            oy = self.owner.rect.centery
            tx = self.owner.rect.left - self.settings.squadron_offset_px - self.rect.width // 2
            return tx, oy

    def update(self):
        if not self.owner.alive():
            self.kill()
            return

        tx, ty = self._target_pos()

        # Smooth chase (low compute, looks nice)
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery

        dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
        current_speed = self.base_speed - self.speed_modifier
        step = min(current_speed, dist)

        self.rect.centerx += int(dx / dist * step)
        self.rect.centery += int(dy / dist * step)

        # Clamp to playfield (never down into HUD strip)
        if self.rect.bottom > self.settings.play_height:
            self.rect.bottom = self.settings.play_height

    def try_fire(self, bullets_group, fireworks_group=None):
        # Limit squadron bullets on screen - count bullets fired by this specific squadron
        active = 0
        for b in bullets_group.sprites():
            squadron_ref = getattr(b, "squadron_ref", None)
            if squadron_ref is self:
                active += 1
        if active >= self.max_bullets:
            return False  # Return False if didn't fire

        if fireworks_group is not None:
            b = VictoryFireworkShellSmall(
                settings=self.settings,
                screen=self.screen,
                x=self.rect.centerx,
                y=self.rect.top,
                fireworks_group=fireworks_group,
                owner_ref=self.owner,  # keep scoring ownership consistent even though cosmetic
                squadron_ref=self
            )
        else:
            b = Bullet(
                self.settings, self.screen,
                self.rect.centerx, self.rect.top,
                direction=-1,
                owner_type="player",
                owner_level=getattr(self.owner, "player_level", 1),
                owner_ref=self.owner,  # Use the player ship, not the squadron, so scoring works
                squadron_ref=self  # Track which squadron fired this bullet
            )
        bullets_group.add(b)
        return True  # Return True if fired successfully


class Nanite(pygame.sprite.Sprite):
    """A non-colliding helper that heals a target by pulsing."""
    def __init__(self, settings, screen, target, heal_fn, anchor: str = "top_center"):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.target = target
        self.heal_fn = heal_fn
        self.anchor = anchor

        # Randomize movement speed slightly per nanite: [base-0.1, base, base+0.1]
        base_speed = float(getattr(self.settings, "nanite_speed", 1.0))
        delta = float(getattr(self.settings, "nanite_speed_variation_delta", 0.1))
        self.move_speed = max(0.1, base_speed + random.choice([-delta, 0.0, delta]))

        # Beam flicker (arc-welder style): per-nanite state so multiple beams don't sync perfectly
        self._beam_on = True
        self._beam_alpha = 255
        self._beam_next_flicker_ms = pygame.time.get_ticks()

        self.image = pygame.image.load(settings.nanite_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (round(self.settings.multiplayer_resizer*22), round(self.settings.multiplayer_resizer*22)))

        self.rect = self.image.get_rect()

        # Start offscreen below, center:
        self.rect.center = (settings.screen_width // 2, settings.screen_height + 40)

        self.pulses_done = 0
        self.last_pulse_ms = pygame.time.get_ticks()

        self.state = "approach"  # approach -> pulse -> exit
        self.exit_image = None

    def _target_anchor(self):
        # Align to top-left/top-center/top-right of the target (slightly inset), at y = top + 5
        y = self.target.rect.top + 5
        if self.anchor in ("ship_top_left", "ship_top_right"):
            # Ships: exact corners (requested)
            if self.anchor == "ship_top_left":
                x = self.target.rect.left
            else:
                x = self.target.rect.right
        else:
            # Shields/other: keep a small inset so the nanites don't clip the edges
            inset = 6
            if self.anchor == "top_left":
                x = self.target.rect.left + inset
            elif self.anchor == "top_right":
                x = self.target.rect.right - inset
            else:  # "top_center"
                x = self.target.rect.centerx
        return (x, y)

    def update(self):
        if not self.target:
            self.kill()
            return

        now = pygame.time.get_ticks()
        tx, ty = self._target_anchor()

        if self.state == "approach":
            dx = tx - self.rect.centerx
            dy = ty - self.rect.centery
            dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
            step = min(self.move_speed, dist)

            self.rect.centerx += int(dx / dist * step)
            self.rect.centery += int(dy / dist * step)

            # close enough -> start pulsing
            if abs(dx) <= 3 and abs(dy) <= 3:
                self.state = "pulse"
                self.last_pulse_ms = now

        elif self.state == "pulse":
            # Stay locked to target
            self.rect.midbottom = (tx, ty)

            if now - self.last_pulse_ms >= self.settings.nanite_pulse_interval_ms:
                self.last_pulse_ms = now
                self.heal_fn(1)
                self.pulses_done += 1

                if self.pulses_done >= self.settings.nanite_pulses:
                    # Flip and exit downward
                    self.exit_image = pygame.transform.rotate(self.image, 180)
                    self.image = self.exit_image
                    self.state = "exit"

        elif self.state == "exit":
            self.rect.centery += int(self.move_speed * 2)
            if self.rect.top > self.settings.screen_height_total + 40:
                self.kill()

    def draw_beam(self):
        """Very cheap visual: a white 'beam' between nanite and target."""
        if self.state != "pulse":
            return
        x1, y1 = self.rect.midbottom
        x2, y2 = self.target.rect.midtop
        beam_rect = pygame.Rect(0, 0, self.settings.nanite_beam_width, max(6, y2 - y1))
        beam_rect.centerx = x1
        beam_rect.top = y1

        # Arc-welder flicker: very fast, slightly irregular, with randomized brightness/alpha.
        now = pygame.time.get_ticks()
        if now >= getattr(self, "_beam_next_flicker_ms", 0):
            min_ms = int(getattr(self.settings, "nanite_beam_flicker_min_ms", 10))
            max_ms = int(getattr(self.settings, "nanite_beam_flicker_max_ms", 35))
            if max_ms < min_ms:
                max_ms = min_ms
            self._beam_next_flicker_ms = now + random.randint(min_ms, max_ms)

            on_prob = float(getattr(self.settings, "nanite_beam_on_probability", 0.85))
            self._beam_on = (random.random() < on_prob)

            a_min = int(getattr(self.settings, "nanite_beam_alpha_min", 30))
            a_max = int(getattr(self.settings, "nanite_beam_alpha_max", 255))
            if a_max < a_min:
                a_max = a_min
            self._beam_alpha = random.randint(a_min, a_max)

        if not getattr(self, "_beam_on", True):
            return

        # Draw as alpha surface (pygame.draw.rect has no alpha on the main surface)
        beam_surf = pygame.Surface((beam_rect.width, beam_rect.height), pygame.SRCALPHA)
        beam_surf.fill((245, 245, 245, int(getattr(self, "_beam_alpha", 255))))
        self.screen.blit(beam_surf, beam_rect.topleft)


class Shockwave(pygame.sprite.Sprite):
    def __init__(self, settings, screen, owner_ship):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.owner = owner_ship
        self.hit_aliens = set()  # Track which aliens this shockwave has already hit

        img = pygame.image.load(settings.shockwave_path).convert_alpha()
        self.image = pygame.transform.smoothscale(img, (round(self.settings.multiplayer_resizer*200), round(self.settings.multiplayer_resizer*95)))
        self.rect = self.image.get_rect()

        # Spawn "in front" of player (above it)
        self.rect.midbottom = owner_ship.rect.midtop

    def update(self):
        self.rect.y -= int(self.settings.shockwave_speed)
        if self.rect.bottom < 0:
            self.kill()

    def apply_damage(self, aliens_group):
        """Kill low-level aliens in path. Call only while shockwave exists (rare)."""
        hits = pygame.sprite.spritecollide(self, aliens_group, dokill=False)
        for alien in hits:
            lvl = getattr(alien, "level", 1)
            if lvl <= self.settings.shockwave_kill_max_alien_level:
                # You may want your alien death routine instead of kill():
                alien.kill()


class DadShip(pygame.sprite.Sprite):
    """Dad ship that flies across screen 3 times, firing shockwaves."""
    def __init__(self, settings, screen, run_number: int):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.run_number = run_number  # 0, 1, or 2 (for 3 runs)
        
        # Load and scale dad ship image to 129w x 70h (scaled by multiplayer_resizer)
        resize = settings.multiplayer_resizer
        sprite_width = round(129 * resize)
        sprite_height = round(70 * resize)
        self.base_image = pygame.image.load(settings.dadship_path).convert_alpha()
        self.base_image = pygame.transform.smoothscale(self.base_image, (sprite_width, sprite_height))
        self.image = self.base_image.copy()
        
        # Determine run parameters
        if run_number == 0:  # First run: right to left at 75% height
            self.start_x = settings.screen_width + sprite_width  # Off-screen right
            self.start_y = int(settings.screen_height * 0.75)
            self.speed = 3.5
            self.direction = -1  # Moving left
            self.flipped = False
        elif run_number == 1:  # Second run: left to right at 50% height
            self.start_x = -sprite_width  # Off-screen left
            self.start_y = int(settings.screen_height * 0.50)
            self.speed = 3.5
            self.direction = 1  # Moving right
            self.flipped = True
            self.image = pygame.transform.flip(self.base_image, True, False)
        else:  # Third run: right to left at 25% height
            self.start_x = settings.screen_width + sprite_width  # Off-screen right
            self.start_y = int(settings.screen_height * 0.25)
            self.speed = 3.5
            self.direction = -1  # Moving left
            self.flipped = False
            self.image = self.base_image.copy()
        
        self.rect = self.image.get_rect()
        self.rect.centerx = self.start_x
        self.rect.centery = self.start_y
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        
        self.shockwave_fired = False
        self.next_run_time = None
        self.is_complete = False  # Track if this run is complete (for runs 0 and 1, don't kill)
        
    def update(self):
        # Move ship
        self.x += self.speed * self.direction
        self.rect.centerx = int(self.x)
        
        # Fire shockwave when left edge passes right edge (for right->left) or right edge passes left edge (for left->right)
        if not self.shockwave_fired:
            if self.direction == -1:  # Moving left
                if self.rect.right <= self.settings.screen_width:
                    self._fire_shockwave()
            else:  # Moving right
                if self.rect.left >= 0:
                    self._fire_shockwave()
        
        # Check if off-screen - only kill after third run (run_number == 2)
        if self.direction == -1 and self.rect.right < 0:  # Exited left
            if self.run_number < 2:  # Schedule next run (runs 0 and 1)
                self.next_run_time = pygame.time.get_ticks() + 2000  # 2 seconds
                self.is_complete = True  # Mark as complete, don't kill yet
                # Move way off screen so it's not visible
                self.rect.right = -1000
            else:  # Run 2 (third and final run)
                self.kill()  # Final run, kill the sprite
        elif self.direction == 1 and self.rect.left > self.settings.screen_width:  # Exited right
            if self.run_number < 2:  # Schedule next run (runs 0 and 1)
                self.next_run_time = pygame.time.get_ticks() + 2000  # 2 seconds
                self.is_complete = True  # Mark as complete, don't kill yet
                # Move way off screen so it's not visible
                self.rect.left = self.settings.screen_width + 1000
            else:  # Run 2 (third and final run)
                self.kill()  # Final run, kill the sprite
    
    def _fire_shockwave(self):
        self.shockwave_fired = True
        # Fire from appropriate side based on direction
        # When moving left (right->left), fire from right side
        # When moving right (left->right), fire from left side
        if self.direction == -1:  # Moving left
            fire_x = self.rect.right  # Fire from right side
        else:  # Moving right
            fire_x = self.rect.left  # Fire from left side
        fire_y = self.rect.centery
        
        shockwave = DadShockwave(self.settings, self.screen, fire_x, fire_y, self.direction, self.flipped)
        # Return shockwave to be added to group
        return shockwave


class DadShockwave(pygame.sprite.Sprite):
    """Dad shockwave that travels in the same direction as the dad ship and damages kitties."""
    def __init__(self, settings, screen, x, y, direction, flipped=False):
        super().__init__()
        self.settings = settings
        self.screen = screen
        
        # Load and scale shockwave image (scaled by multiplayer_resizer)
        resize = settings.multiplayer_resizer
        img = pygame.image.load(settings.shockwave_dad_path).convert_alpha()
        if flipped:
            img = pygame.transform.flip(img, True, False)
        self.image = pygame.transform.smoothscale(img, (round(202 * resize), round(422 * resize)))
        self.rect = self.image.get_rect()
        
        # Position based on direction
        self.direction = direction  # -1 for left, 1 for right
        self.speed = 6.0
        
        if self.direction == -1:  # Moving left
            self.rect.right = x  # Anchor right edge at fire position
        else:  # Moving right
            self.rect.left = x  # Anchor left edge at fire position
        self.rect.centery = y
        
    def update(self):
        self.rect.x += int(self.speed * self.direction)
        # Kill when off-screen based on direction
        if self.direction == -1:  # Moving left
            if self.rect.right < 0:
                self.kill()
        else:  # Moving right
            if self.rect.left > self.settings.screen_width:
                self.kill()


class MomShip(pygame.sprite.Sprite):
    """Mom ship that flies up, fires bullets at players and shield slots, creates shields."""
    def __init__(self, settings, screen, players_group, shield_slots=None):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.players_group = players_group
        self.shield_slots = shield_slots if shield_slots else []  # List of shield slot rects
        
        # Load and scale mom ship image to 70w x 85h (scaled by multiplayer_resizer)
        resize = settings.multiplayer_resizer
        self.base_image = pygame.image.load(settings.momship_path).convert_alpha()
        self.base_image = pygame.transform.smoothscale(self.base_image, (round(70 * resize), round(85 * resize)))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        
        # Start at bottom center
        self.rect.centerx = settings.screen_width // 2
        self.rect.bottom = settings.screen_height
        self.y = float(self.rect.y)
        self.speed = 2.0
        self.target_y = int(settings.screen_height * 0.25)  # Stop at 25% height
        
        self.state = "ascending"  # ascending -> firing -> exiting
        self.bullets_fired = 0
        alive_count = len([p for p in players_group if p.player_state == "alive"])
        shield_count = len(self.shield_slots) if self.shield_slots else 0
        # Fire 14 bullets per player + 14 bullets per shield slot
        self.total_bullets = 14 * (alive_count + shield_count)
        self.next_fire_time = pygame.time.get_ticks()
        self.fire_interval = 200  # 200ms between shots
        
    def update(self):
        if self.state == "ascending":
            self.y -= self.speed
            self.rect.y = int(self.y)
            if self.rect.bottom <= self.target_y:
                self.state = "firing"
                self.rect.bottom = self.target_y
                self.y = float(self.rect.y)
        
        elif self.state == "firing":
            now = pygame.time.get_ticks()
            if now >= self.next_fire_time and self.bullets_fired < self.total_bullets:
                # Fire bullets at all alive players and shield slots
                # Store bullets to be added to group
                if not hasattr(self, 'bullets_to_fire'):
                    self.bullets_to_fire = []
                
                # Fire at players
                alive_players = [p for p in self.players_group if p.player_state == "alive"]
                for player in alive_players:
                    bullet = MomBullet(self.settings, self.screen, target_player=player, 
                                      start_x=self.rect.centerx, start_y=self.rect.centery)
                    self.bullets_to_fire.append(bullet)
                
                # Fire at shield slots
                if self.shield_slots:
                    for slot_rect in self.shield_slots:
                        # Target the center of the shield slot
                        bullet = MomBullet(self.settings, self.screen, target_player=None,
                                          start_x=self.rect.centerx, start_y=self.rect.centery,
                                          target_x=slot_rect.centerx, target_y=slot_rect.centery)
                        self.bullets_to_fire.append(bullet)
                
                bullets_this_volley = len(alive_players) + (len(self.shield_slots) if self.shield_slots else 0)
                self.bullets_fired += bullets_this_volley
                self.next_fire_time = now + self.fire_interval
            else:
                if not hasattr(self, 'bullets_to_fire'):
                    self.bullets_to_fire = []
            
            if self.bullets_fired >= self.total_bullets:
                # Flip vertically and exit
                self.image = pygame.transform.flip(self.base_image, False, True)
                self.state = "exiting"
        
        elif self.state == "exiting":
            self.y += self.speed
            self.rect.y = int(self.y)
            if self.rect.top > self.settings.screen_height:
                self.kill()


class MomBullet(pygame.sprite.Sprite):
    """Mom's white charge shot that targets player midbottom or a fixed position."""
    def __init__(self, settings, screen, target_player=None, start_x=None, start_y=None, target_x=None, target_y=None):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.target_player = target_player  # Can be None if targeting fixed position
        self.is_fixed_target = target_player is None
        
        # Create white square (scaled by multiplayer_resizer)
        resize = settings.multiplayer_resizer
        size = max(1, round(7 * resize))  # Ensure at least 1 pixel
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = start_x
        self.rect.centery = start_y
        
        self.speed = 4.5
        
        # Calculate direction to target
        if self.is_fixed_target:
            # Fixed position target (for shield slots)
            self.target_x = target_x
            self.target_y = target_y
        else:
            # Player target (player's midbottom = centerx, top)
            self.target_x = target_player.rect.centerx
            self.target_y = target_player.rect.top
        
    def update(self):
        # Update target position if targeting a player
        if not self.is_fixed_target:
            if self.target_player and self.target_player.alive():
                self.target_x = self.target_player.rect.centerx
                self.target_y = self.target_player.rect.top
            else:
                # Player is dead, kill bullet
                self.kill()
                return
        
        # Move toward target
        dx = self.target_x - self.rect.centerx
        dy = self.target_y - self.rect.centery
        dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
        
        self.rect.centerx += int((dx / dist) * self.speed)
        self.rect.centery += int((dy / dist) * self.speed)
        
        # Kill if off-screen
        if (self.rect.right < 0 or self.rect.left > self.settings.screen_width or
            self.rect.bottom < 0 or self.rect.top > self.settings.screen_height):
            self.kill()
