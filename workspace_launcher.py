"""
The WorkspaceLauncher class provides a UI for interacting with the list of Workspace objects 
  discovered by WorkspaceLocator.
"""

from workspace import Workspace
from workspace_settings import WorkspaceSettings
from workspace_locator import WorkspaceLocator
import PySimpleGUI as sg
import subprocess
import sys
from os import path
import webbrowser

# TODO: Add support for launching Repo URL if available

class WorkspaceLauncher:
    """UI for interacting with the list of workspaces"""

    def __init__(self, settings_file: str=None) -> None:
        self._settings = WorkspaceSettings.from_file(settings_file) if settings_file else WorkspaceSettings()
        self._workspace_locator = WorkspaceLocator(self._settings)

    def create_ui(self) -> None:
        text = (self._settings.font, self._settings.font_size)
        filter = sg.InputText(enable_events=True, key="-FILTER-", font=text)
        url_toggle = sg.Checkbox("Launch repo URL", default=False)
        workspaces = self._workspace_locator.workspaces
        workspace_selector = sg.Combo(
            [w.display_name for w in workspaces],
            enable_events=True,
            key="-DROPDOWN-",
            font=text
        )
        window_layout = [[sg.Text("Filter:", font=text), filter, url_toggle],[workspace_selector]]
        window = sg.Window(
            title="Workspace Launcher for Visual Studio Code",
            icon=self.resource_path("rocket.ico"),
            layout=window_layout,
            margins=(0, 0)
        )
        x_size, y_size = window.get_screen_dimensions()
        x, y = self._settings.x_location, self._settings.y_location
        x_pos = x if x > 0 else x_size + x
        y_pos = y if y > 0 else y_size + y
        window.Location = (x_pos, y_pos)
        filter_text = ""
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            if event == "-FILTER-" and values["-FILTER-"] != filter_text:
                filter_text =  values["-FILTER-"]
                workspaces = [w for w in self._workspace_locator.workspaces if filter_text in w.display_name]
                window["-DROPDOWN-"].update(values=[w.display_name for w in workspaces])
            if event == "-DROPDOWN-":
                ws = next(w for w in workspaces if w.display_name == values["-DROPDOWN-"])
                args = [self._settings.exe_path, ws.workspace]
                subprocess.call(args)
                if url_toggle.get() and ws.repo_uri:
                    webbrowser.open(ws.repo_uri)

        window.close()

    def resource_path(self, file_name: str) -> str:
        """Fix for issue with PyInstaller not respecting the icon"""
        base_path = getattr(sys, "_MEIPASS", path.dirname(path.abspath(__file__)))
        return path.join(base_path, file_name)
