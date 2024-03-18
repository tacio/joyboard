from time import sleep

import keyboard
import pygame

LAYER_DIR_LETTER_MAP = {}


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


if __name__ == "__main__":
    pygame.init()

    controller = pygame.joystick.Joystick(0)
    controller.init()
    clock = pygame.time.Clock()

    LAYER_DIR_LETTER_MAP = load_key_map()
    prev_key = None

    try:
        running = True
        while running:
            a_button = 0

            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            move_cursor = get_direction(controller, "R")
            if move_cursor != "X":
                match move_cursor:
                    case "N":
                        keyboard.send("up")
                    case "E":
                        keyboard.send("right")
                    case "S":
                        keyboard.send("down")
                    case "W":
                        keyboard.send("left")
                sleep(0.1)

            else:
                raw_buttom_input = [
                    controller.get_button(i) for i in range(controller.get_numbuttons())
                ]
                if any(raw_buttom_input):
                    buttom = get_button(raw_buttom_input)
                    direction = get_direction(controller, "L")
                    # print(direction, buttom)
                    if direction == "X":
                        key = LAYER_DIR_LETTER_MAP[(direction, buttom)]
                        keyboard.send(key)
                    else:
                        key = LAYER_DIR_LETTER_MAP[(direction, buttom)]
                        keyboard.write(key)

                    if prev_key == key:
                        sleep(0.3)
                    else:
                        sleep(0.1)
                    prev_key = key

            clock.tick(60)

    finally:
        # Clean up
        print(">> cleaning up")
        controller.quit()
        pygame.quit()
