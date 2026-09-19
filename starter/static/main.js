const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuLeaderboard';
const THEME_STORAGE_KEY = 'sudokuTheme';
const MAX_LEADERBOARD_ENTRIES = 10;
const DIFFICULTY_CONFIG = {
  easy: 40,
  medium: 32,
  hard: 24,
};

const state = {
  puzzle: [],
  solution: [],
  difficulty: 'medium',
  hintedCells: new Set(),
  hintsUsed: 0,
  elapsedSeconds: 0,
  timerIntervalId: null,
  completed: false,
};

const boardElement = document.getElementById('sudoku-board');
const messageElement = document.getElementById('message');
const hintCountElement = document.getElementById('hint-count');
const timerElement = document.getElementById('timer-display');
const completionSummaryElement = document.getElementById('completion-summary');
const completionDetailsElement = document.getElementById('completion-details');
const leaderboardBodyElement = document.getElementById('leaderboard-body');
const themeToggle = document.getElementById('theme-toggle');

function getInitialTheme() {
  try {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (storedTheme === 'light' || storedTheme === 'dark') {
      return storedTheme;
    }
  } catch (error) {
    // Fall back to the system preference when storage is unavailable.
  }

  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
}

function applyTheme(theme, persist = true) {
  const normalizedTheme = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.theme = normalizedTheme;
  themeToggle.setAttribute('aria-pressed', String(normalizedTheme === 'dark'));
  themeToggle.textContent = normalizedTheme === 'dark'
    ? 'Enable light mode'
    : 'Enable dark mode';

  if (persist) {
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, normalizedTheme);
    } catch (error) {
      // The theme still applies for this page when storage is unavailable.
    }
  }
}
const difficultySelect = document.getElementById('difficulty-select');
const newGameButton = document.getElementById('new-game');
const checkButton = document.getElementById('check-solution');
const hintButton = document.getElementById('hint-button');

function formatElapsedTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function isValidScore(score) {
  return score
    && typeof score.name === 'string'
    && score.name.trim().length > 0
    && Number.isInteger(score.timeSeconds)
    && score.timeSeconds >= 0
    && Object.prototype.hasOwnProperty.call(DIFFICULTY_CONFIG, score.difficulty)
    && Number.isInteger(score.hintsUsed)
    && score.hintsUsed >= 0;
}

function normalizeScores(scores) {
  if (!Array.isArray(scores)) {
    return [];
  }

  return scores
    .filter(isValidScore)
    .map((score) => ({
      name: score.name.trim(),
      timeSeconds: score.timeSeconds,
      difficulty: score.difficulty,
      hintsUsed: score.hintsUsed,
    }));
}

function sortScores(scores) {
  return [...scores].sort((first, second) => {
    if (first.timeSeconds !== second.timeSeconds) {
      return first.timeSeconds - second.timeSeconds;
    }
    if (first.hintsUsed !== second.hintsUsed) {
      return first.hintsUsed - second.hintsUsed;
    }
    return first.name.localeCompare(second.name);
  });
}

function limitScores(scores) {
  return sortScores(scores).slice(0, MAX_LEADERBOARD_ENTRIES);
}

function loadScores() {
  try {
    const storedScores = window.localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    if (!storedScores) {
      return [];
    }

    const parsedScores = JSON.parse(storedScores);
    const topScores = limitScores(normalizeScores(parsedScores));
    const canonicalScores = JSON.stringify(topScores);

    if (storedScores !== canonicalScores) {
      window.localStorage.setItem(LEADERBOARD_STORAGE_KEY, canonicalScores);
    }

    return topScores;
  } catch (error) {
    return [];
  }
}

function saveScores(scores) {
  const topScores = limitScores(normalizeScores(scores));

  try {
    window.localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(topScores));
    return true;
  } catch (error) {
    return false;
  }
}

function addScore(score) {
  if (!isValidScore(score)) {
    return loadScores();
  }

  const scores = limitScores([...loadScores(), {
    ...score,
    name: score.name.trim(),
  }]);
  saveScores(scores);
  return scores;
}

function renderLeaderboard(scores = loadScores()) {
  leaderboardBodyElement.innerHTML = '';
  const topScores = limitScores(normalizeScores(scores));

  if (topScores.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.className = 'leaderboard-empty';
    cell.textContent = 'No completed games yet.';
    row.appendChild(cell);
    leaderboardBodyElement.appendChild(row);
    return;
  }

  topScores.forEach((score, index) => {
    const row = document.createElement('tr');
    const values = [
      String(index + 1),
      score.name,
      formatElapsedTime(score.timeSeconds),
      score.difficulty,
      String(score.hintsUsed),
    ];

    values.forEach((value) => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.appendChild(cell);
    });

    leaderboardBodyElement.appendChild(row);
  });
}

