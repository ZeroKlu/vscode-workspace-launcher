import PySimpleGUI as sg
from os import path, scandir
from pathlib import Path
import json
import urllib.parse as up
import subprocess

def create_window() -> None:
    """Create a new window in PySimpleGUIQt"""
    code_exe = path.join(path.expanduser("~"), "AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
    filter = sg.InputText(enable_events=True, key="-FILTER-")
    workspaces = get_workspaces()
    workspace_selector = sg.Combo(list(workspaces.keys()), enable_events=True, key="-DROPDOWN-")
    window_layout = [[sg.Text("Filter:"), filter],[workspace_selector]]

    window = sg.Window(
        title="VSCode Workspace Launcher",
        icon="vscode.ico",
        layout=window_layout,
        margins=(10, 10)
    )
    filter_text = ""
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == "-FILTER-" and values["-FILTER-"] != filter_text:
            filter_text =  values["-FILTER-"]
            workspaces = get_workspaces(filter_text)
            window["-DROPDOWN-"].update(values=list(workspaces.keys()))
        if event == "-DROPDOWN-":
            args = [code_exe, workspaces[values["-DROPDOWN-"]]]
            subprocess.run(args)

    window.close()

def get_workspaces(filter: str|None="") -> dict[str, str]:
    """Get the list of workspaces from the local PC"""
    ws_dir = path.join(path.expanduser("~"), "AppData\\Roaming\\Code\\User\\workspaceStorage")
    workspaces = {}
    folders = [f.path for f in scandir(ws_dir) if f.is_dir()]
    for folder in folders:
        file = Path(path.join(folder, "workspace.json"))
        if not file.is_file(): continue
        data = json.loads(file.read_text())
        if "folder" not in data: continue
        workspace = up.unquote(data["folder"][8:]).replace("/", "\\")
        if workspace[1] != ":" or not path.isdir(workspace): continue
        if len(filter) > 0 and filter.lower() not in workspace.lower(): continue
        parts = workspace.split("\\")
        workspaces[f"{parts[-2]} > {parts[-1]}"] = workspace
    return dict(sorted(workspaces.items()))

def main() -> None:
    create_window()

if __name__ == "__main__":
    main()
