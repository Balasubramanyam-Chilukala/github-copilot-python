# Copilot Instructions for the Sudoku Flask Project

## Project goal
This repository is a Python Flask Sudoku application that should remain lightweight, maintainable, and easy to extend. The application must support a 9x9 Sudoku board, multiple difficulty levels (easy, medium, hard), unique generated puzzles, responsive UI behavior, dark mode, a timer, hints, validation feedback, and a local leaderboard.

The codebase should prioritize clarity over cleverness. Favor small, testable functions and clearly separated responsibilities over deeply nested logic or tightly coupled UI and backend code.

## 1. Python and Flask code organization
- Keep the Flask application modular and easy to navigate.
- Prefer a structure such as:
  - `app.py` for app creation and route registration only
  - `services/` for game logic, puzzle generation, validation, and solver rules
  - `models/` or `domain/` for dataclasses or structured board/game state objects
  - `utils/` for shared helpers
  - `templates/` and `static/` for frontend assets
- Keep route handlers thin and focused on request/response flow.
- Business rules should live outside route functions; do not embed puzzle-generation logic directly inside Flask handlers.
- Use functions with clear names such as `generate_puzzle`, `validate_move`, `check_board`, `apply_hint`, `format_time`.
- Use type hints where helpful, especially for board structures, move validation, and puzzle metadata.
- Keep Flask-specific concerns separate from game rules so the logic remains testable without a live web server.

Why this matters: A Sudoku game has a lot of rules and edge cases. Splitting the logic into reusable modules makes the code easier to understand, test, and evolve as the app grows.

## 2. JavaScript organization
- Keep JavaScript modular and organized by responsibility.
- Prefer separate modules or clear sections for:
  - board rendering
  - user input and validation
  - timer logic
  - hint/check behavior
  - leaderboard persistence
  - dark mode handling
  - difficulty selection
- Use DOM event delegation for repeated board interactions rather than attaching handlers to every individual cell.
- Avoid large single-file scripts that mix rendering, rules, and UI state management.
- Store game state in a predictable structure instead of relying on implicit DOM state alone.
- Use clear naming for UI actions such as `renderBoard()`, `handleCellInput()`, `checkBoard()`, `showInvalidCell()`, `saveLeaderboardEntry()`.
- Keep browser logic deterministic and readable. Favor explicit state updates over hidden side effects.

Why this matters: The board is interactive and stateful. Modular JavaScript reduces bugs, improves maintainability, and makes future enhancements easier to implement safely.

## 3. HTML and CSS accessibility and responsiveness
- Use semantic HTML for structure, including buttons, labels, form controls, and lists where appropriate.
- Ensure keyboard accessibility for all interactive controls.
- Provide visible focus states for buttons and inputs.
- Use color contrast that remains readable in both light and dark mode.
- Do not rely on color alone to communicate validity; combine color with visible text or labels when needed.
- Design the layout to work on mobile and desktop screens using responsive CSS.
- Ensure the Sudoku grid remains usable at smaller widths without overlapping or clipping cells.
- Use CSS for alternating 3x3 region styling so different regions are visually distinct without harming readability.
- Keep styles organized by component or section, not as one large unstructured stylesheet.

Why this matters: A Sudoku app is highly visual and interactive. Good accessibility and responsive design improve usability for all users and prevent obvious issues on mobile devices.

## 4. Error handling and user feedback
- Handle invalid moves immediately and show clear UI feedback without breaking the game flow.
- Invalid entries should be visually highlighted and should not silently fail.
- When puzzles cannot be generated or validated correctly, surface a clear error message instead of crashing the page or app.
- Show graceful fallback messages for missing data, invalid leaderboard entries, or bad input.
- Validate backend requests and front-end input before acting on them.
- Prefer explicit checks and descriptive exceptions over broad `except:` blocks.
- Keep error messages user-friendly, brief, and actionable.

Why this matters: A game can fail in many ways, especially around puzzle generation and user input. Good error handling keeps the experience stable and understandable.

## 5. Naming conventions and code style
- Use clear, descriptive names for variables, functions, and modules.
- Prefer snake_case for Python and camelCase for JavaScript, matching the project’s language conventions.
- Use `is_`/`has_`/`can_` prefixes for boolean values when helpful.
- Avoid abbreviations that reduce readability unless they are standard in the domain.
- Use constant names in uppercase for fixed values such as board size, difficulty settings, and leaderboard limits.
- Write code that reads naturally and can be understood by someone new to the repository.
- Keep functions focused on a single responsibility.

