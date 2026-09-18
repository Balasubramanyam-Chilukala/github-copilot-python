"""Reusable Sudoku engine for puzzle generation, validation, and solving."""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass
from typing import List, Sequence

SIZE = 9
EMPTY = 0
BOX_SIZE = 3
VALID_VALUES = set(range(1, SIZE + 1))

DIFFICULTY_SETTINGS = {
    "easy": {"clues": 40, "label": "easy"},
    "medium": {"clues": 32, "label": "medium"},
    "hard": {"clues": 24, "label": "hard"},
}


@dataclass(frozen=True)
class DifficultyConfig:
    """Configuration for a Sudoku difficulty level."""

    name: str
    clues: int

    @property
    def label(self) -> str:
        return self.name.lower()


def get_difficulty_settings(level: str) -> DifficultyConfig:
    """Return the configuration for a named difficulty."""
    normalized = level.lower()
    if normalized not in DIFFICULTY_SETTINGS:
        raise ValueError(f"Unsupported difficulty '{level}'.")
    settings = DIFFICULTY_SETTINGS[normalized]
    return DifficultyConfig(name=normalized, clues=settings["clues"])


class InvalidSudokuBoardError(ValueError):
    """Raised when a board is structurally invalid for Sudoku."""


class SudokuBoard:
    """Represents a 9x9 Sudoku board."""

    def __init__(self, grid: Sequence[Sequence[int]]) -> None:
        self.grid = self._validate_and_normalize(grid)

    @staticmethod
    def _validate_and_normalize(grid: Sequence[Sequence[int]]) -> List[List[int]]:
        if not isinstance(grid, Sequence) or len(grid) != SIZE:
            raise InvalidSudokuBoardError("Sudoku board must contain exactly 9 rows.")

        normalized: List[List[int]] = []
        for row in grid:
            if not isinstance(row, Sequence) or len(row) != SIZE:
                raise InvalidSudokuBoardError("Each Sudoku row must contain exactly 9 values.")
            normalized_row: List[int] = []
            for value in row:
                if not isinstance(value, int):
                    raise InvalidSudokuBoardError("Board values must be integers.")
                if value < EMPTY or value > SIZE:
                    raise InvalidSudokuBoardError("Board values must be between 0 and 9.")
                normalized_row.append(value)
            normalized.append(normalized_row)
        return normalized

    def copy(self) -> "SudokuBoard":
        """Return a deep copy of the board."""
        return SudokuBoard(copy.deepcopy(self.grid))

    def can_place(self, row: int, col: int, value: int) -> bool:
        """Return whether a value can be placed in the given cell without conflicts."""
        if not 0 <= row < SIZE or not 0 <= col < SIZE:
            raise IndexError("Row and column indices must be within the 9x9 board.")
        if value < 1 or value > SIZE:
            raise ValueError("Value must be between 1 and 9.")

        if self.grid[row][col] != EMPTY:
            return False

        for idx in range(SIZE):
            if self.grid[row][idx] == value or self.grid[idx][col] == value:
                return False

        start_row = (row // BOX_SIZE) * BOX_SIZE
        start_col = (col // BOX_SIZE) * BOX_SIZE
        for r in range(start_row, start_row + BOX_SIZE):
            for c in range(start_col, start_col + BOX_SIZE):
                if self.grid[r][c] == value:
                    return False
        return True

    def get_candidates(self, row: int, col: int) -> set[int]:
        """Return the valid values that can be placed in a cell."""
        if not 0 <= row < SIZE or not 0 <= col < SIZE:
            raise IndexError("Row and column indices must be within the 9x9 board.")
        if self.grid[row][col] != EMPTY:
            return set()

        candidates = set(VALID_VALUES)
        for idx in range(SIZE):
            candidates.discard(self.grid[row][idx])
            candidates.discard(self.grid[idx][col])

        start_row = (row // BOX_SIZE) * BOX_SIZE
        start_col = (col // BOX_SIZE) * BOX_SIZE
        for r in range(start_row, start_row + BOX_SIZE):
            for c in range(start_col, start_col + BOX_SIZE):
                candidates.discard(self.grid[r][c])
        return candidates

    def is_valid(self) -> bool:
        """Return whether the current board has no row, column, or box conflicts."""
        for row in self.grid:
            seen = {value for value in row if value != EMPTY}
            if len(seen) != sum(1 for value in row if value != EMPTY):
                return False
        for col in range(SIZE):
            seen = {self.grid[row][col] for row in range(SIZE) if self.grid[row][col] != EMPTY}
            if len(seen) != sum(1 for row in range(SIZE) if self.grid[row][col] != EMPTY):
                return False
        for box_row in range(0, SIZE, BOX_SIZE):
            for box_col in range(0, SIZE, BOX_SIZE):
                seen = set()
                for row in range(box_row, box_row + BOX_SIZE):
                    for col in range(box_col, box_col + BOX_SIZE):
                        value = self.grid[row][col]
                        if value == EMPTY:
                            continue
                        if value in seen:
                            return False
                        seen.add(value)
        return True

    def is_complete(self) -> bool:
        """Return whether the board has no empty cells."""
        return all(value != EMPTY for row in self.grid for value in row)

    def solve(self) -> List[List[int]]:
        """Solve the board using backtracking and return the solved grid."""
        if not self.is_valid():
            raise ValueError("Cannot solve an invalid Sudoku board.")

        board = copy.deepcopy(self.grid)

        def backtrack() -> bool:
            for row in range(SIZE):
                for col in range(SIZE):
                    if board[row][col] == EMPTY:
                        for value in random.sample(sorted(VALID_VALUES), len(VALID_VALUES)):
                            if value in SudokuBoard(board).get_candidates(row, col):
                                board[row][col] = value
                                if backtrack():
                                    return True
                                board[row][col] = EMPTY
                        return False
            return True

        if not backtrack():
            raise ValueError("No solution exists for the provided board.")
        return board


def generate_completed_board() -> List[List[int]]:
    """Generate a fully solved Sudoku board."""
    board = SudokuBoard([[EMPTY for _ in range(SIZE)] for _ in range(SIZE)])
    solution = board.copy()
    return solution.solve()


def count_solutions(board: Sequence[Sequence[int]], limit: int = 2) -> int:
    """Count solutions for a board, stopping once the limit is reached."""
    sudoku = SudokuBoard(board)
    if not sudoku.is_valid():
        return 0

    grid = [list(row) for row in sudoku.grid]
    solutions = 0

    def backtrack() -> bool:
        nonlocal solutions
        if solutions >= limit:
            return True

        row, col = None, None
        for r in range(SIZE):
            for c in range(SIZE):
                if grid[r][c] == EMPTY:
                    row, col = r, c
                    break
            if row is not None:
                break

        if row is None:
            solutions += 1
            return solutions < limit

        for value in sorted(VALID_VALUES):
            if SudokuBoard(grid).can_place(row, col, value):
                grid[row][col] = value
                if backtrack():
                    if solutions >= limit:
                        return True
                grid[row][col] = EMPTY
                if solutions >= limit:
                    return True
        return False

    backtrack()
    return solutions


def has_unique_solution(board: Sequence[Sequence[int]]) -> bool:
    """Return whether a board has exactly one valid solution."""
    return count_solutions(board, limit=2) == 1


def _remove_cells(board: List[List[int]], clues: int) -> None:
    """Remove cells from a solved board until the clue count is reached."""
    if clues < 17 or clues > SIZE * SIZE:
        raise ValueError("Clues must be between 17 and 81.")

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    empties_needed = SIZE * SIZE - clues
    removed = 0

    for row, col in cells:
        if removed >= empties_needed:
            break
        if board[row][col] != EMPTY:
            original = board[row][col]
            board[row][col] = EMPTY
            if not has_unique_solution(board):
                board[row][col] = original
            else:
                removed += 1


def generate_puzzle(clues: int = 35) -> tuple[List[List[int]], List[List[int]]]:
    """Generate a puzzle with exactly one solution and return puzzle and solution."""
    if clues < 17 or clues > SIZE * SIZE:
        raise ValueError("Clues must be between 17 and 81.")

    solution = generate_completed_board()
    puzzle = copy.deepcopy(solution)
    _remove_cells(puzzle, clues)

    if not has_unique_solution(puzzle):
        raise ValueError("Generated puzzle does not have exactly one solution.")

    return puzzle, solution


def generate_puzzle_for_difficulty(level: str) -> tuple[List[List[int]], List[List[int]], set[tuple[int, int]]]:
    """Generate a valid puzzle for a given difficulty and return puzzle, solution, and fixed cells."""
    config = get_difficulty_settings(level)
    puzzle, solution = generate_puzzle(config.clues)
    prefilled = {(row, col) for row in range(SIZE) for col in range(SIZE) if puzzle[row][col] != EMPTY}
    return puzzle, solution, prefilled
