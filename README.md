# README #

vscode-workspace-launcher

### What is this repository for? ###

* A utility to list and launch VSCode workspaces.

### Setup/Requirements ###

* Install the following Python modules:
    * PySimpleGUI
        * ```py -m pip install pysimplegui```
    * PyInstaller
        * ```py -m pip install pyinstaller```
    * PyInstaller VersionFile
        * ```py -m pip install pyinstaller-versionfile```

### Usage ###

* To generate a stand-alone executable, run the following command:
    * ```pyinstaller --onefile vscode_workspace_launcher.py --windowed --icon=rocket.ico --version-file=version.txt```<br><br>
* To update the properties (version number, etc.) of the executable, do the following before generating the .exe:
    * Edit "version.yaml" with the values you want for the properties, then run the following command:
    * ```create-version-file version.yaml --outfile version.txt```<br><br>
* To run with the default VSCode paths, leave path items in settings.json set to ```default```<br><br>
* To run with VSCode paths other than the defaults, edit the settings.json file:
    * exe_path:
        * This is the path to the Visual Studio Code executable
        * Default: ```C:\\Users\\{USERNAME}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe```
    * workspace_path:
        * This is the path to the folder containingVisual Studio Code workspaces
        * Default: ```C:\\Users\\{USERNAME}\\AppData\\Roaming\\Code\\User\\workspaceStorage```
    * username:
        * The user whose workspaces should be displayed
        * Default: Current Windows User<br><br>
* To change the position where the window appears when launched, modify the ```x_position``` and/or ```y_position``` values in settings.json
    * x_position: (```"x_position": n```) where n is an integer:
        * n > 0: places the top, left corner n pixels from the left of the screen.
        * n < 0: places the top, left corner n pixels from the right of the screen.
        * n = 0: will be treated as a 10-pixel offset from the left
    * x_position: (```"y_position": n```) where n is an integer:
        * n > 0: places the top, left corner n pixels from the top of the screen.
        * n < 0: places the top, left corner n pixels from the bottom of the screen.
        * n = 0: will be treated as a 10-pixel offset from the top

### Known Conflicts/Compatibility Notes ###

* N/A

### Documentation ###

* See "Usage" (above)

### Version History ###

* v1.0 - 1/15/2024 - Initial release
