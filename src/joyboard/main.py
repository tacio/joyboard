from time import sleep

import keyboard
import pygame


def load_key_map():
    DIRECTION_BUTTON_TABLE = """
   A B X Y
N  a b c h
NE ã g f v
E  e d s m
SE y q j w
S  i p z n
SW õ . , ! 
W  o t r l
NW u k x ?
    """

    layer_dir_letter_map = {
        ("X", "A"): "space",
        ("X", "B"): "backspace",
        ("X", "X"): "enter",
        ("X", "Y"): "tab",
    }

    for row in DIRECTION_BUTTON_TABLE.split("\n"):
        if (not row) or row[0] == " ":
            continue

        direction, A, B, X, Y = row.split()
        layer_dir_letter_map[(direction, "A")] = A
        layer_dir_letter_map[(direction, "B")] = B
        layer_dir_letter_map[(direction, "X")] = X
        layer_dir_letter_map[(direction, "Y")] = Y

    return layer_dir_letter_map


def get_clean_input(controller, axis):
    return round(controller.get_axis(axis))


def get_direction(controller, pad="L"):
    pad_axis_map = {"L": 0, "R": 2, "T": 4}

    value_compass_map = {
        (0, -1): "N",
        (1, -1): "NE",
        (1, 0): "E",
        (1, 1): "SE",
        (0, 1): "S",
        (-1, 1): "SW",
        (-1, 0): "W",
        (-1, -1): "NW",
        (0, 0): "X",
    }

    axis = pad_axis_map.get(pad)
    if axis is None:
        raise ValueError(f"pad {pad} not recognized, try L, R or M")

    direction = (
        get_clean_input(controller, axis),
        get_clean_input(controller, axis + 1),
    )
    return value_compass_map.get(direction)


def get_button(pressed_buttons):
    match pressed_buttons:
        case _ as b if b[0]:
            return "A"
        case _ as b if b[1]:
            return "B"
        case _ as b if b[2]:
            return "X"
        case _ as b if b[3]:
            return "Y"
        case _ as b if b[4]:
            return "LB"
        case _ as b if b[5]:
            return "RB"
        case _ as b if b[6]:
            return "<"
        case _ as b if b[7]:
            return ">"
        case _ as b if b[8]:
            return "LA"
        case _ as b if b[9]:
            return "RA"
        case _ as b if b[10]:
            return "M"


CURSOR_ARROWS = {"N": "up", "E": "right", "S": "down", "W": "left"}


def process_frame(controller, key_map, output):
    """Run one frame of input handling, emitting keystrokes via output.

    output must expose .send(key) and .write(key) (the keyboard module does).
    Returns one of:
      ("cursor", None) - right stick moved (an arrow may have been sent)
      ("key", key)     - a character/special key was emitted for a button press
      ("idle", None)   - nothing happened this frame
    """
    move_cursor = get_direction(controller, "R")
    if move_cursor != "X":
        arrow = CURSOR_ARROWS.get(move_cursor)
        if arrow is not None:
            output.send(arrow)
        return ("cursor", None)

    raw_button_input = [
        controller.get_button(i) for i in range(controller.get_numbuttons())
    ]
    if any(raw_button_input):
        button = get_button(raw_button_input)
        direction = get_direction(controller, "L")
        key = key_map[(direction, button)]
        if direction == "X":
            output.send(key)
        else:
            output.write(key)
        return ("key", key)

    return ("idle", None)


def run_loop(
    controller,
    key_map,
    output=keyboard,
    *,
    sleep=sleep,
    tick=None,
    poll_events=pygame.event.get,
    should_continue=None,
):
    """Poll the controller and emit keystrokes until QUIT or should_continue()."""
    prev_key = None
    running = True
    while running:
        for event in poll_events():
            if event.type == pygame.QUIT:
                running = False

        kind, key = process_frame(controller, key_map, output)
        if kind == "cursor":
            sleep(0.1)
        elif kind == "key":
            sleep(0.3 if prev_key == key else 0.1)
            prev_key = key

        if tick is not None:
            tick()

        if should_continue is not None and not should_continue():
            running = False


if __name__ == "__main__":
    pygame.init()

    controller = pygame.joystick.Joystick(0)
    controller.init()
    clock = pygame.time.Clock()

    key_map = load_key_map()

    try:
        run_loop(controller, key_map, tick=lambda: clock.tick(60))
    finally:
        # Clean up
        print(">> cleaning up")
        controller.quit()
        pygame.quit()
