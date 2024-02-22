"""
This WorkspaceLocator class obtains a list of all VS Code workspaces on the workstation.
"""

from workspace import Workspace
import json
from pathlib import Path
from os import path, getlogin, scandir
import shutil

class WorkspaceLocator:
    """Locator for VS Code Workspaces on PC"""

    default_settings = {
        "exe_path": "default",
        "workspace_path": "default",
        "username": "default",
        "hide_missing": True,
        "clean_up_orphans": False,
        "show_repos": True,
        "font": "CaskaydiaCove",
        "show_glyphs": False,
        "x_location": 10,
        "y_location": -160
    }

    def __init__(self, settings: dict[str, str]=None, settings_file: str=None) -> None:
        """Initialize"""
        # Get settings
        self._settings = WorkspaceLocator.load_settings(settings, settings_file)
        self._workspaces = self.load_workspaces()
        if self._settings["clean_up_orphans"]:
            self.clean_up_orphans()
    
    @property
    def workspaces(self):
        return self._workspaces if not self._settings["hide_missing"] else [w for w in self._workspaces if w.exists]

    @classmethod
    def load_settings(cls, settings: dict[str, str]=None, settings_file: str=None) -> dict[str, str]:
        """Initializes settings"""
        settings_dict = settings
        if settings_file:
            settings_dict = json.loads(Path(settings_file).read_text())
        if not settings_dict:
            settings_dict = WorkspaceLocator.default_settings

        # Populate values for settings defaults
        default_username = getlogin()
        username = default_username if settings_dict["username"].lower() == "default" else settings_dict["username"]
        settings_dict["username"] = username
        o_user = path.expanduser("~")
        if username != default_username:
            o_user = o_user.replace(default_username, username)
        exe_path = settings_dict["exe_path"]
        if exe_path.lower() == "default":
            exe_path = path.join(o_user, "AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
            settings_dict["exe_path"] = exe_path
        workspace_path = settings_dict["workspace_path"]
        if workspace_path.lower() == "default":
            workspace_path = path.join(o_user, "AppData\\Roaming\\Code\\User\\workspaceStorage")
            settings_dict["workspace_path"] = workspace_path

        return settings_dict

    def load_workspaces(self) -> list[Workspace]:
        """Scans the PC for VS Code workspaces"""
        folders = [f.path for f in scandir(self._settings["workspace_path"]) if f.is_dir()]
        workspaces = [Workspace.from_vscode_folder(f, self._settings["show_repos"], self._settings["show_glyphs"]) for f in folders]
        return sorted([w for w in workspaces if w is not None], key=lambda w: w.display_name)

    def clean_up_orphans(self) -> None:
        """Delete orphan workspaces"""
        for workspace in [w for w in self._workspaces if not w.exists]:
            shutil.rmtree(workspace.vsc_folder)
        self._workspaces = self.load_workspaces()
