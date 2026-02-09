# Credits Refactor Plan

## Overview
This document outlines the plan to clean up and fix the credits implementation to match the detailed specifications provided.

## Current Issues Identified

### 1. **Enemies Destroyed Tracking**
- **Current**: Using `player_score` as a proxy for enemies destroyed
- **Problem**: Score includes points from various sources (boss kills, minions, etc.), not just enemy kills
- **Fix Needed**: Add `enemies_destroyed` counter to `player_stats` and increment it whenever an alien is killed by a player bullet

### 2. **Shield Recharge Shots Tracking**
- **Current**: `shield_recharge_shots` is defined in `player_stats` but **NEVER INCREMENTED**
- **Problem**: Shield Master award will always show 0 or be incorrect
- **Fix Needed**: Track shield recharge hits in `_do_collisions()` when bullets hit shields for recharge (lines 2941, 2946)

### 3. **Player List Display**
- **Current**: Players are sorted by score in credits
- **Problem**: Should show ALL players that were in the game (1, 2, 3, 4) regardless of score, in order
- **Fix Needed**: Track which players were in the game at start, display in order (1, 2, 3, 4) with conditional display

### 4. **Icon Sizes**
- **Current**: Icons are scaled to 50% of gameplay size
- **Problem**: User wants hardcoded 30w x 20h
- **Fix Needed**: Change icon scaling to fixed 30x20 pixels

### 5. **Password Logic**
- **Current**: 
  - Blinks for 10 seconds, then shows for 30 seconds
  - Shows on both victory and defeat
- **Problem**: 
  - Should blink for 5 seconds (1 blink per second)
  - Should show solid password until menu exit
  - Should only show on victory, not defeat
- **Fix Needed**: 
  - Change timing to 5 seconds blink (500ms on/off = 1 blink/second)
  - Remove 30-second timeout
  - Only show on victory (already correct, but verify)

### 6. **Final Victory Message**
- **Current**: Only shows password or nothing
- **Problem**: Should show "You did well! Come back after defeating Hard Mode..." message if not password condition
- **Fix Needed**: Add else clause to show encouragement message

### 7. **Text Formatting**
- **Current**: Some inconsistencies in spacing/formatting
- **Problem**: Need proper formatting with colons and spacing
- **Fix Needed**: Ensure consistent formatting: "Player 1: [value]"

### 8. **Section Timing**
- **Current**: Sections advance when header reaches midpoint
- **Status**: This appears correct, but need to verify all sections scroll until off-screen

### 9. **"THANK YOU FOR PLAYING" Font**
- **Current**: Uses custom font (BAUHS93.ttf) at screen_height * 0.14
- **Status**: Appears correct, matches victory/defeat banner size

## Implementation Steps

### Step 1: Add Missing Tracking
1. Add `enemies_destroyed` to `player_stats` initialization (line ~3803)
2. Increment `enemies_destroyed` when aliens are killed by player bullets:
   - In `_do_collisions()` when alien is killed by bullet (around line 3184)
   - In shockwave kills (around line 1324)
   - In bonus wave enemy kills (around line 5002)
3. Add `shield_recharge_shots` increment in `_do_collisions()`:
   - When bullet hits shield for recharge (lines 2941, 2946)
   - Track the bullet owner's player_id

### Step 2: Track Active Players
1. Store list of active player IDs at game start in `_create_players_from_count()`
2. Use this list in credits to show all players in order (1, 2, 3, 4)

### Step 3: Fix Credits Display
1. Change player list from sorted-by-score to ordered-by-player-id
2. Show all players that were in game, regardless of current state
3. Fix icon sizes to 30w x 20h
4. Ensure proper text formatting with colons

### Step 4: Fix Password Logic
1. Change blink timing to 5 seconds (500ms intervals = 1 blink/second)
2. Remove 30-second timeout - password stays until menu exit
3. Verify password only shows on victory (already correct)

### Step 5: Add Final Victory Message
1. Add else clause for non-password victory condition
2. Display: "You did well! Come back after defeating Hard Mode, with powerups on Normal or Rare,\nand this is where the\nSECRET MESSAGE\nwill appear..."

### Step 6: Verify Section Timing
1. Ensure each section scrolls until completely off-screen before being removed
2. Verify next section appears when previous section reaches halfway point

## Files to Modify

1. **Visintainer_A_AlienGame.py**:
   - `_create_players_from_count()`: Add active players tracking
   - `_do_collisions()`: Add enemies_destroyed and shield_recharge_shots tracking
   - `_store_final_player_data()`: Include enemies_destroyed
   - `_draw_credits()`: Complete rewrite to match specifications
   - `_update_defeat_victory_screens()`: Fix password timing
   - `_draw_defeat_victory_screens()`: Fix password display and add final message

## Testing Checklist

- [ ] Enemies destroyed count is accurate for each player
- [ ] Damage taken is tracked correctly
- [ ] Lives lost is tracked correctly
- [ ] Accuracy percentage is calculated correctly
- [ ] Powerup awards show correct player icons (30x20)
- [ ] Conduct awards show correct player icons (30x20)
- [ ] All players in game are shown (even if dead)
- [ ] Players shown in order (1, 2, 3, 4)
- [ ] Sections appear at correct timing (halfway point)
- [ ] Sections scroll until off-screen
- [ ] "THANK YOU FOR PLAYING" appears with correct font/size
- [ ] Password blinks for 5 seconds (1 blink/second)
- [ ] Password shows solid after 5 seconds
- [ ] Password only appears on victory (Hard Mode + powerups not High)
- [ ] Final message appears on victory when password condition not met
- [ ] Credits end after "THANK YOU FOR PLAYING" on defeat
- [ ] Credits continue to final message on victory

## Questions for Clarification

1. **Enemies Destroyed**: Should this count:
   - Only aliens killed by bullets?
   - Aliens killed by shockwaves?
   - Aliens killed by collision?
   - Minions?
   - Bonus wave enemies?
   - **Assumption**: All enemies (aliens, minions, bonus wave) killed by any player action

2. **Shield Recharge Shots**: Should this count:
   - Only shots that actually improve shield stage?
   - All shots that hit shield for recharge (even if stage doesn't improve)?
   - **Assumption**: All shots that hit shield for recharge (both `heal(1)` and `register_recharge_hit()`)

3. **Player Display**: Should players be shown:
   - In order 1, 2, 3, 4 regardless of who joined?
   - Only players that actually played?
   - **Assumption**: Show all players that were in game at start, in order 1-4

4. **Accuracy**: Currently tracks bullets_fired and bullets_hit. Is this:
   - Only player bullets?
   - Including squadron bullets?
   - **Assumption**: Only player bullets (squadrons are separate)

