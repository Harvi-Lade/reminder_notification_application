import pytest
from unittest.mock import patch
from main import main
from views.cli_menu import ShowMenu

@patch.object(ShowMenu, '__init__', lambda self: None)  # Mock the constructor to avoid any setup delays
@patch.object(ShowMenu, 'menu', return_value=None)  # Mock the menu method to prevent hanging
def test_main(mock_menu):
    main()
    mock_menu.assert_called_once()
