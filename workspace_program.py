from sm_utils import file_path
from sys import argv
from workspace_launcher import WorkspaceLauncher

def main() -> None:
    settings_path = file_path(argv[1] if len(argv) > 1 else "settings.json")
    launcher = WorkspaceLauncher(settings_path)
    launcher.create_ui()

if __name__ == "__main__":
    main()