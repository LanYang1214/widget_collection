import json
import random
import time
from pathlib import Path
from time import sleep


DEFAULT_CONFIG = [10, 16, 10, 10, 3]
CONFIG_PATH = Path(__file__).with_name("config.json")


class GameTimeout(Exception):
    """Raised when the game's time limit expires."""

def printboard(board_rows, board_columns):
    gameboard = []
    for j in range(board_rows):
        line = []
        for i in range(board_columns):
            num = random.randint(1, 9)
            line.append(num)
        gameboard.append(line)
    for k in gameboard:
        print(k)
    return gameboard, 1

def select(last_board, score, deadline):
    """Interactively select a rectangular area of ``last_board``.

    The cursor always begins at the board's top-left cell.  Press Enter once
    to place the first corner and again to confirm the opposite corner. The
    selection expires when ``deadline`` is reached.
    Returns ``((top_row, left_col), (bottom_row, right_col))``.
    """
    import curses

    if not last_board or not last_board[0]:
        raise ValueError("last_board must contain at least one cell")
    if any(len(row) != len(last_board[0]) for row in last_board):
        raise ValueError("last_board must be rectangular")

    row_count, col_count = len(last_board), len(last_board[0])

    def select_in_window(window):
        cursor_row = cursor_col = 0
        first_corner = None

        window.keypad(True)
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_BLACK, -1)
            curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)

        while True:
            seconds_remaining = deadline - time.monotonic()
            if seconds_remaining <= 0:
                raise GameTimeout

            window.erase()
            minutes, seconds = divmod(int(seconds_remaining + 0.999), 60)
            window.addstr(0, 0, f"Use arrow keys to move | Score: {score} | Time left: {minutes:02d}:{seconds:02d}")

            for row_index, row in enumerate(last_board):
                for col_index, value in enumerate(row):
                    is_cursor = (row_index, col_index) == (cursor_row, cursor_col)
                    is_marked = (row_index, col_index) == first_corner
                    is_selected = is_cursor or is_marked
                    attribute = curses.A_REVERSE if is_cursor else curses.A_NORMAL
                    if curses.has_colors():
                        if value == 0:
                            attribute = curses.color_pair(3 if is_selected else 2)
                        elif is_selected:
                            attribute |= curses.color_pair(1)
                    window.addstr(row_index + 2, col_index * 4, f"{value:>2} ", attribute)

            window.refresh()
            window.timeout(max(1, int(seconds_remaining * 1000)))
            key = window.getch()

            if key == -1 or time.monotonic() >= deadline:
                raise GameTimeout

            if key == curses.KEY_UP:
                cursor_row = max(0, cursor_row - 1)
            elif key == curses.KEY_DOWN:
                cursor_row = min(row_count - 1, cursor_row + 1)
            elif key == curses.KEY_LEFT:
                cursor_col = max(0, cursor_col - 1)
            elif key == curses.KEY_RIGHT:
                cursor_col = min(col_count - 1, cursor_col + 1)
            elif key in (curses.KEY_ENTER, 10, 13):
                if first_corner is None:
                    first_corner = (cursor_row, cursor_col)
                else:
                    return (
                        (min(first_corner[0], cursor_row), min(first_corner[1], cursor_col)),
                        (max(first_corner[0], cursor_row), max(first_corner[1], cursor_col)),
                    )
    return curses.wrapper(select_in_window)

def count(select_box, lastest_board):
    row_start = select_box[0][0]
    row_end = select_box[1][0]
    col_start = select_box[0][1]
    col_end = select_box[1][1]
    toll = 0
    for row_index in range(row_start, row_end + 1):
        row = lastest_board[row_index]
        for col_index in range(col_start, col_end + 1):
            item = row[col_index]
            toll += item
    return toll

def updateboard(remove_box, before_board, combo_boost):
    row_start = remove_box[0][0]
    row_end = remove_box[1][0]
    col_start = remove_box[0][1]
    col_end = remove_box[1][1]
    score_boost = 0
    for row_index in range(row_start, row_end + 1):
        row = before_board[row_index]
        for col_index in range(col_start, col_end + 1):
            if row[col_index] != 0:
                score_boost += combo_boost
                row[col_index] = 0
    non_empty = any(item != 0 for row in before_board for item in row)
    if non_empty:
        return before_board, 1, score_boost + 4
    else:
        return before_board, 0, score_boost + 4

def playcustomed(configurations):
    board_rows, board_columns, sum_target, game_duration_minutes, combo_boost = configurations
    board, status = printboard(board_rows, board_columns)
    score = 0
    deadline = time.monotonic() + game_duration_minutes * 60
    try:
        while status == 1:
            selection = select(board, score, deadline)
            selected = count(selection, board)
            if selected != 0 and selected % sum_target == 0:
                board, status, scoring = updateboard(selection, board, combo_boost)
                score += scoring
    except GameTimeout:
        print(f"time's up! your score: {score}")
    else:
        print(f"you win! with score: {score}")

def setup():
    print("default config:\n- board rows = 10\n- board columns = 16\n- summation target = 10\n- time limit = 10"
          "\n- combo boost = 3\n")
    print("for each term, enter the new integer, or enter nothing to skip")
    board_height = input("new board height? ")
    try:
        board_height = int(board_height)
        if board_height < 1 or board_height > 100:
            raise ValueError
    except ValueError:
        board_height = DEFAULT_CONFIG[0]
    board_width = input("new board width? ")
    try:
        board_width = int(board_width)
        if board_width < 1 or board_width > 100:
            raise ValueError
    except ValueError:
        board_width = DEFAULT_CONFIG[1]
    sum_to_times = input("new summation target? ")
    try:
        sum_to_times = int(sum_to_times)
        if sum_to_times < 1 or sum_to_times > 100:
            raise ValueError
    except ValueError:
        sum_to_times = DEFAULT_CONFIG[2]
    time_limit = input("new time limit? ")
    try:
        time_limit = int(time_limit)
        if time_limit < 1 or time_limit > 100:
            raise ValueError
    except ValueError:
        time_limit = DEFAULT_CONFIG[3]
    combo_boost = input("new combo boost value? ")
    try:
        combo_boost = int(combo_boost)
        if combo_boost < 1 or combo_boost > 100:
            raise ValueError
    except ValueError:
        combo_boost = DEFAULT_CONFIG[4]
    configurations = [board_height, board_width, sum_to_times, time_limit, combo_boost]
    save = input("\nsave for next use? y/n ")
    if save == "y":
        CONFIG_PATH.write_text(json.dumps(configurations), encoding="utf-8")
    print("you're all done! ", end = "")
    for i in "GAME START ->":
        sleep(0.05)
        print(i, end="")
    return configurations

def readjson():
    try:
        configurations = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"could not read saved configuration: {error}") from error

    if (
        not isinstance(configurations, list)
        or len(configurations) != len(DEFAULT_CONFIG)
        or any(not isinstance(value, int) or not 1 <= value <= 100 for value in configurations)
    ):
        raise ValueError("saved configuration must be a list of five integers from 1 to 100")
    return configurations

if __name__ == '__main__':
    read = input("read from saving or configure all? y/n ")
    config = readjson() if read == "y" else setup()
    playcustomed(config)
