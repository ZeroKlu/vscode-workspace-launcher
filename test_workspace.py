"""Test functions for the Workspace Class"""

from workspace import Workspace
import pytest

# Dev Note: Make sure all fixtures exist on the current workstation
@pytest.fixture
def defaults() -> str:
    return Workspace(
        "C:\\Users\\SMCLEAN\\AppData\\Roaming\\Code\\User\\workspaceStorage\\7b93dc74a785af6e142eb81ca9ace44f",
        "d:\\Training\\Bitbucket\\inversion-of-control",
        "inversion-of-control",
        "Bitbucket",
        "https://bitbucket.org/databankimx/inversion-of-control",
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

def test_init_defaults(defaults):
    """Test initializer with values but no factory functions"""
    w = Workspace(defaults.vsc_folder, defaults.workspace, defaults.name, defaults.parent, defaults.repo_uri, defaults.exists)
    assert w.vsc_folder == defaults.vsc_folder
    assert w.workspace == defaults.workspace
    assert w.name == defaults.name
    assert w.parent == defaults.parent
    assert w.repo_uri == defaults.repo_uri
    assert w.exists == defaults.exists

def test_from_vsc_folder(defaults):
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

def test_from_ws_folder(defaults):
    """Test Workspace factory using WS folder"""
    w = Workspace.from_workspace_folder(defaults.workspace, defaults.vsc_folder)
    assert w.vsc_folder == defaults.vsc_folder
    assert w.workspace == defaults.workspace
    assert w.name == defaults.name
    assert w.parent == defaults.parent
    assert w.repo_uri == defaults.repo_uri
    assert w.exists == defaults.exists

def test_from_ws_folder_no_vsc(defaults):
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

def test_display_name(defaults):
    """Test display name"""
    w = Workspace.from_workspace_folder(defaults.workspace)
    assert w.display_name == defaults.display_name
    assert w.display_name == f"{defaults.parent} > {defaults.name} | {defaults.repo_uri}"
