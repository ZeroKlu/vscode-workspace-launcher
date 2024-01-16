import PySimpleGUI as sg
from os import path, scandir, getlogin
from pathlib import Path
import json
import urllib.parse as up
import subprocess
from dataclasses import dataclass
from sm_utils import file_path

@dataclass
class Workspace(object):
    """Defines a workspace"""
    name: str
    parent: str
    workspace: str
    @property
    def display_name(self) -> str:
        return f"{self.parent} > {self.name}"

class WorkspaceLocater(object):
    """VSCode Workspace Launcher"""
    def __init__(self, settings: dict[str, str]) -> None:
        """Initialize"""
        self.settings = settings

    def get_workspaces(self, filter: str|None="") -> list[Workspace]:
        """Get all workspaces used by VSCode"""
        workspaces = []
        folders = [f.path for f in scandir(self.settings["workspace_path"]) if f.is_dir()]
        for folder in folders:
            file = Path(path.join(folder, "workspace.json"))
            if not file.is_file():
                continue
            data = json.loads(file.read_text())
            if "folder" not in data:
                continue
            workspace = up.unquote(data["folder"][8:]).replace("/", "\\")
            if not path.isdir(workspace):
                continue
            parts = workspace.split("\\")
            if len(filter) > 0 and filter.lower() not in "".join([p for p in parts[-2:]]):
                continue
            workspaces.append(Workspace(
                workspace=workspace,
                parent=parts[-2],
                name=parts[-1]
            ))
        return sorted(workspaces, key=lambda x: x.display_name)

class WorkspaceLauncher(object):
    """UI for Workspace Launcher"""
    def __init__(self) -> None:
        """Initialize"""
        self.settings = self.get_settings()
        self.workspace_locater = WorkspaceLocater(self.settings)
    
    def get_settings(self):
        """Get the user settings from JSON file"""
        o_user = path.expanduser("~")
        settings = {
            "exe_path": path.join(o_user, "AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"),
            "workspace_path": path.join(o_user, "AppData\\Roaming\\Code\\User\\workspaceStorage"),
            "username": getlogin(),
            "x_location": 10,
            "y_location": 10
        }
        if path.isfile("settings.json"):
            file = Path(file_path("settings.json"))
            user_settings = json.loads(file.read_text())
            if user_settings["exe_path"].lower() != "default":
                settings["exe_path"] = user_settings["exe_path"]
            if user_settings["workspace_path"].lower() != "default":
                settings["workspace_path"] = user_settings["workspace_path"]
            if user_settings["username"].lower() != "default":
                u_user = f"C:\\Users\\{settings['username']}"
                settings["username"] = user_settings["username"]
                settings["exe_path"] = settings["exe_path"].replace(o_user, u_user)
                settings["workspace_path"] = settings["workspace_path"].replace(o_user, u_user)
            if user_settings["x_location"] != 0:
                settings["x_location"] = user_settings["x_location"]
            if user_settings["y_location"] != 0:
                settings["y_location"] = user_settings["y_location"]
        return settings

    def create_ui(self) -> None:
        """Launch the UI window and run"""
        text = ("Consolas", 10)
        filter = sg.InputText(enable_events=True, key="-FILTER-", font=text)
        workspaces = self.workspace_locater.get_workspaces()
        workspace_selector = sg.Combo(
            [w.display_name for w in workspaces],
            enable_events=True,
            key="-DROPDOWN-",
            font=text
        )
        window_layout = [[sg.Text("Filter:", font=text), filter],[workspace_selector]]
        window = sg.Window(
            title="Workspace Launcher for Visual Studio Code",
            icon="vscode.ico",
            layout=window_layout,
            margins=(0, 0)
        )
        x_size, y_size = window.get_screen_dimensions()
        x, y = self.settings["x_location"], self.settings["y_location"]
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
                workspaces = self.workspace_locater.get_workspaces(filter_text)
                window["-DROPDOWN-"].update(values=[w.display_name for w in workspaces])
            if event == "-DROPDOWN-":
                print(window.CurrentLocation())
                workspace = next(x.workspace for x in workspaces if x.display_name == values["-DROPDOWN-"])
                args = [self.settings["exe_path"], workspace]
        window.close()

def main() -> None:
    launcher = WorkspaceLauncher()
    launcher.create_ui()

if __name__ == "__main__":
    main()
