const state = {
  target: 0,
  guesses: [],
  bestScore: null,
  roundsWon: 0,
  lowerBound: 0,
  upperBound: 100,
  solved: false,
};

const refs = {
  bestScore: document.getElementById("best-score"),
  roundsWon: document.getElementById("rounds-won"),
  attempts: document.getElementById("attempts"),
  status: document.getElementById("status"),
  badge: document.getElementById("session-badge"),
  rangeCaption: document.getElementById("range-caption"),
  activeRange: document.getElementById("active-range"),
  lastMarker: document.getElementById("last-marker"),
  history: document.getElementById("history"),
  input: document.getElementById("guess-input"),
  form: document.getElementById("guess-form"),
  smartHint: document.getElementById("smart-hint"),
  restart: document.getElementById("restart-round"),
};

function randomNumber(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function proximityText(guess) {
  const distance = Math.abs(state.target - guess);
  if (distance === 0) return "Perfect.";
  if (distance <= 3) return "You are extremely close.";
  if (distance <= 7) return "Very warm.";
  if (distance <= 15) return "Getting close.";
  if (distance <= 25) return "Still in reach.";
  return "Way off right now.";
}

function setBadge(text, color) {
  refs.badge.textContent = text;
  refs.badge.style.color = color;
}

function updateStats() {
  refs.bestScore.textContent = state.bestScore === null ? "-" : state.bestScore;
  refs.roundsWon.textContent = state.roundsWon;
  refs.attempts.textContent = state.guesses.length;
}

function updateRange() {
  refs.activeRange.style.left = `${state.lowerBound}%`;
  refs.activeRange.style.width = `${state.upperBound - state.lowerBound}%`;
  refs.rangeCaption.textContent = `${state.lowerBound} to ${state.upperBound}`;

  const lastGuess = state.guesses[state.guesses.length - 1];
  if (typeof lastGuess === "number") {
    refs.lastMarker.classList.remove("hidden");
    refs.lastMarker.style.left = `${lastGuess}%`;
  } else {
    refs.lastMarker.classList.add("hidden");
  }
}

function renderHistory() {
  refs.history.innerHTML = "";

  if (!state.guesses.length) {
    refs.history.innerHTML =
      '<div class="empty-state">Your guesses will appear here with direction and proximity feedback.</div>';
    return;
  }

  [...state.guesses].reverse().forEach((guess) => {
    const item = document.createElement("article");
    item.className = "empty-state";
    let direction = "Correct";

    if (guess < state.target) {
      direction = "Higher";
    } else if (guess > state.target) {
      direction = "Lower";
    }

    item.innerHTML = `<strong>${guess}</strong><p>${direction} | ${proximityText(guess)}</p>`;
    refs.history.appendChild(item);
  });
}

function startNewRound() {
  state.target = randomNumber(0, 100);
  state.guesses = [];
  state.lowerBound = 0;
  state.upperBound = 100;
  state.solved = false;

  refs.form.reset();
  refs.input.focus();
  refs.status.textContent =
    "New round started. The number is hidden somewhere between 0 and 100.";
  setBadge("Fresh Round", "#85f0ff");
  updateStats();
  updateRange();
  renderHistory();
}

function showHint() {
  const midpoint = Math.floor((state.lowerBound + state.upperBound) / 2);
  refs.status.textContent = `Try working near ${midpoint}. Current range: ${state.lowerBound} to ${state.upperBound}.`;
  setBadge("Hint Active", "#85f0ff");
}

function handleGuess(event) {
  event.preventDefault();

  if (state.solved) {
    refs.status.textContent = "This round is solved. Start a new round to keep playing.";
    return;
  }

  const raw = refs.input.value.trim();
  const guess = Number(raw);

  if (!raw || !Number.isInteger(guess) || guess < 0 || guess > 100) {
    refs.status.textContent = "Enter a whole number between 0 and 100.";
    setBadge("Invalid Input", "#ff8fa4");
    return;
  }

  if (state.guesses.includes(guess)) {
    refs.status.textContent = `You already tried ${guess}. Pick a new number.`;
    setBadge("Repeated Guess", "#ffd17f");
    return;
  }

  state.guesses.push(guess);

  if (guess < state.target) {
    state.lowerBound = Math.max(state.lowerBound, guess + 1);
    refs.status.textContent = `${guess} is low. Move higher. ${proximityText(guess)}`;
    setBadge("Go Higher", "#85f0ff");
  } else if (guess > state.target) {
    state.upperBound = Math.min(state.upperBound, guess - 1);
    refs.status.textContent = `${guess} is high. Pull lower. ${proximityText(guess)}`;
    setBadge("Go Lower", "#85f0ff");
  } else {
    state.solved = true;
    state.roundsWon += 1;
    if (state.bestScore === null || state.guesses.length < state.bestScore) {
      state.bestScore = state.guesses.length;
    }
    refs.status.textContent = `Locked in. You found ${state.target} in ${state.guesses.length} attempts.`;
    setBadge("Solved", "#9af7be");
  }

  refs.form.reset();
  refs.input.focus();
  updateStats();
  updateRange();
  renderHistory();
}

refs.form.addEventListener("submit", handleGuess);
refs.smartHint.addEventListener("click", showHint);
refs.restart.addEventListener("click", startNewRound);

startNewRound();
