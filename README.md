# joyboard

[![PyPI - Version](https://img.shields.io/pypi/v/joyboard.svg)](https://pypi.org/project/joyboard)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/joyboard.svg)](https://pypi.org/project/joyboard)

-----

**Table of Contents**

- [Purpose](#purpose)
- [Installation](#installation)
- [Usage](#usage)
- [Controls](#controls)
- [License](#license)

## Purpose

`joyboard` is a python program that sends keyboard signals from a joypad (like a xbox controller)
so that you write from the joypad.

Currently, lower case letters and some punctuaction is all you can write.
Also, you can delete characters (backspace), insert newline (enter), insert tab, and move the cursor.
But, there many buttons and combos yet to create.

Conceptually, it should act kind of like a stenographic keyboard, writing full words with simultaneous key presses.


## Installation

```console
pip install joyboard
```

This will also install the necessary dependencies: `pygame` for controller input and `keyboard` for sending keystrokes.

## Usage

To run joyboard, execute the main script:

```console
python -m joyboard.main
```

> [!NOTE]
> On Linux, you might need to run it with `sudo` for it to work.

## Controls

The controller is used as follows:

- **Left Stick**: Selects a character set.
- **Face Buttons (A, B, X, Y)**: Selects a character from the set.
- **Right Stick**: Moves the cursor (up, down, left, right).

### Character Mapping

The table below shows the character mapped to each combination of the left stick direction and face button.

| Direction | A | B | X | Y |
|---|---|---|---|---|
| **N** (Up) | a | b | c | h |
| **NE** | ã | g | f | v |
| **E** (Right) | e | d | s | m |
| **SE** | y | q | j | w |
| **S** (Down) | i | p | z | n |
| **SW** | õ | . | , | ! |
| **W** (Left) | o | t | r | l |
| **NW** | u | k | x | ? |

### Special Characters

Special actions are mapped to face buttons when the left stick is in the neutral position.

| Button | Action |
|---|---|
| **A** | space |
| **B** | backspace |
| **X** | enter |
| **Y** | tab |


## License

`joyboard` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
