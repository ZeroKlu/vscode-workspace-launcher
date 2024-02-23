"""
The WorkspaceSettings class is just a model for the settings dictionary passed around in an earlier iteration
"""

from dataclasses import dataclass
from sm_utils import file_path
from os import path, getlogin
from pathlib import Path
import json

@dataclass
class WorkspaceSettings:
    """Settings model"""
    exe_path: str="default"
    workspace_path: str="default"
    username: str="default"
    hide_missing: bool=True
    clean_up_orphans: bool=False
    show_repos: bool=True
    font: str="Consolas"
    font_size: int=10
    show_glyphs: bool=False
    x_location: int=10
    y_location: int=-160

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
        settings.username = WorkspaceSettings.get_user(settings.username)
        settings.exe_path, settings.workspace_path = WorkspaceSettings.get_user_paths(
            settings.username, settings.exe_path, settings.workspace_path)
        return settings

    @classmethod
    def get_user(cls, username: str) -> str:
        """Get the username for the settings"""
        return getlogin() if username.lower() == "default" else username

    @classmethod
    def get_user_paths(cls, username: str, exe_path: str, ws_path: str) -> tuple[str, str]:
        """Get the AppData path for the settings user"""
        user_path = path.expanduser(f"~{username}")
        if exe_path.lower() == "default":
            exe_path = path.join(user_path, "AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
        if ws_path.lower() == "default":
            ws_path = path.join(user_path, "AppData\\Roaming\\Code\\User\\workspaceStorage")
        return (exe_path, ws_path)
