"""Test functions for the WorkspaceLocator Class"""

from workspace_locator import WorkspaceLocator
import pytest

# Run tests on a machine with workspaces

@pytest.fixture
def settings_path():
    # Dev note: Set to path on testing machine
    return r"D:\Training\GitHub\git-poc\settings.json"

def test_init_no_settings():
    """Test initializing without passing settings"""
    wl = WorkspaceLocator()
    assert wl._settings == WorkspaceLocator.default_settings

def test_init_with_settings():
    """Test initializing passing settings"""
    settings = WorkspaceLocator.default_settings
    wl = WorkspaceLocator(settings)
    assert wl._settings == WorkspaceLocator.default_settings

def test_init_with_settings_file(settings_path):
    """Test initializing passing settings JSON file"""
    wl = WorkspaceLocator(settings_file=settings_path)
    assert wl._settings == WorkspaceLocator.default_settings

def test_workspaces(settings_path):
    """Test obtaining workspaces"""
    wl = WorkspaceLocator(settings_file=settings_path)
    assert len(wl._workspaces) > 0
