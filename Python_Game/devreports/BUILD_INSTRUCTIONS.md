# PyInstaller Build Instructions for Alien Invasion Game

## Quick Start

### Option 1: Using the Spec File (Recommended)

1. **Build the executable:**
   ```bash
   pyinstaller AlienInvasion.spec
   ```

2. **Find your executable:**
   - The executable will be in: `dist/AlienInvasion.exe`
   - You can run it directly from there, or copy it to wherever you want

3. **Test the executable:**
   - Run `dist/AlienInvasion.exe` to test
   - Make sure all images and fonts load correctly

### Option 2: Using Command Line Directly

If you prefer not to use the spec file, you can use this command:

```bash
pyinstaller --onefile --windowed --add-data "img;img" --add-data "assets;assets" --name AlienInvasion Visintainer_A_AlienGame.py
```

**Note:** 
- On Windows, use semicolons (`;`) to separate paths in `--add-data`. On Linux/Mac, use colons (`:`).
- Use `--windowed` to hide console window (default) or `--console` to show it (for debugging).

## Detailed Explanation

### What the Spec File Does

- **Includes all Python modules** automatically (PyInstaller detects imports)
- **Bundles image files** from the `img/` folder
- **Bundles font files** from the `assets/` folder
- **Creates a single executable** (`--onefile` mode)
- **Hides console window** (`console=False`) - console is hidden by default (set to `True` to show for debugging)

### Customization Options

#### To Hide/Show Console Window:
Edit `AlienInvasion.spec` and change:
```python
console=False,  # Set to False to hide console (default), True to show for debugging
```

#### To Add an Icon:
1. Create or obtain an `.ico` file (e.g., `icon.ico`)
2. Place it in the project directory
3. Edit `AlienInvasion.spec` and change:
```python
icon=None,  # Change to 'icon.ico'
```

#### To Create a Folder Distribution (instead of single file):
Edit `AlienInvasion.spec` and change:
```python
exe = EXE(
    ...
    # Remove or comment out these lines:
    # a.zipfiles,
    # a.datas,
)
```

Then add at the end:
```python
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AlienInvasion',
)
```

This creates a folder with the executable and all dependencies (faster startup, but more files).

## Troubleshooting

### If images/fonts don't load:
- Make sure the `img/` and `assets/` folders are in the same directory as the executable
- Or use folder distribution mode (see above) which keeps the folder structure

### If you get import errors:
- Check that all Python modules are in the same directory
- PyInstaller should auto-detect them, but you can add to `hiddenimports` in the spec file if needed

### If the executable is large:
- This is normal - PyInstaller bundles Python interpreter and all dependencies
- Typical size: 50-100MB for a pygame game
- You can use UPX compression (already enabled in spec file) to reduce size slightly

### To reduce executable size:
1. Use `--exclude-module` to exclude unused modules
2. Use folder distribution instead of single file
3. Consider using `--strip` (already enabled)

## Testing Checklist

After building, test:
- [ ] Game launches without errors
- [ ] All images display correctly
- [ ] Fonts render correctly (menu text, banners)
- [ ] Sound works (if you add sound later)
- [ ] All game modes work (normal game, bonus wave)
- [ ] Menus function correctly
- [ ] Save/load works (if applicable)

## Distribution

When distributing your game:
1. Test the executable on a clean machine (without Python installed)
2. Include a README with system requirements
3. Consider creating an installer (e.g., using Inno Setup or NSIS)
4. The executable is standalone - no Python installation needed!

## Advanced: Creating an Installer

If you want to create a professional installer:

1. **Inno Setup** (Windows):
   - Download from: https://jrsoftware.org/isinfo.php
   - Create a script that installs the executable and creates shortcuts

2. **NSIS** (Windows):
   - Download from: https://nsis.sourceforge.io/
   - More complex but very powerful

3. **PyInstaller with Installer**:
   - Some tools can create installers automatically
   - Search for "PyInstaller installer creator"

## Notes

- The first build may take a few minutes
- Subsequent builds are faster (PyInstaller caches some data)
- The `build/` folder contains temporary files (can be deleted)
- The `dist/` folder contains your final executable
- Keep the spec file for future builds - it's easier than typing the full command

