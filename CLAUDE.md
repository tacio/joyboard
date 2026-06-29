# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`joyboard` turns a gamepad (e.g. an Xbox controller) into a text-input device. It reads
joystick axes/buttons via `pygame` and emits real keystrokes via `keyboard`, acting like a
stenographic keyboard where a left-stick direction + face button selects a character.

## Commands

The project uses [uv](https://docs.astral.sh/uv/) for environment, dependency, and task
management. Dev tools (pytest, coverage, ruff, ty) live in the `dev` dependency group and are
installed by `uv sync`.

```console
uv sync                        # create/refresh the .venv from pyproject + uv.lock
uv run pytest tests            # run the test suite
uv run pytest tests/test_main.py::test_load_key_map   # run a single test
uv run coverage run -m pytest tests && uv run coverage report   # tests with coverage
uv run ruff format             # format the code
uv run ruff format --check     # check formatting without writing
uv run ty check                # type-check (Astral's ty)
uv build                       # build sdist + wheel (uv_build backend)
uv run python -m joyboard.main # run the app (needs a connected controller)
```

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

- **`process_frame(controller, key_map, output)`** runs one polling frame and returns
  `("cursor", None)`, `("key", char)`, or `("idle", None)`. The **right stick** moves the
  cursor (arrow keys); when it's neutral, a face button + **left stick** direction looks up a
  character in `key_map`. Neutral-left-stick keys are sent with `output.send` (named keys),
  others typed with `output.write`. `output` is anything with `.send`/`.write` — the `keyboard`
  module in production.
- **`run_loop(controller, key_map, output=keyboard, *, sleep, tick, poll_events, should_continue)`**
  is the polling loop, with all side-effecting collaborators injected (production defaults make
  the real path unchanged). It owns `prev_key` and the debounce: repeated identical keys sleep
  longer (0.3s vs 0.1s); cursor frames always sleep 0.1s and never touch `prev_key`. QUIT (from
  `poll_events`) stops it. The `__main__` block is thin wiring: build the key map and call
  `run_loop(..., tick=lambda: clock.tick(60))` (60 fps).

## Testing notes

`pygame` and `keyboard` *are* installed in the synced environment, but the tests mock both via
`sys.modules[...] = MagicMock()` *before* `from joyboard import main`, so the module-level
imports resolve without a real controller/display. `tests/test_main.py` does this inline; any
other test module that imports `main` must do the same — or just import `tests/harness.py`,
which centralizes the mock guard.

`tests/test_main.py` covers the pure functions (`load_key_map`, `get_direction`, `get_button`).
`tests/test_loop.py` exercises the full `run_loop`/`process_frame` path using the harness in
`tests/harness.py`: a `VirtualClock` (sleep advances virtual time, no real delay), a
`ScriptedController` driven by a `Hold(t0, t1, left=, right=, button=)` timeline with explicit
press/release timestamps, and a `KeyboardRecorder` capturing `(time, "send"/"write", key)`.
Author a test with `run_scripted([...holds])` and assert the returned timed keystroke list —
this is how debounce/repeat timing is verified deterministically.

The package version is static in `pyproject.toml` (`project.version`).