Why this matters: Consistent naming and readable code help both humans and Copilot generate accurate, maintainable solutions.

## 6. Testing expectations
- Write tests for core game logic before or alongside feature work.
- At minimum, cover:
  - valid puzzle generation checks
  - uniqueness of solution checks
  - move validation rules
  - hint application behavior
  - board completion checks
  - leaderboard data formatting and persistence logic
- Prefer unit tests for pure logic and small integration tests where appropriate.
- Test the most error-prone rules, especially Sudoku validity and uniqueness constraints.
- Keep test names descriptive and behavior-focused.
- Do not skip tests for puzzle correctness, because unique-solution generation is a critical requirement.

Why this matters: Sudoku rules are easy to get subtly wrong. Automated tests protect correctness and reduce regressions while refactoring.

## 7. Frontend/backend separation of responsibilities
- The backend should own puzzle generation, validation, and rules enforcement.
- The frontend should own rendering, interaction logic, timer display, and local UI state.
- Use backend endpoints or API-style responses for game operations that need shared logic or server-side coordination.
- Do not let the browser directly determine all game rules in a way that bypasses backend validation.
- Keep the UI responsible for feedback, animation, and user experience; keep the rules engine responsible for correctness.
- If data is displayed in the frontend, it should be derived from game state rather than hidden DOM assumptions.

Why this matters: Clear separation reduces duplication, improves testability, and helps ensure that game rules stay consistent across the app.

## 8. Avoiding unnecessary dependencies
- Keep the project lightweight and use only the libraries needed for Flask and the game.
- Prefer standard Python libraries and simple Flask patterns over large frameworks or heavy abstractions.
- Avoid adding front-end frameworks or complex build pipelines unless doing so is clearly necessary.
- Do not add dependencies for simple DOM work, localStorage handling, or small utility logic that can be implemented directly.
- If a dependency is introduced, justify it in terms of maintainability, reliability, or a real project requirement.

Why this matters: This project is a small Flask app. Minimal dependencies improve reliability, reduce maintenance cost, and keep the project approachable.

## 9. Maintainability and readability
- Write code that is easy for someone else to understand without deep context.
- Favor explicit, readable implementation over terse or clever solutions.
- Add brief comments only where the logic is non-obvious or domain-specific.
- Keep functions short and cohesive.
- Refactor repeated logic into shared helpers instead of copying logic across files.
- Do not add complexity that the app does not need.
- Keep HTML, CSS, and JavaScript easy to scan and maintain.

Why this matters: This is a learning project and a refactoring exercise. Readability is a first-class requirement because future improvements depend on code being easy to reason about.

## 10. Modern Python practices within a Flask app
- Use modern Python features where they improve clarity, such as dataclasses, f-strings, comprehensions, and type hints in appropriate places.
- Keep the structure simple and idiomatic for Flask rather than forcing advanced patterns that are unnecessary for this project.
- Use `if __name__ == "__main__":` for local development entry points when appropriate.
- Prefer straightforward, explicit logic over abstract frameworks that make the app harder to follow.
- Maintain compatibility with the project’s Python environment while using modern, readable syntax supported by the repo’s version.

Why this matters: Modern Python practices improve maintainability without overengineering a small Flask application.

## Required project behaviors to preserve and enhance
- 9x9 Sudoku board and rules
- easy, medium, and hard difficulty levels
- unique-solution puzzle generation
- locked prefilled cells
- immediate invalid move feedback
- check button highlighting incorrect entries
- hint button that fills exactly one correct empty cell and locks it
- timer tracking completion time
- Top 10 leaderboard with persistent browser localStorage
- leaderboard entries including player name, time, difficulty, and hints used
- dark mode support
- responsive layout for desktop and mobile
- alternating 3x3 region styling
- modular, readable, maintainable, and testable code

## Contribution guidance for Copilot
When generating code or proposing changes:
- prefer the simplest correct solution
- keep existing project structure understandable
- avoid unnecessary refactors unrelated to the task
- preserve the game’s UX and requirements while improving architecture
- validate changes with targeted tests where practical
- ensure the feature works without breaking puzzle correctness or UI stability

This instruction file is intended to keep future changes aligned with the project’s technical and product requirements while encouraging maintainable, readable, and testable code.
