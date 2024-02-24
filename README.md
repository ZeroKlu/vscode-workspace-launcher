# README #

Workspace Launcher for Visual Studio Code

---

### What is this repository for? ###

* A utility to list and launch VSCode workspaces.
* Currently only supports Windows (tested on Windows 10 and 11)

---

### Roadmap ###

* Add Linux support
* Clean up appearance
* Allow sort by latest used date instead of parent folder > workspace name

---

### What's in here? ###

#### Program Files ####

* **workspace.py**: implements the ***Workspace*** class, which defines a VS Code workspace
    * Attributes:
        * **vsc_folder** (*str*): path to the folder that contains the VS Code workspace.json file
        * **workspace** (*str*): path to the workspace folder
        * **name** (*str*): folder name for the workspace
        * **parent** (*str*): parent folder name (that contains the workspace folder)
        * **repo_uri** (*str*): URI to the GIT repository for the workspace (if one exists)
        * **exists** (*bool*): True if the workspace folder is defined and exists
        * **show_repo** (*bool*): When True, show the repository in the display name
        * **show_glyph** (*bool*): When True, prepend the glyph to the repository if applicable
    * Properties:
        * **display_name** (*str*): Display name for the workspace in the select list
    * Methods:
        * **from_vscode_folder**: Class Method to generate a Workspace Instance given the path to a VS Code folder (containing a workspace.json file)
            * Arguments:
                * vsc_folder (*str*): The path to the VS Code folder
                * show_repo (*bool* default=True): When true, include the repository in the display name
                * show_glyph (*bool* default=False): When true, prepend the glyph to the repository in the display name
            * Code Sample:
              ```python
              from workspace import Workspace
              vsc_folder = "C:\\Users\\USERNAME\\AppData\\Roaming\\Code\\User\\workspaceStorage\\0d14953ffbc0e69d994e7b502e8cc120"
              workspace = Workspace.from_vscode_folder(vsc_folder)
              ```
        *  **from_workspace_folder**: Class Method to generate a Workspace Instance given the path to a workspace (containing code files)
            * Arguments:
                * workspace_folder (*str*): The path to the workspace folder
                * vsc_folder (*str*): The path to the VS Code folder
                * show_repo (*bool* default=True): When true, include the repository in the display name
                * show_glyph (*bool* default=False): When true, prepend the glyph to the repository in the display name
            * Code Sample:
              ```python
              from workspace import Workspace
              ws_folder = "C:\\My Python Project"
              workspace = Workspace.from_vscode_folder(ws_folder)
              ```

* **workspace_settings.py**: Implements the ***WorkspaceSettings*** class, which models a settings object to control behaviors throughout the project. This class is also represented one-for-one in the *settings.json* configuration file.
    * Attributes:
        * **exe_path** (*str* default="default"): Path to the VS Code executable
            * Default points to:<br>
            ```C:\\Users\\{USERNAME}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe```
        * **workspace_path** (*str* default="default"): Path to the workspace folder
            * Default points to:<br>
            ```C:\\Users\\{USERNAME}\\AppData\\Roaming\\Code\\User\\workspaceStorage```
        * **username** (*str* default="default"): Username to use to get workspaces
            * Default will be the currently logged-in user
        * **hide_missing** (*bool* default=True): When true, missing workspace folders are omitted from the select list
        * **clean_up_orphans** (*bool* default=False): When true, missing workspace folders have their related VS Code folders removed
        * **show_repos** (*bool* default=True): When true, the repository URL is shown in the select list
        * **font** (*str* default="Consolas"): Name of font to use in the UI
            * Font must already be installed on the system
            * If using the *show_glyphs* option, the font must be a nerd font that includes the Bitbucket and GitHub glyphs
        * **font_size** (*int* default=10): Size of the font to use in the UI
        * **show_glyphs** (*bool* default=False): When true, a glyph is prepended to the repository URL
            * Currently only supports
                * Bitbucket
                * GitHub
        * **x_location** (*int* default=10): Horizontal location of the UI (top-left corner)
            * Measures from the left of the screen
            * Supports a negative number to measure from the right of the screen
        * **y_location** (*int* default=-160): Vertical location of the UI (top-left corner)
            * Measures from the top of the screen
            * Supports a negative number to measure from the bottom of the screen
    * Methods:
        * **from_file**: Class method to generate a *WorkspaceSettings* instance from a JSON file
            * Arguments:
                * filename (*str*): The filename to load
                * folder (*str*): Optional folder name the file is in
            * Code Sample:
            ```python
            from workspace_settings import WorkspaceSettings
            settings = WorkspaceSettings.from_file("settings.json")
            ```
        * **from_dict**: Class method to generate a *WorkspaceSettings* instance from a dictionary
            * Arguments:
                * settings (*dict[str, any]*): Dictionary containing settings values.
                    * Note: Keys must exactly match the class attribute names
            * Code Sample:
            ```python
            import json
            from workspace_settings import WorkspaceSettings
            my_dict = json.load("settings.json")
            settings = WorkspaceSettings.from_dict(my_dict)
            ```
        * **_get_user**: Internal class method to get the username attribute for the *WorkspaceSettings* instance.
            * Used by the *from_file* and *from_dict* methods
            * When the value is "default" returns the logged-in user
            * Arguments:
                * **username** (*str*): The currently set username value
        * **_get_user_paths**: Internal class method to get the paths to the VS Code executable and VS Code workspace directory
            * Used by the *from_file* and *from_dict* methods
            * Arguments:
                * **username** (*str*): The currently set username value
                * **exe_path** (*str*): The currently set exe_path value
                    * Converts "default" to the path to the exe
                * **ws_path** (*str*): The currently set ws_path value
                    * Converts "default" to the path to the workspaces folder

