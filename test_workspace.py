"""Test functions for the Workspace Class"""

from workspace import Workspace
import pytest

# Dev Note: Make sure all fixtures exist on the current workstation
@pytest.fixture
def default_vsc_path() -> str:
    """Path to a VS Code pointer folder for a workspace on the current workstation"""
    return "C:\\Users\\SMCLEAN\\AppData\\Roaming\\Code\\User\\workspaceStorage\\7b93dc74a785af6e142eb81ca9ace44f"

@pytest.fixture
def default_ws_path() -> str:
    """Path to a workspace on the current workstation"""
    return "d:\\Training\\Bitbucket\\inversion-of-control"

@pytest.fixture
def default_ws_name() -> str:
    """Name of the default workspace on the current workstation"""
    return "inversion-of-control"

@pytest.fixture
def default_parent() -> str:
    """Parent folder of the default workspace on the current workstation"""
    return "Bitbucket"

@pytest.fixture
def default_repo_url() -> str:
    """URL of the default workspace repository"""
    return "https://bitbucket.org/databankimx/inversion-of-control"

@pytest.fixture
def defaults(default_vsc_path: str,
             default_ws_path: str,
             default_workspace_name: str,
             default_parent: str,
             default_repo_url: str) -> Workspace:
    """Default workspace for testing/comparison"""
    return Workspace(
        default_vsc_path,
        default_ws_path,
        default_workspace_name,
        default_parent,
        default_repo_url,
        True
    )

def test_init():
    """Test initializer without any values"""
    w = Workspace()
    assert w.vsc_folder is None
    assert w.workspace is None
    assert w.name is None
    assert w.parent is None
    assert w.repo_uri is None
    assert not w.exists

def test_init_defaults(defaults: Workspace):
    """Test initializer with values but no factory functions"""
    w = Workspace(defaults.vsc_folder, defaults.workspace, defaults.name, defaults.parent, defaults.repo_uri, defaults.exists)
    assert w.vsc_folder == defaults.vsc_folder
    assert w.workspace == defaults.workspace
    assert w.name == defaults.name
    assert w.parent == defaults.parent
    assert w.repo_uri == defaults.repo_uri
    assert w.exists == defaults.exists

def test_from_vsc_folder(defaults: Workspace):
    """Test Workspace factory using VSC folder"""
    w = Workspace.from_vscode_folder(defaults.vsc_folder)
    assert w.vsc_folder == defaults.vsc_folder
    assert w.workspace == defaults.workspace
    assert w.name == defaults.name
    assert w.parent == defaults.parent
    assert w.repo_uri == defaults.repo_uri
    assert w.exists == defaults.exists

def test_from_invalid_vsc_folder():
    """Test Workspace factory using invalid VSC folder"""
    w = Workspace.from_vscode_folder("C:\\Invalid\\Folder\\Path")
    assert w is None

def test_from_ws_folder(defaults: Workspace):
    """Test Workspace factory using WS folder"""
    w = Workspace.from_workspace_folder(defaults.workspace, defaults.vsc_folder)
    assert w.vsc_folder == defaults.vsc_folder
    assert w.workspace == defaults.workspace
    assert w.name == defaults.name
    assert w.parent == defaults.parent
    assert w.repo_uri == defaults.repo_uri
    assert w.exists == defaults.exists

def test_from_ws_folder_no_vsc(defaults: Workspace):
    """Test Workspace factory using WS folder (without VSC folder)"""
    w = Workspace.from_workspace_folder(defaults.workspace)
    assert w.vsc_folder == None
    assert w.workspace == defaults.workspace
    assert w.name == defaults.name
    assert w.parent == defaults.parent
    assert w.repo_uri == defaults.repo_uri
    assert w.exists == defaults.exists

def test_from_invalid_ws_folder():
    """Test Workspace factory using invalid WS folder"""
    w = Workspace.from_workspace_folder("C:\\Invalid\\Folder\\Path")
    assert w is None

def test_display_name(defaults: Workspace):
    """Test display name"""
    w = Workspace.from_workspace_folder(defaults.workspace)
    assert w.display_name == defaults.display_name
    assert w.display_name == f"{defaults.parent} > {defaults.name} | {defaults.repo_uri}"
