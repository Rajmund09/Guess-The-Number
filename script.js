const state = {
  target: 0,
  guesses: [],
  bestScore: null,
  roundsWon: 0,
  lowerBound: 0,
  upperBound: 100,
  solved: false,
  statusTimer: null,
  toastTimer: null,
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
  newRoundTop: document.getElementById("new-round-top"),
  toast: document.getElementById("toast"),
  confetti: document.getElementById("confetti"),
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

function setBadge(label, tone = "info") {
  const toneMap = {
    info: ["rgba(133, 240, 255, 0.1)", "#85f0ff", "rgba(133, 240, 255, 0.18)"],
    success: ["rgba(154, 247, 190, 0.12)", "#9af7be", "rgba(154, 247, 190, 0.18)"],
    warn: ["rgba(255, 209, 127, 0.12)", "#ffd17f", "rgba(255, 209, 127, 0.18)"],
    error: ["rgba(255, 143, 164, 0.12)", "#ff8fa4", "rgba(255, 143, 164, 0.18)"],
  };

  const [bg, color, border] = toneMap[tone] || toneMap.info;
  refs.badge.textContent = label;
  refs.badge.style.background = bg;
  refs.badge.style.color = color;
  refs.badge.style.borderColor = border;
}

function typeStatus(message, tone = "info") {
  const colorMap = {
    info: "#85f0ff",
    success: "#9af7be",
    warn: "#ffd17f",
    error: "#ff8fa4",
  };

  if (state.statusTimer) {
    clearInterval(state.statusTimer);
  }

  refs.status.style.color = colorMap[tone] || "#eef3fb";
  refs.status.textContent = "";

  let index = 0;
  state.statusTimer = window.setInterval(() => {
    refs.status.textContent = message.slice(0, index);
    index += 1;
    if (index > message.length) {
      clearInterval(state.statusTimer);
      state.statusTimer = null;
    }
  }, 12);
}

function showToast(message, tone = "info") {
  const colorMap = {
    info: "#85f0ff",
    success: "#9af7be",
    warn: "#ffd17f",
    error: "#ff8fa4",
  };

  refs.toast.textContent = message;
  refs.toast.style.color = colorMap[tone] || "#eef3fb";
  refs.toast.classList.remove("hidden");
  refs.toast.classList.add("visible");

  if (state.toastTimer) {
    clearTimeout(state.toastTimer);
  }

  state.toastTimer = window.setTimeout(() => {
    refs.toast.classList.remove("visible");
  }, 2400);
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
  typeStatus("New round started. The number is hidden somewhere between 0 and 100.", "info");
  showToast("Fresh round ready.", "info");
  setBadge("Fresh Round", "info");
  updateStats();
  updateRange();
  renderHistory();
}

function showHint() {
  const midpoint = Math.floor((state.lowerBound + state.upperBound) / 2);
  typeStatus(
    `Try working near ${midpoint}. Current range: ${state.lowerBound} to ${state.upperBound}.`,
    "info",
  );
  setBadge("Hint Active", "info");
}

function launchConfetti() {
  refs.confetti.innerHTML = "";
  const colors = ["#85f0ff", "#78a6ff", "#9af7be", "#ffd17f", "#ffffff"];

  for (let index = 0; index < 42; index += 1) {
    const piece = document.createElement("span");
    piece.className = "confetti";
    piece.style.left = `${randomNumber(4, 96)}vw`;
    piece.style.background = colors[randomNumber(0, colors.length - 1)];
    piece.style.animationDuration = `${randomNumber(1800, 3200)}ms`;
    piece.style.animationDelay = `${randomNumber(0, 240)}ms`;
    piece.style.setProperty("--drift", `${randomNumber(-160, 160)}px`);
    refs.confetti.appendChild(piece);
  }

  window.setTimeout(() => {
    refs.confetti.innerHTML = "";
  }, 3500);
}

function handleGuess(event) {
  event.preventDefault();

  if (state.solved) {
    typeStatus("This round is solved. Start a new round to keep playing.", "success");
    return;
  }

  const raw = refs.input.value.trim();
  const guess = Number(raw);

  if (!raw || !Number.isInteger(guess) || guess < 0 || guess > 100) {
    typeStatus("Enter a whole number between 0 and 100.", "error");
    showToast("Whole numbers only, from 0 to 100.", "error");
    setBadge("Invalid Input", "error");
    return;
  }

  if (state.guesses.includes(guess)) {
    typeStatus(`You already tried ${guess}. Pick a new number.`, "warn");
    showToast("Try a fresh number.", "warn");
    setBadge("Repeated Guess", "warn");
    return;
  }

  state.guesses.push(guess);

  if (guess < state.target) {
    state.lowerBound = Math.max(state.lowerBound, guess + 1);
    typeStatus(`${guess} is low. Move higher. ${proximityText(guess)}`, "info");
    setBadge("Go Higher", "info");
  } else if (guess > state.target) {
    state.upperBound = Math.min(state.upperBound, guess - 1);
    typeStatus(`${guess} is high. Pull lower. ${proximityText(guess)}`, "info");
    setBadge("Go Lower", "info");
  } else {
    state.solved = true;
    state.roundsWon += 1;
    if (state.bestScore === null || state.guesses.length < state.bestScore) {
      state.bestScore = state.guesses.length;
    }
    typeStatus(`Locked in. You found ${state.target} in ${state.guesses.length} attempts.`, "success");
    showToast("Round solved beautifully.", "success");
    setBadge("Solved", "success");
    launchConfetti();
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
refs.newRoundTop.addEventListener("click", startNewRound);

startNewRound();