* **workspace_locator.py**: Implements the ***WorkspaceLocator*** class, which generates the list of all workspaces in the user's workspace directory for display in the UI select list.
    * Attributes:
        * **_settings** (*WorkspaceSettings*): The settings for the current execution
        * **_workspaces** (*list[Workspace]*): The list of workspaces found for the user
            * This should be accessed from within the class only, as it does not obey settings filters like *hide_missing* (see property below)
    * Properties:
        * **workspaces** (*list[Workspace]*): The list of workspaces to display in the UI
            * Filters out missing workspaces if the *hide_missing* attribute is true in the *_settings* object
    * Methods:
        * **load_workspaces**: Traverses the VS Code workspace directories and generates the list of workspaces, sorted by *display_name*
            * Arguments: (none)
        * **clean_up_orphans**: Traverses the list of workspaces and deletes the VS Code reference folders for any that are missing (Workspace.exists == False).
            * Does not execute unless _settings.clean_up_orphans == True
            * Arguments: (none)

* **workspace_launcher.py**

---

### Setup/Requirements ###

* Install the following Python modules:
    * PySimpleGUI
        * ```py -m pip install pysimplegui```
    * sm-utils
        * ```py -m pip install sm_utils```
* If you want to compile this to an executable, install the following additional Python modules:
    * PyInstaller
        * ```py -m pip install pyinstaller```
    * PyInstaller VersionFile
        * ```py -m pip install pyinstaller-versionfile```

### Usage ###

* To run the application without creating an executable:
    * If *settings.json* is in the same directory as the Python files, run the following command from the terminal:<br>
      ```python.exe workspace_program.py```
    * To point to your JSON file with a different name or at a different location, add its relative path as an argument:<br>
      ```python.exe workspace_program.py settings\my_settings.json```

* To generate a stand-alone executable, run the following command:
    * ```pyinstaller --onefile workspace_program.py --windowed --add-data "rocket.ico:." --icon=rocket.ico --version-file=version.txt```<br><br>
* To update the properties (version number, etc.) of the executable, do the following before generating the .exe:
    * Edit "version.yaml" with the values you want for the properties, then run the following command:
    * ```create-version-file version.yaml --outfile version.txt```<br><br>
* Make sure a copy of settings.json is in the same directory as the compiled executable<br><br>
* To run with the default VSCode paths, leave path items in settings.json set to ```default```<br><br>
* To run with VSCode paths other than the defaults, edit the settings.json file:
    * exe_path:
        * This is the path to the Visual Studio Code executable
        * Default (Windows):<br>
        ```C:\\Users\\{USERNAME}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe```
    * workspace_path:
        * This is the path to the folder containingVisual Studio Code workspaces
        * Default (Windows):<br>
        ```C:\\Users\\{USERNAME}\\AppData\\Roaming\\Code\\User\\workspaceStorage```
    * username:
        * The user whose workspaces should be displayed
        * Default: Current Windows User<br><br>

* To change the position where the window appears when launched, modify the ```x_location``` and/or ```y_location``` values in settings.json
    * x_location: (```"x_location": n```) where n is an integer:
        * n > 0: places the top, left corner n pixels from the left of the screen.
        * n < 0: places the top, left corner |n| pixels from the right of the screen.
        * n = 0: will be treated as a 10-pixel offset from the left
    * y_location: (```"y_location": n```) where n is an integer:
        * n > 0: places the top, left corner n pixels from the top of the screen.
        * n < 0: places the top, left corner |n| pixels from the bottom of the screen.
        * n = 0: will be treated as a 10-pixel offset from the top

* The following additional parameters can be set in the settings.json file:
    * ```hide_missing```
        * When ```true```, workspaces whose folders are missing will not be included in the select list
    * ```clean_up_orphans```
        * When ```true```, workspaces whose folders are missing will have their VS Code workspace folders removed
        * This is obviously an aggressive step, so leave this ```false``` unless you're absolutely sure you don't want them around
    * ```show_repos```
        * When ```true```, names in the select list will include their repository URLs
    * ```show_glyphs```
        * When ```true```, repository URLs (if displayed) will be prepended with the nerd-font glyphs for their sites.
        * Currently only supports the following:
            * Bitbucket
            * GitHub
        * Note: This feature requires that the ```font``` setting (below) be an installed nerd font with the glyphs available
            * I use the "CaskaydiaCove Nerd Font" for example
    * ```font```
        * Name of the (installed) font to be used in the UI
    * ```font_size```
        * Display size of the font in the UI as ```"font_size": <int>```
        * I recommend not setting this lower than 10 or higher than 20

### Known Conflicts/Compatibility Notes ###

* Default paths only support Windows

### Documentation ###

* See "Usage" (above)

### Version History ###

* v1.0 - 1/15/2024 - Initial release
