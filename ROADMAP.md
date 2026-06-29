# Roadmap

This document captures where `joyboard` is headed. Today (v0.0.1, beta) you can type lowercase
letters and some punctuation, delete (backspace), insert newline/tab, and move the cursor with the
right stick — see the [README](README.md#controls) for the full layout.

The work below is grouped into themes rather than fixed releases. Ordering within each section
roughly reflects priority, but nothing here is a commitment — it's a direction, and it will change.
Contributions and suggestions are welcome.

## Input & Character Set

- [ ] **Uppercase letters** via a shift/modifier layer (today the layout is lowercase only).
- [ ] **Digits 0-9 and extended punctuation** so joyboard can type more than prose.
- [ ] **More character layers** using inputs that are already detected but unused: the shoulder,
      stick-click, and menu buttons (`LB, RB, <, >, LA, RA, M`) and the trigger pad.
- [ ] **Stenographic chording** — selecting whole words with simultaneous presses, the long-term
      vision described in the README.

## Configuration

- [ ] **External layout files** so users can remap characters without editing the source table.
- [ ] **Tunable timings** — make the debounce delays (currently fixed at 0.1s / 0.3s) and the
      polling rate (currently 60 FPS) configurable.
- [ ] **Command-line options** for layout selection, controller index, and timing tweaks.

## Platform & Robustness

- [ ] **Graceful failure handling** for controller disconnects and input/init errors instead of
      crashing.
- [ ] **Multi-controller and hot-plug support** (currently only the first controller is used).
- [ ] **Reduce the Linux `sudo` requirement** where possible, and document the constraint clearly
      where it can't be avoided.

## Tooling & CI

- [ ] **Continuous integration** — a GitHub Actions workflow running the test suite, format check,
      and type check on every push and pull request.
- [ ] **Coverage in CI**, and closing current gaps (the trigger pad and disconnect paths are
      untested).
- [ ] **Automated releases** to PyPI on tagged versions.

## Documentation

- [ ] **Keep the layout in sync** — generate the README character table from the in-source table
      (or vice versa) so they can't drift apart.
- [ ] **A usage screencast / GIF** showing real typing.
- [ ] **A layout-design rationale** explaining how characters are placed.

## Ecosystem

- [ ] **A joyboard website** as the project's home: docs, downloads, and an interactive demo.
- [ ] **A typing-training tool** (browser-based) to help newcomers learn the layout and build
      speed — think "typing tutor" for the gamepad.
- [ ] **Sharing of character maps** — a place to publish, browse, and import community layouts
      (different languages, keyboard styles, accessibility-focused maps).
- [ ] **Testimonials and showcases** from people using joyboard, including accessibility stories.
- [ ] **Community spaces** (discussion, issues, contribution guide) to grow participation.
