# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`joyboard` turns a gamepad (e.g. an Xbox controller) into a text-input device. It reads
joystick axes/buttons via `pygame` and emits real keystrokes via `keyboard`, acting like a
stenographic keyboard where a left-stick direction + face button selects a character.

## Commands

The project uses [Hatch](https://hatch.pypa.io) for environment and task management.

```console
hatch run test                 # run the test suite (pytest)
hatch run test tests/test_main.py::test_load_key_map   # run a single test
hatch run cov                  # run tests with coverage and print a report
hatch run types:check          # type-check src/joyboard and tests with mypy
python -m joyboard.main        # run the app (needs a connected controller)
```

`pytest tests` also works directly if pytest is installed in the active environment.
On Linux, running the app may require `sudo` because `keyboard` needs raw input access.

## Architecture

Everything lives in `src/joyboard/main.py`. There is no class structure — the program is a
set of pure-ish functions plus an `if __name__ == "__main__"` polling loop.

Key building blocks:

- **`load_key_map()`** parses the `DIRECTION_BUTTON_TABLE` ASCII table into a dict keyed by
  `(direction, button)` → character. The neutral-stick (`"X"`) entries map to special actions
  (`space`, `backspace`, `enter`, `tab`) and are added manually before the table is parsed.
  Editing the in-source table is how you change the character layout.
- **`get_direction(controller, pad)`** reads two axes (`L`=0/1, `R`=2/3, `T`=4/5), rounds each
  to `-1/0/1`, and maps the pair to an 8-way compass direction or `"X"` (neutral). This
  rounding is why off-center stick values still resolve to a direction.
- **`get_button(pressed_buttons)`** maps the first pressed entry in the raw button list to a
  label (`A`, `B`, ... `M`) by index. Index order is the pygame button order for the controller.

The main loop (60 fps via `pygame.time.Clock`): the **right stick** moves the cursor (arrow
keys); when the right stick is neutral, a face button + **left stick** direction looks up a
character in `LAYER_DIR_LETTER_MAP`. Neutral-left-stick keys are sent with `keyboard.send`
(named keys), others are typed with `keyboard.write`. Repeated identical keys sleep longer
(0.3s vs 0.1s) to debounce held inputs.

## Testing notes

`pygame` and `keyboard` are **not** installed in the test environment. `tests/test_main.py`
mocks both via `sys.modules[...] = MagicMock()` *before* importing `main`, and imports it as
`from src.joyboard import main`. Any new test module that imports `main` must do the same mock
setup first, or the import will fail. Tests cover the pure functions only — the main loop is
not exercised.

Version lives in `src/joyboard/__about__.py` (`__version__`), wired to Hatch's version source.
