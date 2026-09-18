import pytest

from sudoku_engine import (
    DIFFICULTY_SETTINGS,
    InvalidSudokuBoardError,
    SudokuBoard,
    count_solutions,
    generate_completed_board,
    generate_puzzle,
    generate_puzzle_for_difficulty,
    get_difficulty_settings,
    has_unique_solution,
)


@pytest.fixture
def solved_board():
    return [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]


@pytest.fixture
def valid_puzzle():
    return [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]


def test_valid_completed_sudoku_board_is_accepted(solved_board):
    board = SudokuBoard(solved_board)

    assert board.is_valid() is True
    assert board.is_complete() is True


def test_invalid_board_is_rejected(solved_board):
    invalid = [row[:] for row in solved_board]
    invalid[0][0] = 1
    invalid[0][1] = 5

    board = SudokuBoard(invalid)

    assert board.is_valid() is False
    assert board.is_complete() is True


def test_solver_can_solve_a_valid_puzzle(valid_puzzle, solved_board):
    board = SudokuBoard(valid_puzzle)

    solved = board.solve()

    assert solved == solved_board


def test_solver_produces_a_valid_completed_board(valid_puzzle):
    solved = SudokuBoard(valid_puzzle).solve()
    solved_board = SudokuBoard(solved)

    assert solved_board.is_valid() is True
    assert solved_board.is_complete() is True


def test_puzzle_with_no_solution_is_detected():
    board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 8],
    ]

    assert count_solutions(board) == 0
    with pytest.raises(ValueError):
        SudokuBoard(board).solve()


def test_puzzle_with_multiple_solutions_is_detected():
    empty_board = [[0 for _ in range(9)] for _ in range(9)]

    assert count_solutions(empty_board, limit=2) == 2
    assert has_unique_solution(empty_board) is False


def test_generated_puzzle_has_exactly_one_solution():
    puzzle, solution = generate_puzzle(35)

    assert has_unique_solution(puzzle) is True
    assert count_solutions(puzzle) == 1
    assert puzzle != solution
    assert SudokuBoard(puzzle).is_valid() is True


def test_difficulty_configuration_has_relative_clue_counts():
    easy = get_difficulty_settings("easy").clues
    medium = get_difficulty_settings("medium").clues
    hard = get_difficulty_settings("hard").clues

    assert DIFFICULTY_SETTINGS["easy"]["clues"] == easy
    assert DIFFICULTY_SETTINGS["medium"]["clues"] == medium
    assert DIFFICULTY_SETTINGS["hard"]["clues"] == hard
    assert easy > medium > hard


def test_easy_medium_and_hard_puzzles_are_generated_successfully():
    for level in ("easy", "medium", "hard"):
        puzzle, solution, prefilled = generate_puzzle_for_difficulty(level)
        assert isinstance(puzzle, list)
        assert isinstance(solution, list)
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)
        assert has_unique_solution(puzzle) is True
        assert count_solutions(puzzle) == 1
        assert puzzle != solution
        assert len(prefilled) > 0
        assert all(puzzle[row][col] == solution[row][col] for row, col in prefilled)


def test_prefilled_cells_remain_part_of_the_puzzle():
    puzzle, solution = generate_puzzle(35)
    filled_cells = [(row, col) for row in range(9) for col in range(9) if puzzle[row][col] != 0]

    assert filled_cells
    for row, col in filled_cells:
        assert puzzle[row][col] == solution[row][col]


def test_invalid_board_dimensions_or_values_are_handled_appropriately():
    invalid_shapes = [
        [[1, 2, 3], [4, 5, 6]],
        [[0 for _ in range(8)] for _ in range(9)],
        [[0 for _ in range(9)] for _ in range(8)],
    ]

    for shape in invalid_shapes:
        with pytest.raises(InvalidSudokuBoardError):
            SudokuBoard(shape)

    with pytest.raises(InvalidSudokuBoardError):
        SudokuBoard([[-1 for _ in range(9)] for _ in range(9)])

    with pytest.raises(InvalidSudokuBoardError):
        SudokuBoard([[10 for _ in range(9)] for _ in range(9)])

    with pytest.raises(InvalidSudokuBoardError):
        SudokuBoard([["1" for _ in range(9)] for _ in range(9)])

    with pytest.raises(ValueError):
        SudokuBoard([[
            5, 3, 4, 6, 7, 8, 9, 1, 2,
        ] for _ in range(9)]).solve()
