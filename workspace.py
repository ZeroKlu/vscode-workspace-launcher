"""
The Workspace class represents a directory that has previously been opened in Visual Studio Code
Because Visual Studio Code does not track moved, renamed or deleted directories, each is checked to determine
  if it still exists
"""

from dataclasses import dataclass
import json
import urllib.parse as up
from os import path
from pathlib import Path

@dataclass
class Workspace:
    """Defines a workspace"""
    vsc_folder: str=None    # Folder where VS Code stores the workspace.json file describing the workspace
    workspace:  str=None    # Full path to the workspace folder
    name:       str=None    # Folder name containing the workspace files
    parent:     str=None    # Parent folder (containing the 'name' folder above)
    repo_uri:   str=None    # URI to the GIT repository for the workspace (if one exists)
    exists:     bool=False  # True if the workspace folder is defined and exists
    show_repo:  bool=True   # When True, show the repository in the display name
    show_glyph: bool=True   # When True, show the glyph in the display name

    @property
    def display_name(self) -> str:
        """Display name for the workspace when presented to the user"""
        name = f"{self.parent} > {self.name}"
        missing = "" if self.exists else " (missing)"
        bb_glyph = " " if self.show_glyph else ""
        gh_glyph = " " if self.show_glyph else ""
        repo = ""
        if self.repo_uri and self.show_repo:
            if "github.com" in self.repo_uri.lower():
                repo = f" | {bb_glyph}{self.repo_uri}"
            elif "bitbucket.org" in self.repo_uri.lower():
                repo = f" | {gh_glyph}{self.repo_uri}"
            else:
                repo = f" | {self.repo_uri}"
        return f"{name}{repo}{missing}"

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
        ws_path = Path(ws.workspace)
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
        git_folder = path.join(ws.workspace, ".git")
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
