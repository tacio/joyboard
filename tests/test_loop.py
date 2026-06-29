"""Timing tests for the main polling loop, driven by the scripted-input harness.

Each test scripts human input on a virtual timeline (explicit press/release
timestamps) and asserts the exact sequence and virtual timing of the keystrokes
``run_loop`` emits, including the 0.1s/0.3s debounce behavior.
"""

import pytest

from tests.harness import (
    Hold,
    KeyboardRecorder,
    ScriptedController,
    VirtualClock,
    main,
    run_scripted,
)


def actions(events):
    """(action, key) pairs, dropping timestamps."""
    return [(action, key) for _, action, key in events]


def times(events):
    return [t for t, _, _ in events]


def gaps(events):
    ts = times(events)
    return [b - a for a, b in zip(ts, ts[1:])]


def test_single_tap_emits_one_keystroke():
    # Press left-stick N + button A, release before the first debounce window.
    events = run_scripted([Hold(0.0, 0.05, left="N", button="A")])
    assert events == [(pytest.approx(0.0), "write", "a")]


def test_holding_repeats_with_debounce_cadence():
    # A held combo repeats: 0.1s after the first emit, then every 0.3s.
    events = run_scripted([Hold(0.0, 0.8, left="N", button="A")])
    assert actions(events) == [("write", "a")] * 4
    assert times(events) == pytest.approx([0.0, 0.1, 0.4, 0.7])
    assert gaps(events) == pytest.approx([0.1, 0.3, 0.3])


def test_prev_key_persists_across_idle_gap():
    # Tap A, then (after an idle gap) hold A again. Because prev_key persists,
    # the repeats inside the second hold are spaced by the 0.3s same-key debounce.
    events = run_scripted(
        [
            Hold(0.0, 0.05, left="N", button="A"),
            Hold(0.2, 0.6, left="N", button="A"),
        ]
    )
    assert actions(events) == [("write", "a")] * 3
    assert times(events) == pytest.approx([0.0, 0.2, 0.5])
    # The repeat within the second hold used the 0.3s same-key debounce.
    assert times(events)[2] - times(events)[1] == pytest.approx(0.3)


def test_switching_to_a_different_key_uses_short_debounce():
    # Tap A, then hold E: the first E repeat comes after the 0.1s new-key
    # debounce (not 0.3s), since the key differs from the previous one.
    events = run_scripted(
        [
            Hold(0.0, 0.05, left="N", button="A"),
            Hold(0.2, 0.6, left="E", button="A"),
        ]
    )
    assert actions(events) == [("write", "a"), ("write", "e"), ("write", "e")]
    assert times(events)[2] - times(events)[1] == pytest.approx(0.1)


@pytest.mark.parametrize(
    "right, arrow",
    [("N", "up"), ("E", "right"), ("S", "down"), ("W", "left")],
)
def test_right_stick_taps_send_arrow_keys(right, arrow):
    events = run_scripted([Hold(0.0, 0.05, right=right)])
    assert events == [(pytest.approx(0.0), "send", arrow)]


def test_right_stick_hold_repeats_arrows_at_tenth_second():
    # Cursor movement always paces at 0.1s and never touches the repeat debounce.
    events = run_scripted([Hold(0.0, 0.35, right="N")])
    assert actions(events) == [("send", "up")] * 4
    assert gaps(events) == pytest.approx([0.1, 0.1, 0.1])


def test_right_stick_takes_priority_over_buttons():
    # With both sticks/buttons active, the right stick wins and no char is typed.
    events = run_scripted([Hold(0.0, 0.05, right="N", button="A")])
    assert events == [(pytest.approx(0.0), "send", "up")]


def test_diagonal_right_stick_emits_nothing_but_blocks_buttons():
    # A diagonal right stick has no arrow mapping: it emits nothing yet still
    # consumes the frame, so the button branch never runs.
    events = run_scripted([Hold(0.0, 0.2, right="NE", button="A")])
    assert events == []


@pytest.mark.parametrize(
    "button, key",
    [("A", "space"), ("B", "backspace"), ("X", "enter"), ("Y", "tab")],
)
def test_neutral_stick_specials_use_send(button, key):
    # Neutral left stick + face button maps to a named special key sent (not
    # written) via keyboard.send.
    events = run_scripted([Hold(0.0, 0.05, button=button)])
    assert events == [(pytest.approx(0.0), "send", key)]


def test_direction_plus_button_character_uses_write():
    events = run_scripted([Hold(0.0, 0.05, left="SW", button="Y")])
    assert events == [(pytest.approx(0.0), "write", "!")]


def test_no_input_emits_nothing():
    assert run_scripted([]) == []
    assert run_scripted([Hold(0.0, 0.1)]) == []


class _QuitEvent:
    def __init__(self):
        self.type = main.pygame.QUIT


def test_quit_event_stops_loop_after_finishing_the_frame():
    # A QUIT event arriving on the first frame stops the loop -- but that frame
    # still completes (emits once) before the `while running` check exits. With
    # no other stop condition, this is what keeps the loop finite.
    clock = VirtualClock()
    controller = ScriptedController(clock, [Hold(0.0, 1.0, left="N", button="A")])
    recorder = KeyboardRecorder(clock)

    main.run_loop(
        controller,
        main.load_key_map(),
        output=recorder,
        sleep=clock.sleep,
        poll_events=lambda: [_QuitEvent()],
    )

    assert actions(recorder.events) == [("write", "a")]
