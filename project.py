"""
This module combines all of the modular components for the workspace launcher
  as a single file for use with PyInstaller
"""

#region Imports
from dataclasses import dataclass
from sm_utils import file_path
from os import path, getlogin, scandir
import urllib.parse as up
from pathlib import Path
import sys
import json
import shutil
import webbrowser
import PySimpleGUI as sg
import subprocess
import platform
#endregion

#region WorkspaceSettings
@dataclass
class WorkspaceSettings:
    """Settings model"""

    #region Attributes
    exe_path: str="default"         # Path to the VS Code exe
    workspace_path: str="default"   # Path to the workspace
    username: str="default"         # Username
    hide_missing: bool=True         # When true, missing workspace folders are omitted from the select list
    clean_up_orphans: bool=False    # When true, missing workspace folders have their related VSC folders removed
    show_repos: bool=True           # When true, the repository URL is shown in the select list
    font: str="Consolas"            # Name of font to use in the UI
    font_size: int=10               # Size of the font to use in the UI
    show_glyphs: bool=False         # When true, a glyph is prepended to the repository URL
    x_location: int=10              # Horizontal location of the UI in pixels from the left of the screen
    y_location: int=-160            # Vertical location of the UI in pixels from the top of the screen
    #endregion

    def __post_init__(self):
        """Initialize the default values if necessary"""
        if self.username == "default":
            self.username = WorkspaceSettings._get_user(self.username)
        if self.exe_path == "default" or self.workspace_path == "default":
            self.exe_path, self.workspace_path = WorkspaceSettings._get_user_paths(self.username, self.exe_path, self.workspace_path)

    #region Static Factory Methods
    @classmethod
    def from_file(cls, filename: str, folder: str=None) -> "WorkspaceSettings":
        """Factory for creating WorkspaceSettings from a JSON file"""
        filepath = file_path(filename, folder)
        if not path.isfile(filepath):
            # If the JSON file doesn't exist, we can only return the default settings
            return cls()
        settings = json.loads(Path(filepath).read_text())
        return WorkspaceSettings.from_dict(settings)

    @classmethod
    def from_dict(cls, settings: dict[str, any]) -> "WorkspaceSettings":
        """Factory for creating WorkspaceSettings from a settings dictionary"""
        settings = cls(**settings)
        # Obtain the paths that are relative to the user
        settings.username = WorkspaceSettings._get_user(settings.username)
        settings.exe_path, settings.workspace_path = WorkspaceSettings._get_user_paths(
            settings.username, settings.exe_path, settings.workspace_path)
        return settings
    #endregion

    #region Static Helper Functions
    @classmethod
    def _get_user(cls, username: str) -> str:
        """Get the username for the settings"""
        return getlogin() if username.lower() == "default" else username

    @classmethod
    def _get_user_paths(cls, username: str, exe_path: str, ws_path: str) -> tuple[str, str]:
        """Get the AppData paths for the settings user"""
        user_path = path.expanduser(f"~{username}")
        if exe_path.lower() == "default":
            exe_path = path.join(user_path, "AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
        if ws_path.lower() == "default":
            ws_path = path.join(user_path, "AppData\\Roaming\\Code\\User\\workspaceStorage")
        return (exe_path, ws_path)
    #endregion
#endregion

#region Workspace
@dataclass
class Workspace:
    """Defines a workspace"""

    #region Attributes
    vsc_folder: str=None    # Folder where VS Code stores the workspace.json file describing the workspace
    workspace:  str=None    # Full path to the workspace folder
    name:       str=None    # Folder name containing the workspace files
    parent:     str=None    # Parent folder (containing the 'name' folder above)
    repo_uri:   str=None    # URI to the GIT repository for the workspace (if one exists)
    exists:     bool=False  # True if the workspace folder is defined and exists
    show_repo:  bool=True   # When True, show the repository in the display name
    show_glyph: bool=True   # When True, show the glyph in the display name
    #endregion

    #region Properties
    @property
    def display_name(self) -> str:
        """Display name for the workspace when presented to the user"""
        name: str = f"{self.parent} > {self.name}"
        missing: bool = "" if self.exists else " (missing)"
        bb_glyph: str = " " if self.show_glyph else ""
        gh_glyph: str = " " if self.show_glyph else ""
        repo: str = ""
        if self.repo_uri and self.show_repo:
            if "github.com" in self.repo_uri.lower():
                repo = f" | {bb_glyph}{self.repo_uri}"
            elif "bitbucket.org" in self.repo_uri.lower():
                repo = f" | {gh_glyph}{self.repo_uri}"
            else:
                repo = f" | {self.repo_uri}"
        return f"{name}{repo}{missing}"
    #endregion

    #region Static Factory Methods
    @classmethod
    def from_vscode_folder(cls, vsc_folder: str, show_repo: bool=True, show_glyph: bool=False) -> "Workspace":
        """Factory: Initialize from vscode folder path only"""
        if vsc_folder is None or not path.isdir(vsc_folder):
            # If the VSCode folder does not exist, we cannot create a Workspace object
            return None
        json_path = path.join(vsc_folder, "workspace.json")
        if not path.isfile(json_path):
            # If the workspace.json file does not exist, we cannot create a Workspace object
            return None
        json_data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        if "folder" not in json_data:
            # If the JSON data does not contain 'folder', we cannot create a Workspace object
            return None
        # Decode the URL-encoded workspace folder path
        ws_path = up.unquote(json_data["folder"][8:]).replace("/", "\\")
        return Workspace.from_workspace_folder(ws_path, vsc_folder, show_repo, show_glyph)

    @classmethod
    def from_workspace_folder(cls, workspace_folder: str, vsc_folder: str=None, show_repo: bool=True, show_glyph: bool=False) -> "Workspace":
        """Factory: Initialize from workspace folder path only"""
        # Create the Workspace object and set the folder paths
        ws = cls()
        ws.show_repo = show_repo
        ws.show_glyph = show_glyph
        ws.vsc_folder = vsc_folder
        ws.workspace = workspace_folder
        ws_path= Path(ws.workspace)
        # Add the name and parent name (for later sorting)
        ws.name = ws_path.name
        ws.parent = ws_path.parent.name
        if not ws.parent:
            ws.parent = workspace_folder.split("/")[0].split("\\")[0].upper()
        if not path.isdir(ws.workspace):
            # If the workspace folder does not exist, we cannot obtain any additional details
            ws.exists = False
            return ws if ws.vsc_folder else None
        # Workspace folder exists
        ws.exists = True
        git_folder= path.join(ws.workspace, ".git")
        if not path.isdir(git_folder):
            # If there is no .git directory, we're done
            return ws
        git_file = path.join(git_folder, "config")
        if not path.isfile(git_file):
            # If the .git directory doesn't contain a 'config' file, we're done
            return ws
        git_list = [line for line in Path(git_file).read_text().splitlines() if line.strip().lower().startswith("url")]
        if not git_list:
            # If there is no URL in the Git config file, we're done
            return ws
        git_data = git_list[0]
        # Add the Git URL to the Workspace object
        ws.repo_uri = git_data.split("=")[1].strip()
        return ws
    #endregion
#endregion

#region WorkspaceLocator
class WorkspaceLocator:
    """Locator for VS Code Workspaces on PC"""

    #region Constructor
    def __init__(self, settings: WorkspaceSettings=None, settings_json: dict[str, any]=None, settings_file: str=None) -> None:
        """Initialize"""
        # Get settings
        self._settings = settings
        if not self._settings:
            try:
                self._settings = WorkspaceSettings.from_dict(settings_json) if settings_json else WorkspaceSettings.from_file(settings_file)
            except:
                self._settings = WorkspaceSettings()
        self._workspaces = self.load_workspaces()
        if self._settings.clean_up_orphans:
            self.clean_up_orphans()
    #endregion
    
    #region Properties
    @property
    def workspaces(self) -> list[Workspace]:
        return self._workspaces if not self._settings.hide_missing else [w for w in self._workspaces if w.exists]
    #endregion

    #region Helper Functions
    def load_workspaces(self) -> list[Workspace]:
        """Scans the PC for VS Code workspaces"""
        folders = [f.path for f in scandir(self._settings.workspace_path) if f.is_dir()]
        workspaces = [Workspace.from_vscode_folder(f, self._settings.show_repos, self._settings.show_glyphs) for f in folders]
        return sorted([w for w in workspaces if w is not None], key=lambda w: w.display_name)

    def clean_up_orphans(self) -> None:
        """Delete orphan workspaces"""
        for workspace in [w for w in self._workspaces if not w.exists]:
            shutil.rmtree(workspace.vsc_folder)
        self._workspaces = self.load_workspaces()
    #endregion
#endregion

#region WorkspaceLauncher
class WorkspaceLauncher:
    """UI for interacting with the list of workspaces"""

    #region Constructor
    def __init__(self, settings: WorkspaceSettings=None, settings_file: str=None) -> None:
        """Initialize"""
        self._settings = settings
        if not self._settings:
            self._settings = WorkspaceSettings.from_file(settings_file) if settings_file else WorkspaceSettings()
        self._workspace_locator = WorkspaceLocator(self._settings)
        
        # UI Controls:
        text = (self._settings.font, self._settings.font_size)
        # Text box for the user to type a filter for the workspaces
        self.workspace_filter = sg.InputText(
            enable_events=True,
            font=text,
            key="-FILTER-"
        )
        # Checkbox to indicate whether to launch the workspace in VS Code
        self.vsc_toggle = sg.Checkbox(
            text="Open in VS Code",
            default=True,
            enable_events=True,
            key="-VSC-"
        )
        # Checkbox to indicate whether to launch the repo URL in a browser
        self.url_toggle = sg.Checkbox(
            text="Launch repo URL",
            default=False,
            enable_events=True,
            key="-URL-"
        )
        # Create and populate the workspace select list
        self.workspace_selector = sg.Combo(
            [w.display_name for w in self._workspace_locator.workspaces],
            enable_events=True,
            font=(self._settings.font, self._settings.font_size),
            key="-DROPDOWN-"
        )
        # UI window layout
        self.window_layout = [
            [sg.Text("Filter:", font=text), self.workspace_filter, self.vsc_toggle, self.url_toggle],
            [self.workspace_selector]
        ]
        # UI Window
        self.window = sg.Window(
            title="Workspace Launcher for Visual Studio Code",
            icon=self.resource_path("rocket.ico"),
            layout=self.window_layout,
            margins=(0, 0)
        )
        self.window.Location = self.get_ui_position(self.window)
    #endregion

    #region GUI Execution
    def create_ui(self) -> None:
        """Generate and launch the GUI"""
        # Get the list of workspaces to display in the drop-down list
        workspaces = self._workspace_locator.workspaces
        
        # Set the initial values for tracking variables
        selected_workspace = None
        filter_text = ""

        # Run the UI until the user closes the window
        while True:
            # Listen for events
            event, values = self.window.read()

            if event == sg.WIN_CLOSED:
                # Halt processing if the user closes the UI
                break

            if event == "-FILTER-" and values["-FILTER-"] != filter_text:
                # Reload the filtered workspace list if the user changes the filter text
                filter_text = values["-FILTER-"]
                workspaces = self.on_filter_change(filter_text)
                if selected_workspace not in workspaces:
                    selected_workspace = None

            if event == "-DROPDOWN-":
                # When the user selects a workspace from the dropdown list, perform the action(s) identified
                #   by the checkboxes
                selected_workspace = next(w for w in workspaces if w.display_name == values["-DROPDOWN-"])
                self.on_workspace_select(selected_workspace)

            if event == "-VSC-":
                # When the user checks the workspace checkbox (with a workspace selected),
                #   launch the workspace in VS Code
                self.on_vsc_toggle_change(selected_workspace)

            if event == "-URL-":
                # When the user checks the URL checkbox (with a workspace selected),
                #   launch the repository (if it exists) in the browser
                self.on_url_toggle_change(selected_workspace)

        self.window.close()
    #endregion

    #region Event handlers
    def on_filter_change(self, filter_text: str):
        """Update the filtered workspace list when the user changes the filter text"""
        workspaces = [w for w in self._workspace_locator.workspaces if filter_text.lower() in w.display_name.lower()]
        self.window["-DROPDOWN-"].update(values=[w.display_name for w in workspaces])
        return workspaces

    def on_workspace_select(self, selected_workspace: Workspace) -> None:
        """Perform the selected actions when the user selects a workspace"""
        # Launch the workspace in VS Code
        if self.vsc_toggle.get():
            self.launch_workspace(selected_workspace)
        # Launch the repository (if one exists) in the browser
        if self.url_toggle.get():
            self.launch_repository(selected_workspace)
    
    def on_vsc_toggle_change(self, selected_workspace: Workspace) -> None:
        """Launch the workspace in VS code if the user checks the box while a workspace is selected"""
        if not self.vsc_toggle.get() or not selected_workspace:
            return
        self.launch_workspace(selected_workspace)
    
    def on_url_toggle_change(self, selected_workspace: Workspace) -> None:
        """Launch the repository in the default browser if the user checks the box while a workspace is selected"""
        if not self.url_toggle.get() or not selected_workspace:
            return
        self.launch_repository(selected_workspace)
    #endregion

    #region Helper functions
    def get_ui_position(self, window: sg.Window) -> tuple[int, int]:
        # Set the position for the UI window
        x_size, y_size = window.get_screen_dimensions()
        x, y = self._settings.x_location, self._settings.y_location
        x_pos = x if x > 0 else x_size + x
        y_pos = y if y > 0 else y_size + y
        return (x_pos, y_pos)
    
    def launch_workspace(self, selected_workspace: Workspace):
        """Open the selected workspace an instance of Visual Studio code"""
        # Launch a subprocess to open the workspace in VS Code
        args = [self._settings.exe_path, selected_workspace.workspace]
        subprocess.call(args)

    def launch_repository(self, selected_workspace: Workspace):
        """Open the repository (if one exists) for the selected workspace in the default browser"""
        # Get the workspace Identified by the display name
        if selected_workspace.repo_uri:
            # Open the browser to the repository
            webbrowser.open(selected_workspace.repo_uri)
        
    def resource_path(self, file_name: str) -> str:
        """Fix for issue with PyInstaller not respecting the icon"""
        base_path = getattr(sys, "_MEIPASS", path.dirname(path.abspath(__file__)))
        return path.join(base_path, file_name)
    #endregion
#endregion

#region WorkspaceProgram
#region Helper Functions
def verify_windows() -> bool:
    """Check that this is a Windows PC"""
    return platform.system() == "Windows"

def get_settings(json_path: str) -> WorkspaceSettings:
    """Read the settings.json file and load settings"""
    if not path.isfile(json_path):
        return None
    print(json_path)
    settings_dict = json.loads(Path(json_path).read_text())
    try:
        return WorkspaceSettings.from_dict(settings_dict)
    except:
        return None

def unsupported_os_alert(suppress_alert: bool=False) -> str:
    """Display an alert window if not running Windows"""
    ops = platform.system()
    if not suppress_alert:
        sg.popup_ok(f"Your OS ({ops}) is not yet supported by this application.")
    return f"Unsupported OS: {ops}"
#endregion

#region Main Function
def main() -> None:
    """Get settings from JSON file and run the WorkspaceLauncher"""
    if not verify_windows():
        exit(unsupported_os_alert())
    settings_path = file_path(sys.argv[1] if len(sys.argv) > 1 else "settings.json")
    settings = get_settings(settings_path)
    launcher = WorkspaceLauncher(settings=settings) if settings else WorkspaceLauncher()
    launcher.create_ui()
#endregion

#region Main Guard
if __name__ == "__main__":
    main()
#endregion
#endregion

#region Default settings.json File
# {
#     "exe_path": "default",
#     "workspace_path": "default",
#     "username": "default",
#     "hide_missing": true,
#     "clean_up_orphans": false,
#     "show_repos": true,
#     "font": "CaskaydiaCove Nerd Font",
#     "font_size": 10,
#     "show_glyphs": true,
#     "x_location": 10,
#     "y_location": -160
# }
#endregion