function updateTimerDisplay() {
  timerElement.textContent = `Time: ${formatElapsedTime(state.elapsedSeconds)}`;
}

function stopTimer() {
  if (state.timerIntervalId !== null) {
    window.clearInterval(state.timerIntervalId);
    state.timerIntervalId = null;
  }
}

function startTimer() {
  stopTimer();
  state.elapsedSeconds = 0;
  updateTimerDisplay();

  state.timerIntervalId = window.setInterval(() => {
    state.elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function isBoardSolved(board = readBoardFromGrid()) {
  if (board.length !== SIZE || state.solution.length !== SIZE) {
    return false;
  }

  for (let row = 0; row < SIZE; row += 1) {
    if (board[row].length !== SIZE || state.solution[row].length !== SIZE) {
      return false;
    }

    for (let col = 0; col < SIZE; col += 1) {
      if (!Number.isInteger(board[row][col])
        || board[row][col] < 1
        || board[row][col] > SIZE
        || board[row][col] !== state.solution[row][col]) {
        return false;
      }
    }
  }

  return true;
}

function showMessage(text, type = 'error') {
  messageElement.textContent = text;
  messageElement.className = `message ${type}`;
}

function updateHintCounter() {
  hintCountElement.textContent = `Hints used: ${state.hintsUsed}`;
}

function resetCompletionSummary() {
  completionSummaryElement.hidden = true;
  completionDetailsElement.textContent = '';
}

function completePuzzle(board = readBoardFromGrid()) {
  if (state.completed || !isBoardSolved(board)) {
    return false;
  }

  state.completed = true;
  stopTimer();

  const finalTime = formatElapsedTime(state.elapsedSeconds);
  completionDetailsElement.textContent = `Time: ${finalTime} | Difficulty: ${state.difficulty} | Hints used: ${state.hintsUsed}`;
  completionSummaryElement.hidden = false;
  showMessage('Congratulations! You solved the puzzle!', 'success');

  const playerName = window.prompt('Enter your name for the leaderboard:');
  const name = playerName && playerName.trim() ? playerName.trim() : 'Anonymous';
  state.completionResult = {
    name,
    timeSeconds: state.elapsedSeconds,
    difficulty: state.difficulty,
    hintsUsed: state.hintsUsed,
  };
  renderLeaderboard(addScore(state.completionResult));

  return true;
}

function createBoardElement() {
  boardElement.innerHTML = '';

  for (let rowIndex = 0; rowIndex < SIZE; rowIndex += 1) {
    const row = document.createElement('div');
    row.className = 'sudoku-row';
    row.setAttribute('role', 'row');

    for (let colIndex = 0; colIndex < SIZE; colIndex += 1) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.classList.add(`region-${Math.floor(rowIndex / 3)}-${Math.floor(colIndex / 3)}`);
      input.setAttribute('role', 'gridcell');
      input.dataset.row = String(rowIndex);
      input.dataset.col = String(colIndex);
      input.setAttribute('aria-label', `Row ${rowIndex + 1}, column ${colIndex + 1}`);
      row.appendChild(input);
    }

    boardElement.appendChild(row);
  }
}

function renderPuzzle(puzzle, solution = []) {
  state.puzzle = puzzle;
  state.solution = solution;
  state.hintedCells = new Set();
  state.hintsUsed = 0;
  state.completed = false;
  state.completionResult = null;
  state.elapsedSeconds = 0;
  stopTimer();
  updateTimerDisplay();
  updateHintCounter();
  resetCompletionSummary();
  createBoardElement();

  const inputs = boardElement.querySelectorAll('.sudoku-cell');
  inputs.forEach((input) => {
    const row = Number(input.dataset.row);
    const col = Number(input.dataset.col);
    const value = puzzle[row][col];

    input.value = value === 0 ? '' : String(value);
    input.disabled = value !== 0;
    input.checked = false;
    input.setAttribute('aria-invalid', 'false');
    input.removeAttribute('title');
    input.classList.remove('incorrect', 'hinted');
    if (value !== 0) {
      input.classList.add('prefilled');
    }
  });
}

function readBoardFromGrid() {
  const result = [];
  const rows = boardElement.querySelectorAll('.sudoku-row');

  rows.forEach((row) => {
    const cells = row.querySelectorAll('.sudoku-cell');
    const values = [];

    cells.forEach((cell) => {
      const value = cell.value.trim();
      values.push(value === '' ? 0 : Number.parseInt(value, 10));
    });

    result.push(values);
  });

  return result;
}

function resetCellHighlights() {
  const inputs = boardElement.querySelectorAll('.sudoku-cell');
  inputs.forEach((input) => {
    if (input.disabled) {
      return;
    }
    input.classList.remove('incorrect');
  });
}

function handleCellInput(event) {
  const input = event.target;
  if (!input.classList.contains('sudoku-cell')) {
    return;
  }

  if (input.disabled || state.hintedCells.has(`${input.dataset.row}-${input.dataset.col}`)) {
    input.value = input.value || '';
    return;
  }

  const value = input.value.replace(/[^1-9]/g, '').slice(0, 1);
  input.value = value;
  input.classList.remove('incorrect');
  input.setAttribute('aria-invalid', 'false');
  input.removeAttribute('title');

  if (value === '') {
    showMessage('', 'success');
    return;
  }

  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const expected = Number(state.solution[row]?.[col]);

  if (!Number.isInteger(expected) || Number(value) !== expected) {
    input.classList.add('incorrect');
    input.setAttribute('aria-invalid', 'true');
    input.setAttribute('title', 'This value does not match the correct Sudoku solution.');
    showMessage('Incorrect entry: this value does not match the solution.', 'error');
    return;
  }

  if (completePuzzle()) {
    return;
  }

  showMessage('Correct entry.', 'success');
}

async function newGame() {
  stopTimer();
  const clues = DIFFICULTY_CONFIG[state.difficulty];
  showMessage('Loading puzzle...', 'success');

  try {
    const response = await fetch(`/new?clues=${clues}`);
    if (!response.ok) {
      throw new Error('Unable to load a new puzzle.');
    }

    const data = await response.json();
    renderPuzzle(data.puzzle, data.solution || []);
    resetCellHighlights();
    startTimer();
    showMessage('', 'success');
  } catch (error) {
    showMessage(error.message || 'Could not load the puzzle.', 'error');
  }
}

async function checkSolution() {
  const board = readBoardFromGrid();

  try {
    const response = await fetch('/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board }),
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || 'Unable to validate the board.');
    }

    const incorrect = new Set(data.incorrect.map(([row, col]) => row * SIZE + col));
    const inputs = boardElement.querySelectorAll('.sudoku-cell');

    inputs.forEach((input) => {
      if (input.disabled || state.hintedCells.has(`${input.dataset.row}-${input.dataset.col}`)) {
        return;
      }

      const row = Number(input.dataset.row);
      const col = Number(input.dataset.col);
      const index = row * SIZE + col;
      input.classList.remove('incorrect');
      input.setAttribute('aria-invalid', 'false');
      input.removeAttribute('title');

      if (incorrect.has(index)) {
        input.classList.add('incorrect');
        input.setAttribute('aria-invalid', 'true');
        input.setAttribute('title', 'This entry is incorrect.');
      }
    });

    if (incorrect.size === 0 && completePuzzle(board)) {
      return;
    }

    showMessage('Some cells are incorrect. Try again.', 'error');
  } catch (error) {
    showMessage(error.message || 'Validation failed.', 'error');
  }
}

function applyHint() {
  const inputs = boardElement.querySelectorAll('.sudoku-cell');
  let targetInput = null;

  for (const input of inputs) {
    if (input.disabled) {
      continue;
    }

    const key = `${input.dataset.row}-${input.dataset.col}`;
    if (state.hintedCells.has(key)) {
      continue;
    }

    const row = Number(input.dataset.row);
    const col = Number(input.dataset.col);
    const solutionValue = Number(state.solution[row]?.[col]);

    if (!Number.isInteger(solutionValue)) {
      continue;
    }

    targetInput = input;
    break;
  }

  if (!targetInput) {
    showMessage('No empty cells remain to hint.', 'error');
    return;
  }

  const row = Number(targetInput.dataset.row);
  const col = Number(targetInput.dataset.col);
  const solutionValue = Number(state.solution[row][col]);
  const key = `${row}-${col}`;

  targetInput.value = String(solutionValue);
  targetInput.disabled = true;
  targetInput.classList.add('hinted');
  targetInput.classList.remove('incorrect');
  targetInput.setAttribute('aria-invalid', 'false');
  targetInput.removeAttribute('title');
  state.hintedCells.add(key);
  state.hintsUsed += 1;
  updateHintCounter();
  if (completePuzzle()) {
    return;
  }
  showMessage('Hint used: one correct cell was revealed.', 'success');
}

function bindEvents() {
  themeToggle.addEventListener('click', () => {
    const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
  });

  difficultySelect.addEventListener('change', (event) => {
    state.difficulty = event.target.value;
    newGame();
  });

  newGameButton.addEventListener('click', newGame);
  checkButton.addEventListener('click', checkSolution);
  hintButton.addEventListener('click', applyHint);
  boardElement.addEventListener('input', handleCellInput);
}

window.addEventListener('load', () => {
  bindEvents();
  applyTheme(getInitialTheme(), false);
  createBoardElement();
  state.difficulty = difficultySelect.value;
  updateTimerDisplay();
  renderLeaderboard();
  newGame();
});