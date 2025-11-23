# Distribution Guide

This guide explains how to build and distribute the Meal Planner application.

## Building the Standalone Executable

### For Windows

1. Open Command Prompt in the project directory
2. Run the build script:
   ```cmd
   build.bat
   ```
3. Wait for the build to complete (may take a few minutes)
4. The executable will be in `dist\MealPlanner.exe`

**File Size**: Approximately 15-25 MB (includes Python runtime)

### For macOS

1. Open Terminal in the project directory
2. Make the script executable (first time only):
   ```bash
   chmod +x build.sh
   ```
3. Run the build script:
   ```bash
   ./build.sh
   ```
4. The application bundle will be in `dist/MealPlanner.app`

**File Size**: Approximately 20-30 MB

### For Linux

1. Open Terminal in the project directory
2. Make the script executable (first time only):
   ```bash
   chmod +x build.sh
   ```
3. Run the build script:
   ```bash
   ./build.sh
   ```
4. The executable will be in `dist/MealPlanner`

**File Size**: Approximately 15-25 MB

## Distributing to Others

### Windows Distribution

**Option 1: Simple ZIP File**
1. Build the executable using `build.bat`
2. Copy these files to a new folder:
   - `dist\MealPlanner.exe`
   - `sample_recipes.json`
   - `QUICKSTART.md` (optional)
3. Compress the folder to a ZIP file
4. Share the ZIP file

**Users can:**
- Extract the ZIP
- Run `MealPlanner.exe` directly
- No Python installation required!

**Option 2: Installer (Advanced)**
- Use tools like Inno Setup or NSIS to create a professional installer
- Not covered in this guide

### macOS Distribution

**Option 1: DMG File (Recommended)**
1. Build the application using `build.sh`
2. Create a DMG file:
   ```bash
   hdiutil create -volname "Meal Planner" -srcfolder dist/MealPlanner.app -ov -format UDZO MealPlanner.dmg
   ```
3. Share the DMG file

**Users can:**
- Open the DMG
- Drag MealPlanner.app to Applications
- Run from Applications folder

**Option 2: ZIP File**
1. Compress `dist/MealPlanner.app` to ZIP
2. Include `sample_recipes.json` and `QUICKSTART.md`
3. Share the ZIP file

### Linux Distribution

**Option 1: AppImage (Universal)**
- Consider creating an AppImage for broader compatibility
- Requires additional setup (not covered here)

**Option 2: Compressed Archive**
1. Build the executable using `build.sh`
2. Create a tarball:
   ```bash
   tar -czf meal-planner-linux.tar.gz -C dist MealPlanner sample_recipes.json QUICKSTART.md
   ```
3. Share the tarball

**Users can:**
- Extract: `tar -xzf meal-planner-linux.tar.gz`
- Run: `./MealPlanner`

**Option 3: Distribution-Specific Packages**
- DEB for Debian/Ubuntu
- RPM for Fedora/RedHat
- Requires packaging knowledge (not covered here)

## What Users Need to Know

### Windows Users
- No Python required
- Double-click `MealPlanner.exe` to run
- Data stored in: `%APPDATA%\MealPlanner`
- May show security warning on first run (click "More info" → "Run anyway")

### macOS Users
- No Python required
- May need to allow app in System Preferences → Security & Privacy
- Right-click app and select "Open" on first run
- Data stored in: `~/Library/Application Support/MealPlanner`

### Linux Users
- No Python required
- May need to make executable: `chmod +x MealPlanner`
- Data stored in: `~/.local/share/mealplanner`

## Sample Data

Always include `sample_recipes.json` with your distribution so users can:
- Quickly test the application
- See example recipe formats
- Start using immediately

## License

This project uses the MIT License (see LICENSE file). You are free to:
- Use commercially
- Modify
- Distribute
- Use privately

## File Size Reduction (Optional)

If the executable is too large, you can:

1. **Use UPX compression** (already enabled in build script):
   - Reduces file size by 30-50%
   - May trigger some antivirus false positives

2. **Exclude unused modules** in `meal_planner_gui.spec`:
   ```python
   excludes=[
       'test', 'unittest', 'email', 'http', 'xml',
       'pydoc', 'doctest', 'argparse', 'matplotlib',
       'numpy', 'pandas', 'PIL', 'PyQt5', 'PyQt6', 'wx'
   ]
   ```

3. **One-folder vs One-file**:
   - Current setup: One-file (easier to distribute)
   - One-folder option: Faster startup, larger distribution

## Testing Your Distribution

Before sharing, test on a clean machine:

1. **Windows**: Test on a Windows PC without Python
2. **macOS**: Test on a Mac without Python
3. **Linux**: Test on a fresh Linux VM

Verify:
- Application launches correctly
- All features work (recipes, meal plans, grocery lists, pantry)
- Can import sample_recipes.json
- Can export grocery lists
- Data persists between runs

## Troubleshooting

### "Application can't be opened" (macOS)
- This is normal for unsigned apps
- Users should right-click → Open → confirm

### "Windows protected your PC" (Windows)
- Click "More info" → "Run anyway"
- Consider code signing for production distribution

### Antivirus false positives
- UPX compression may trigger warnings
- Disable UPX in spec file if needed
- Consider code signing certificate

## Version Control

When distributing updates:
1. Update version in `setup.py`
2. Update "What's New" in README
3. Build new executable
4. Test thoroughly
5. Distribute with release notes

## Support

Provide users with:
- QUICKSTART.md for getting started
- README.md for full documentation
- sample_recipes.json for testing
- Your contact information for support

---

**Ready to distribute?** Follow the platform-specific instructions above and share your Meal Planner application!
