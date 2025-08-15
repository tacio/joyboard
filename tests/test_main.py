import sys
import pytest
from unittest.mock import MagicMock

# Mock pygame and keyboard before importing main, since they are not installed in the test env
sys.modules["pygame"] = MagicMock()
sys.modules["keyboard"] = MagicMock()

from src.joyboard import main

def test_load_key_map():
    key_map = main.load_key_map()
    assert key_map[("X", "A")] == "space"
    assert key_map[("N", "A")] == "a"
    assert key_map[("SW", "Y")] == "!"

@pytest.mark.parametrize(
    "x_axis, y_axis, expected_direction",
    [
        (0, -1, "N"),
        (1, -1, "NE"),
        (1, 0, "E"),
        (1, 1, "SE"),
        (0, 1, "S"),
        (-1, 1, "SW"),
        (-1, 0, "W"),
        (-1, -1, "NW"),
        (0, 0, "X"),
        (0.1, -0.9, "N"),
        (0.8, 0.7, "SE"),
    ],
)
def test_get_direction(x_axis, y_axis, expected_direction):
    mock_controller = MagicMock()

    def get_axis_side_effect(axis):
        if axis == 0:
            return x_axis
        if axis == 1:
            return y_axis
        return 0

    mock_controller.get_axis.side_effect = get_axis_side_effect
    assert main.get_direction(mock_controller, "L") == expected_direction

@pytest.mark.parametrize(
    "button_index, expected_button",
    [
        (0, "A"),
        (1, "B"),
        (2, "X"),
        (3, "Y"),
        (4, "LB"),
        (5, "RB"),
        (6, "<"),
        (7, ">"),
        (8, "LA"),
        (9, "RA"),
        (10, "M"),
    ],
)
def test_get_button(button_index, expected_button):
    pressed_buttons = [False] * 11
    pressed_buttons[button_index] = True
    assert main.get_button(pressed_buttons) == expected_button
