import sudoku_logic


def test_create_empty_board_returns_9_by_9_grid():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_detects_conflicts_in_row_column_and_box():
    board = [[0, 0, 0, 0, 0, 0, 0, 0, 0] for _ in range(9)]
    board[0][0] = 5
    board[0][1] = 5

    assert sudoku_logic.is_safe(board, 0, 1, 5) is False

    board = [[0, 0, 0, 0, 0, 0, 0, 0, 0] for _ in range(9)]
    board[0][0] = 5
    board[1][0] = 5

    assert sudoku_logic.is_safe(board, 1, 0, 5) is False

    board = [[0, 0, 0, 0, 0, 0, 0, 0, 0] for _ in range(9)]
    board[0][0] = 5
    board[1][1] = 5

    assert sudoku_logic.is_safe(board, 1, 1, 5) is False


def test_generate_puzzle_returns_board_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert puzzle != solution


def test_generate_puzzle_contains_zeroes_for_empty_cells():
    puzzle, _ = sudoku_logic.generate_puzzle(35)

    assert any(cell == sudoku_logic.EMPTY for row in puzzle for cell in row)
