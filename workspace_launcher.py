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
        # Create the textbox for the user to type a filter for the workspaces
        filter = sg.InputText(enable_events=True, key="-FILTER-", font=text)
        # Create the checkbox to indicate whether to launch the workspace in VS Code
        vsc_toggle = sg.Checkbox("Open in VS Code", default=True, enable_events=True, key="-VSC-")
        # Create the checkbox to indicate whether to launch the repo URL in a browser
        url_toggle = sg.Checkbox("Launch repo URL", default=False, enable_events=True, key="-URL-")
        # Get the list of workspaces to display in the drop-down list
        workspaces = self._workspace_locator.workspaces
        # Create and populate the workspace select list
        workspace_selector = sg.Combo(
            [w.display_name for w in workspaces],
            enable_events=True,
            key="-DROPDOWN-",
            font=text
        )
        # Lay out the window
        window_layout = [[sg.Text("Filter:", font=text), filter, vsc_toggle, url_toggle],[workspace_selector]]
        # Create the UI window
        window = sg.Window(
            title="Workspace Launcher for Visual Studio Code",
            icon=self.resource_path("rocket.ico"),
            layout=window_layout,
            margins=(0, 0)
        )
        # Position the window
        x_size, y_size = window.get_screen_dimensions()
        x, y = self._settings.x_location, self._settings.y_location
        x_pos = x if x > 0 else x_size + x
        y_pos = y if y > 0 else y_size + y
        window.Location = (x_pos, y_pos)
        # Set the initial filter text blank
        filter_text = ""
        # Run the UI until the user closes the window
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                # Halt processing if the user closes the UI
                break

            if event == "-FILTER-" and values["-FILTER-"] != filter_text:
                # Reload the filtered workspace list if the user changes the filter text
                filter_text =  values["-FILTER-"]
                workspaces = [w for w in self._workspace_locator.workspaces if filter_text in w.display_name]
                window["-DROPDOWN-"].update(values=[w.display_name for w in workspaces])

            if event == "-DROPDOWN-":
                # When the user selects a workspace from the dropdown list, perform the action(s) identified
                #   by the checkboxes

                # Get the workspace Identified by the display name
                ws = next(w for w in workspaces if w.display_name == values["-DROPDOWN-"])
                # Launch the workspace in VS Code
                if vsc_toggle.get():
                    self.launch_workspace(workspaces, values["-DROPDOWN-"])
                # Launch the repository (if one exists) in the browser
                if url_toggle.get():
                    self.launch_repository(workspaces, values["-DROPDOWN-"])

            if event == "-VSC-" and vsc_toggle.get() and values["-DROPDOWN-"]:
                # When the user checks the workspace checkbox (with a workspace selected),
                #   launch the workspace in VS Code
                self.launch_workspace(workspaces, values["-DROPDOWN-"])

            if event == "-URL-" and url_toggle.get() and values["-DROPDOWN-"]:
                # When the user checks the URL checkbox (with a workspace selected),
                #   launch the repository (if it exists) in the browser
                self.launch_repository(workspaces, values["-DROPDOWN-"])

        window.close()

    def launch_workspace(self, workspaces: list[Workspace], selected: str):
        # Get the workspace Identified by the display name
        ws = next(w for w in workspaces if w.display_name == selected)
        args = [self._settings.exe_path, ws.workspace]
        subprocess.call(args)

    def launch_repository(self, workspaces: list[Workspace], selected: str):
        # Get the workspace Identified by the display name
        ws = next(w for w in workspaces if w.display_name == selected)
        if ws.repo_uri:
            webbrowser.open(ws.repo_uri)
        

    def resource_path(self, file_name: str) -> str:
        """Fix for issue with PyInstaller not respecting the icon"""
        base_path = getattr(sys, "_MEIPASS", path.dirname(path.abspath(__file__)))
        return path.join(base_path, file_name)
