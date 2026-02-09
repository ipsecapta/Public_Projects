# Sound System Analysis Report

## 1. Sounds Unable to Load (Missing Files)

Based on the `_load_variants()` calls and the actual files in the `/sounds` directory:

### Missing Files:
1. **`announce_game_opens`** - Tries to load 3 variants (`announce_game_opens_1.wav` through `announce_game_opens_3.wav`)
   - **Status**: NO FILES EXIST
   - **Similar files**: None found

2. **`announce_game_start`** - Tries to load 1 variant (`announce_game_start_1.wav`)
   - **Status**: NO FILES EXIST
   - **Similar files**: None found

3. **`announce_defeat`** - Tries to load 2 variants (`announce_defeat_1.wav`, `announce_defeat_2.wav`)
   - **Status**: NO FILES EXIST
   - **Similar files**: None found

4. **`announce_victory`** - Tries to load 2 variants (`announce_victory_1.wav`, `announce_victory_2.wav`)
   - **Status**: NO FILES EXIST (neither variant exists in the directory)
   - **Similar files**: None found

5. **`announce_new_wave`** - Tries to load 1 variant (`announce_new_wave_1.wav`)
   - **Status**: FILE EXISTS (but code expects 1, file shows `announce_new_wave_1.wav` and `announce_new_wave_2.wav` exist)
   - **Note**: Code loads 1 variant but 2 files exist - this is fine, just underutilized

6. **`alien_breach`** - Tries to load 1 variant (`alien_breach_1.wav`)
   - **Status**: NO FILES EXIST
   - **Similar files**: None found

7. **`powerup_railgun_charge`** - Tries to load 3 variants
   - **Status**: Only `powerup_railgun_charge_1.wav` exists, missing `_2.wav` and `_3.wav`
   - **Similar files**: `powerup_railgun_charge_1.wav` exists

8. **`powerup_railgun_fire`** - Tries to load 3 variants
   - **Status**: Only `powerup_railgun_fire_1.wav` and `powerup_railgun_fire_2.wav` exist, missing `_3.wav`
   - **Similar files**: Files exist but incomplete set

9. **`powerup_emp`** - Tries to load 3 variants
   - **Status**: NO FILES EXIST
   - **Similar files**: None found

10. **`powerup_squadron_hello`** - Tries to load 3 variants
    - **Status**: Only `powerup_squadron_hello_1.wav` and `powerup_squadron_hello_2.wav` exist, missing `_3.wav`
    - **Similar files**: Files exist but incomplete set

11. **`player_level_up`** - Tries to load 3 variants
    - **Status**: Only `player_level_up_1.wav` and `player_level_up_2.wav` exist, missing `_3.wav`
    - **Similar files**: Files exist but incomplete set

12. **`alien_lvl1to3_death`** - Tries to load 4 variants
    - **Status**: Only `alien_lvl1to3_death_1.wav`, `alien_lvl1to3_death_3.wav`, and `alien_lvl1to3_death_4.wav` exist
    - **Missing**: `alien_lvl1to3_death_2.wav`
    - **Note**: This will cause a warning but won't break (missing variant 2)

## 2. Sounds Loaded But Not Used

Sounds that are loaded into the dictionary but never called with `_play()`:

1. **`announce_game_opens`** - Loaded (3 variants expected, 0 exist), never called
2. **`announce_game_start`** - Loaded (1 variant expected, 0 exist), never called
3. **`alien_breach`** - Loaded (1 variant expected, 0 exist), never called (commented out at line 3404)
4. **`powerup_railgun_charge`** - Loaded (3 variants, 1 exists), never called
5. **`powerup_railgun_fire`** - Loaded (3 variants, 2 exist), never called
6. **`powerup_emp`** - Loaded (3 variants, 0 exist), never called
7. **`player_death`** - Loaded (2 variants exist), never called (commented out at lines 3095, 3276)
8. **`alien_lvl4_hum`** - Loaded (1 variant exists), never called (hum sounds are played elsewhere, but this specific one isn't)
9. **`alien_destroyer_hum`** - Loaded (1 variant exists), never called
10. **`alien_cruiser_hum`** - Loaded (1 variant exists), never called
11. **`alien_tanker_hum`** - Loaded (1 variant exists), never called
12. **`transcendence_cat_music`** - Loaded (1 variant exists), never called
13. **`nyan_cat_music`** - Loaded (1 variant exists), never called (might be used in bonus wave, need to check)

## 3. Sound Calls That Reference Unloaded Sounds

Sounds called with `_play()` but NOT loaded in `load_sounds()`:

**NONE FOUND** - All sound calls reference sounds that are loaded in the dictionary.

## 4. Potential File Naming Mismatches

Based on the file listing, all loaded sounds appear to use the correct naming convention (`{base_name}_{var_num}.wav`). However, there are some files in the directory that are NOT loaded:

### Unused Files in /sounds Directory:
1. **`alien_bombarder_death_1.wav`** - Not loaded (bombarder not implemented)
2. **`plasma_fire_1.wav`** - Not loaded (bombarder not implemented, commented out)
3. **`shield_laser_collision_1.wav`** and **`shield_laser_collision_2.wav`** - Not loaded (might be for a feature not yet implemented)
4. **`small_pop_1.wav`** - Not loaded (unused)
5. **`waow3.wav`** - Not loaded (unused, also wrong extension - should be .wav but might be misnamed)

## Summary

### Critical Issues:
- **6 sounds completely missing**: `announce_game_opens`, `announce_game_start`, `announce_defeat`, `announce_victory`, `alien_breach`, `powerup_emp`
- **Several sounds with incomplete variant sets**: `powerup_railgun_charge` (missing 2 variants), `powerup_railgun_fire` (missing 1 variant), `powerup_squadron_hello` (missing 1 variant), `player_level_up` (missing 1 variant), `alien_lvl1to3_death` (missing variant 2)

### Unused Sounds:
- **13 sounds loaded but never called**, including hum sounds, railgun sounds, EMP, and some announcements

### No Misnamed Calls:
- All `_play()` calls reference correctly named dictionary keys

