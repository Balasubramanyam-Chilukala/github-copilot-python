import sudoku_logic
from sudoku_engine import SudokuBoard, count_solutions


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


def test_is_safe_accepts_a_non_conflicting_value():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.is_safe(board, 0, 0, 5) is True


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


def test_generate_puzzle_preserves_solution_values_for_clues():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY:
                assert puzzle[row][col] == solution[row][col]


def test_generate_puzzle_has_exactly_one_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert count_solutions(puzzle, limit=2) == 1
    assert SudokuBoard(solution).is_complete() is True
    assert SudokuBoard(solution).is_valid() is True


def test_deep_copy_does_not_share_nested_rows():
    board = sudoku_logic.create_empty_board()
    copied_board = sudoku_logic.deep_copy(board)

    copied_board[0][0] = 9

    assert board[0][0] == sudoku_logic.EMPTY
