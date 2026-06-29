"""Test harness for simulating human controller input with precise timing.

A test author scripts a timeline of :class:`Hold` intervals (each with explicit
press/release timestamps) and replays them through the real ``main.run_loop`` via
:func:`run_scripted`, which returns the exact sequence *and* virtual timing of the
emitted keystrokes. No real pygame/keyboard/sleep is used -- a ``VirtualClock``
stands in for wall-clock time so timing is deterministic.
"""

import sys
from unittest.mock import MagicMock

# pygame and keyboard touch real hardware/displays; mock them before importing
# main so its module-level imports resolve in a headless test environment.
sys.modules.setdefault("pygame", MagicMock())
sys.modules.setdefault("keyboard", MagicMock())

from joyboard import main

# Inverse of get_direction's value_compass_map: compass label -> (x, y) axes.
COMPASS_TO_XY = {
    "N": (0, -1),
    "NE": (1, -1),
    "E": (1, 0),
    "SE": (1, 1),
    "S": (0, 1),
    "SW": (-1, 1),
    "W": (-1, 0),
    "NW": (-1, -1),
    "X": (0, 0),
}

# Inverse of get_button's index table: button label -> button index.
BUTTON_TO_INDEX = {
    "A": 0,
    "B": 1,
    "X": 2,
    "Y": 3,
    "LB": 4,
    "RB": 5,
    "<": 6,
    ">": 7,
    "LA": 8,
    "RA": 9,
    "M": 10,
}


class VirtualClock:
    """A fake clock whose time only advances when ``sleep`` is called."""

    def __init__(self, start=0.0):
        self.now = start

    def sleep(self, seconds):
        self.now += seconds


class Hold:
    """A single human input held over the half-open interval ``[t0, t1)``.

    ``left``/``right`` are compass strings ("N".."NW") or "X"/None for a neutral
    stick; ``button`` is a face/label string ("A".."M") or None. Half-open
    intervals make release timing unambiguous: at exactly ``t1`` the input is
    already released.
    """

    def __init__(self, t0, t1, *, left=None, right=None, button=None):
        self.t0 = t0
        self.t1 = t1
        self.left = left
        self.right = right
        self.button = button


class ScriptedController:
    """A pygame-controller stand-in that reports the held input at the current
    virtual time, computed from a list of :class:`Hold` intervals."""

    def __init__(self, clock, holds, numbuttons=11):
        self.clock = clock
        self.holds = list(holds)
        self.numbuttons = numbuttons

    def _active_hold(self):
        now = self.clock.now
        for hold in self.holds:
            if hold.t0 <= now < hold.t1:
                return hold
        return None

    def next_start(self):
        """The earliest press time strictly after now, or None."""
        now = self.clock.now
        starts = [hold.t0 for hold in self.holds if hold.t0 > now]
        return min(starts) if starts else None

    def get_numbuttons(self):
        return self.numbuttons

    def get_axis(self, axis):
        hold = self._active_hold()
        if hold is None:
            return 0.0
        if axis in (0, 1):
            x, y = COMPASS_TO_XY.get(hold.left or "X", (0, 0))
        elif axis in (2, 3):
            x, y = COMPASS_TO_XY.get(hold.right or "X", (0, 0))
        else:
            return 0.0
        return float(x if axis % 2 == 0 else y)

    def get_button(self, index):
        hold = self._active_hold()
        if hold is None or hold.button is None:
            return False
        return BUTTON_TO_INDEX.get(hold.button) == index


class KeyboardRecorder:
    """Output sink capturing ``(virtual_time, "send"|"write", key)`` per emit."""

    def __init__(self, clock):
        self.clock = clock
        self.events = []

    def send(self, key):
        self.events.append((self.clock.now, "send", key))

    def write(self, key):
        self.events.append((self.clock.now, "write", key))


def run_scripted(holds, *, key_map=None, numbuttons=11, max_time=None):
    """Replay scripted holds through the real ``main.run_loop`` and return the
    list of emitted ``(virtual_time, "send"|"write", key)`` keystroke events."""
    clock = VirtualClock()
    if key_map is None:
        key_map = main.load_key_map()
    controller = ScriptedController(clock, holds, numbuttons)
    recorder = KeyboardRecorder(clock)

    holds_end = max((hold.t1 for hold in holds), default=0.0)
    end = holds_end if max_time is None else min(holds_end, max_time)

    # Idle frames (nothing held) don't sleep, so virtual time would stall on dead
    # gaps between holds. Detect a stalled frame (time unchanged since the prior
    # frame) and fast-forward to the next scripted press, or to the end when
    # nothing remains -- this keeps the loop progressing and guarantees it stops.
    last = {"now": clock.now}

    def tick():
        if clock.now == last["now"]:
            nxt = controller.next_start()
            clock.now = nxt if nxt is not None else end
        last["now"] = clock.now

    def should_continue():
        return clock.now < end

    main.run_loop(
        controller,
        key_map,
        output=recorder,
        sleep=clock.sleep,
        tick=tick,
        poll_events=lambda: [],
        should_continue=should_continue,
    )
    return recorder.events
