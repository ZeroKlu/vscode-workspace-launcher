"""
This WorkspaceLocator class obtains a list of all VS Code workspaces on the workstation.
"""

from workspace import Workspace
from workspace_settings import WorkspaceSettings
from os import scandir
import shutil

class WorkspaceLocator:
    """Locator for VS Code Workspaces on PC"""

    def __init__(self, settings: WorkspaceSettings=None, settings_json: dict[str, str]=None, settings_file: str=None) -> None:
        """Initialize"""
        # Get settings
        self._settings = settings
        if not self._settings:
            self._settings = WorkspaceSettings.from_dict(settings) if settings else WorkspaceSettings.from_file(settings_file)
        self._workspaces = self.load_workspaces()
        if self._settings.clean_up_orphans:
            self.clean_up_orphans()
    
    @property
    def workspaces(self):
        return self._workspaces if not self._settings.hide_missing else [w for w in self._workspaces if w.exists]

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
