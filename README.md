# README #

vscode-workspace-launcher

### What is this repository for? ###

* A utility to list and launch VSCode workspaces.

### Setup/Requirements ###

* List of requirements for project:
    * PySimpleGUI
        * ```py -m pip install pysimplegui```
    * PyInstaller
        * ```py -m pip install pyinstaller```

### Usage ###

* To generate a stand-alone executable, run the following command:
    * ```pyinstaller --onefile vscode_workspace_launcher.py --windowed --icon=vscode.ico```<br><br>
* To run with the default VSCode paths, leave all items in settings.json set to ```default```<br><br>
* To run with VSCode paths other than the defaults, edit the settings.json file:
    * exe_path:
        * This is the path to the Visual Studio Code executable
        * Default: ```C:\\Users\\{USERNAME}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe```
    * workspace_path:
        * This is the path to the folder containingVisual Studio Code workspaces
        * Default: ```C:\\Users\\{USERNAME}\\AppData\\Roaming\\Code\\User\\workspaceStorage```
    * username:
        * The user whose workspaces should be displayed
        * Default: Current Windows User

### Known Conflicts/Compatibility Notes ###

* N/A

### Documentation ###

* See "Usage" (above)

### Version History ###

* v1.0 - 1/15/2024 - Initial release
