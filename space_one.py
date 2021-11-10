import time
import curses
import asyncio
import random
from fire_animation import fire
from curses_tools import draw_frame, read_controls, get_frame_size
import os
import itertools


TIC_TIMEOUT = 0.1
STARS = '+*.:'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BORDER = 1


async def blink(canvas, row, column, symbol='*'):

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(random.randint(1, 19)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(2):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(4):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(2):
            await asyncio.sleep(0)


def read_file(path):
    with open(path, 'r') as file:
        return file.read()


async def animate_spaceship(canvas, row, column, frames, max_row, max_column):

    frame_rows, frame_cols = get_frame_size(frames[0])

    for frame in itertools.cycle(frames):

            row_dir, col_dir, _ = read_controls(canvas)

            row += row_dir
            column += col_dir

            if row <= 0:
                row = 1
            if row + frame_rows >= max_row:
                row = max_row - frame_rows - BORDER
            if column <= 0:
                column = 1
            if column + frame_cols >= max_column:
                column = max_column - frame_cols - BORDER

            draw_frame(canvas, round(row), round(column), frame)
            await asyncio.sleep(0)
            draw_frame(canvas, round(row), round(column), frame, negative=True)


def draw(canvas):
    canvas.nodelay(True)
    curses.curs_set(False)
    rocket_frame_1 = read_file(
        os.path.join(BASE_DIR, 'frames/rocket_frame_1.txt')
    )
    rocket_frame_2 = read_file(
        os.path.join(BASE_DIR, 'frames/rocket_frame_2.txt')
    )
    rocket_frames = [rocket_frame_1, rocket_frame_2]
    max_row, max_column = canvas.getmaxyx()
    max_star_row = max_row - 2
    max_star_column = max_column - 2

    coroutines = [
        blink(
            canvas,
            random.randint(1, max_star_row),
            random.randint(1, max_star_column),
            random.choice(STARS)
        ) for i in range(random.randint(1, max_column))
    ]

    field_center_row = max_row//2
    field_center_column = max_column//2

    gun_fire = fire(canvas, field_center_row, field_center_column)
    coroutines.append(gun_fire)

    spaceship_center_column = field_center_column-2

    spaceship = animate_spaceship(
        canvas,
        field_center_row,
        spaceship_center_column,
        rocket_frames,
        max_row,
        max_column
    )
    coroutines.append(spaceship)
    while True:
        canvas.refresh()
        for coroutine in coroutines.copy():

            try:
                coroutine.send(None)
                canvas.border()

            except StopIteration:
                coroutines.remove(coroutine)
        if not coroutines:
            continue
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':

    curses.update_lines_cols()
    curses.wrapper(draw)
