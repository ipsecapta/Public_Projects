**INDEX:**

**assets/:** contains the open-source proprietary font for the game.

**cursor\_devreports/**:Contains AI-generated reports on various issues, created for troubleshooting purposes.

**img/**: game images for sprites and backgrounds. Majority generated in Gemini or ChatGPT, and edited for better graphic design/consistency using GIMP. Some (like  MAC\_round3.png) were created by hand from scratch.

**sounds/**: game sounds, several still unused but prerecorded. All sound editing was done in Audacity.
_______________________________________________________________________________________________________


**GAME DESCRIPTION:**
Arcade shooter with multi-wave, scaled difficulty gameplay format. Passion project, initial codebase done by hand ([check out other directories](https://github.com/ipsecapta/Public_Projects/tree/main/Python_Game/Old_Code) for work-in-progress snapshots)
This is a 'homemade' Python-based Alien Invasion Game.
I use the experience of building and expanding it to continually build new skills in Python, both with manual and AI-assisted coding.

___

**GOALS IN BUILDING THE GAME:**

1)**Recapture the communal spirit of arcade gaming,** where friend groups are geographically together (as opposed to just remotely connected), spending quality time around the arcade. 
>>>Current single-keyboard + multiplayer setup meets this goal.

2)**Lean into a "homegrown" feel.** Sound effects made by the people playing the game are ported into the game. Current method is multistep process: Raw audio request -> Manual Audacity Edits -> clean sounds/ directory that maps into the sound_manager.py module. 
>>>Next steps: improve the recording process into a more prescriptive / guided workflow for the user; prompt for sounds     one  at a time, specifying length; allow playback for user to rerecord and tweak as desired; on final save, auto-adjust     volume, and save directly to the sounds directory.
>>>Distant goal: Custom Sprites.

___
**CUSTOMIZATION FEATURES:** 

-Options Menu: Allows for powerups, lifepods (after-death player participation), and game difficulty to be adjusted

-Settings Menu: User can choose custom player movement/fire keys, toggle sound on/off, change resolution

**GAMEPLAY FEATURES:**
-Scaled multiplayer: sprites get smaller to make field larger; more enemies spawn.
- 8 base enemy models, with 20+ damage-stage and death-animation sprites
- Powerups for ally/healer and firepower boosts; XP-based leveling up; optional "escape pod" dynamic that allows dead players to keep participating
- End Credits: Game tracks and then announces user stats and accomplishments, while "celebration mode" has all player bullets change to behave like fireworks.
- Secret wave built around cat memes. See [password\_spoiler.txt](https://github.com/ipsecapta/Public_Projects/blob/main/Python_Game/Current_Iteration/password_spoiler.txt) (or hunt in the code like an a grownup) if you want to find the password for access to it. Otherwise you have to beat the game on hard (like a REAL grownup ;)&nbsp;), with powerups set to either normal or low.


&nbsp;	Many features left to add. Check back for updates.


__



_NOTE: Most in‑game music is sourced from public‑domain or royalty‑free libraries. The Hard Mode victory theme includes the track “Believe” by Thomas Bergersen, for which full credit is given here to the artist. This project is entirely non‑commercial and does not generate any revenue._
