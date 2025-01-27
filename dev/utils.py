import time
from autoclicker import click_position_right, go_down, go_left, go_right, go_up, move_mouse_smoothly
from logger_config import logger

def change_map(map):

    click_position_right(500, 750)
    time.sleep(0.5)
    move_mouse_smoothly(400, 750)
    time.sleep(1)
    logger.info(f'On change map vers {map}')
    if map == "gauche":
        go_left()
    elif map == "droite":
        go_right()
    elif map == "haut":
        go_up()
    elif map == "bas":
        go_down()

    time.sleep(6)