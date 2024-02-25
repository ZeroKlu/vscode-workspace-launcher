"""
The WorkspaceLauncher class provides a UI for interacting with the list of Workspace objects 
  discovered by WorkspaceLocator.
"""

#region Imports
from workspace import Workspace
from workspace_settings import WorkspaceSettings
from workspace_locator import WorkspaceLocator
import PySimpleGUI as sg
import subprocess
import sys
from os import path
import webbrowser
#endregion

class WorkspaceLauncher:
    """UI for interacting with the list of workspaces"""

    #region Constructor
    def __init__(self, settings_file: str=None) -> None:
        """Initialize"""
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
        self.window.Location = self._get_ui_position(self.window)
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
            self._launch_workspace(selected_workspace)
        # Launch the repository (if one exists) in the browser
        if self.url_toggle.get():
            self._launch_repository(selected_workspace)
    
    def on_vsc_toggle_change(self, selected_workspace: Workspace) -> None:
        """Launch the workspace in VS code if the user checks the box while a workspace is selected"""
        if not self.vsc_toggle.get() or not selected_workspace:
            return
        self._launch_workspace(selected_workspace)
    
    def on_url_toggle_change(self, selected_workspace: Workspace) -> None:
        """Launch the repository in the default browser if the user checks the box while a workspace is selected"""
        if not self.url_toggle.get() or not selected_workspace:
            return
        self._launch_repository(selected_workspace)
    #endregion

    #region Helper functions
    def _get_ui_position(self, window: sg.Window) -> tuple[int, int]:
        # Set the position for the UI window
        x_size, y_size = window.get_screen_dimensions()
        x, y = self._settings.x_location, self._settings.y_location
        x_pos = x if x > 0 else x_size + x
        y_pos = y if y > 0 else y_size + y
        return (x_pos, y_pos)
    
    def _launch_workspace(self, selected_workspace: Workspace):
        """Open the selected workspace an instance of Visual Studio code"""
        # Launch a subprocess to open the workspace in VS Code
        args = [self._settings.exe_path, selected_workspace.workspace]
        subprocess.call(args)

    def _launch_repository(self, selected_workspace: Workspace):
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
