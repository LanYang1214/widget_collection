import random
import time


BOARD_ROW = 10
BOARD_COL = 16
SUM_TARGET = 10
GAME_DURATION_MINUTES = 10
COMBO_BOOST = 3


class GameTimeout(Exception):
    """Raised when the game's time limit expires."""

def printboard():
    gameboard = []
    for j in range(BOARD_ROW):
        line = []
        for i in range(BOARD_COL):
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

def updateboard(remove_box, before_board):
    row_start = remove_box[0][0]
    row_end = remove_box[1][0]
    col_start = remove_box[0][1]
    col_end = remove_box[1][1]
    score_boost = 0
    for row_index in range(row_start, row_end + 1):
        row = before_board[row_index]
        for col_index in range(col_start, col_end + 1):
            if row[col_index] != 0:
                score_boost += COMBO_BOOST
                row[col_index] = 0
    non_empty = any(i != 0 for row in before_board for i in row)
    if non_empty:
        return before_board, 1, score_boost + 4
    else:
        return before_board, 0, score_boost + 4

if __name__ == '__main__':
    board, status = printboard()
    score = 0
    deadline = time.monotonic() + GAME_DURATION_MINUTES * 60
    try:
        while status == 1:
            selection = select(board, score, deadline)
            if count(selection, board) == SUM_TARGET:
                board, status, scoring = updateboard(selection, board)
                score += scoring
    except GameTimeout:
        print(f"\ntime's up! your score: {score}")
    else:
        print(f"\nyou win! with score: {score}")
