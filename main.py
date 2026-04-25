import math
import random
import tkinter as tk


class GuessTheNumberApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Guess The Number | Premium Edition")
        self.root.geometry("1180x760")
        self.root.minsize(980, 680)
        self.root.configure(bg="#08111F")

        self.palette = {
            "bg": "#08111F",
            "panel": "#0F1B2D",
            "card": "#12243A",
            "card_alt": "#162B46",
            "line": "#27415E",
            "soft_text": "#8CA4C2",
            "text": "#F5F7FB",
            "accent": "#71E5FF",
            "accent_2": "#5B8CFF",
            "success": "#8EF0B6",
            "warning": "#FFCE73",
            "danger": "#FF7F96",
            "chip": "#0B1728",
        }

        self.best_score = None
        self.games_won = 0
        self.guesses = []
        self.target = 0
        self.lower_bound = 0
        self.upper_bound = 100
        self.status_animation = None
        self.particles = []

        self.background = tk.Canvas(
            self.root,
            bg=self.palette["bg"],
            highlightthickness=0,
            bd=0,
        )
        self.background.pack(fill="both", expand=True)
        self.background.bind("<Configure>", self.draw_background)

        self.main_frame = tk.Frame(self.background, bg=self.palette["bg"])
        self.window_id = self.background.create_window(
            0, 0, anchor="nw", window=self.main_frame
        )
        self.background.bind("<Configure>", self.position_main_frame, add="+")

        self.build_ui()
        self.start_new_round(announce=False)
        self.animate_status("A new round is ready. Take your first guess.", "info")

    def draw_background(self, event=None) -> None:
        width = max(self.root.winfo_width(), 1)
        height = max(self.root.winfo_height(), 1)
        self.background.delete("bg")

        steps = 14
        top = (8, 17, 31)
        bottom = (16, 34, 54)
        for index in range(steps):
            t = index / max(steps - 1, 1)
            color = self.mix_color(top, bottom, t)
            y1 = int(height * index / steps)
            y2 = int(height * (index + 1) / steps)
            self.background.create_rectangle(
                0, y1, width, y2, fill=color, outline="", tags="bg"
            )

        glows = [
            (width * 0.14, height * 0.12, 350, "#143C73"),
            (width * 0.82, height * 0.18, 280, "#0E7EA2"),
            (width * 0.72, height * 0.78, 420, "#17325C"),
        ]
        for cx, cy, radius, color in glows:
            for ring in range(5, 0, -1):
                alpha = ring / 5
                fill = self.mix_hex(color, self.palette["bg"], 1 - alpha * 0.25)
                size = radius * ring / 5
                self.background.create_oval(
                    cx - size,
                    cy - size,
                    cx + size,
                    cy + size,
                    fill=fill,
                    outline="",
                    tags="bg",
                )

    def position_main_frame(self, event=None) -> None:
        padding_x = max((self.root.winfo_width() - 1040) // 2, 36)
        padding_y = max((self.root.winfo_height() - 630) // 2, 30)
        self.background.coords(self.window_id, padding_x, padding_y)

    def build_ui(self) -> None:
        self.main_frame.grid_columnconfigure(0, weight=4)
        self.main_frame.grid_columnconfigure(1, weight=2)

        self.hero_card = self.make_card(self.main_frame, width=700, height=610)
        self.hero_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.side_card = self.make_card(self.main_frame, width=320, height=610)
        self.side_card.grid(row=0, column=1, sticky="nsew")

        self.build_hero()
        self.build_sidebar()

    def make_card(self, parent: tk.Widget, width: int, height: int) -> tk.Frame:
        shell = tk.Frame(parent, bg=self.palette["line"], padx=1, pady=1)
        card = tk.Frame(shell, bg=self.palette["panel"], width=width, height=height)
        card.pack(fill="both", expand=True)
        card.pack_propagate(False)
        return shell

    def build_hero(self) -> None:
        card = self.hero_card.winfo_children()[0]
        card.grid_columnconfigure(0, weight=1)

        masthead = tk.Frame(card, bg=self.palette["panel"])
        masthead.pack(fill="x", padx=28, pady=(28, 18))

        tk.Label(
            masthead,
            text="Guess The Number",
            fg=self.palette["text"],
            bg=self.palette["panel"],
            font=("Segoe UI Semibold", 28),
        ).pack(anchor="w")
        tk.Label(
            masthead,
            text="A polished, high-feedback guessing experience tuned for speed and clarity.",
            fg=self.palette["soft_text"],
            bg=self.palette["panel"],
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(6, 0))

        self.stats_row = tk.Frame(card, bg=self.palette["panel"])
        self.stats_row.pack(fill="x", padx=28, pady=(0, 18))
        for column in range(3):
            self.stats_row.grid_columnconfigure(column, weight=1)

        self.score_value = self.create_stat_tile(
            self.stats_row, "Best Score", "-", 0, self.palette["accent"]
        )
        self.rounds_value = self.create_stat_tile(
            self.stats_row, "Rounds Won", "0", 1, self.palette["success"]
        )
        self.attempts_value = self.create_stat_tile(
            self.stats_row, "Current Attempts", "0", 2, self.palette["warning"]
        )

        play_area = tk.Frame(card, bg=self.palette["panel"])
        play_area.pack(fill="both", expand=True, padx=28, pady=(0, 28))

        glass = tk.Frame(play_area, bg=self.palette["card"], padx=24, pady=24)
        glass.pack(fill="both", expand=True)

        tk.Label(
            glass,
            text="Find the hidden number between 0 and 100",
            fg=self.palette["text"],
            bg=self.palette["card"],
            font=("Segoe UI Semibold", 16),
        ).pack(anchor="w")

        self.status_label = tk.Label(
            glass,
            text="",
            fg=self.palette["accent"],
            bg=self.palette["card"],
            font=("Segoe UI", 12),
            wraplength=560,
            justify="left",
        )
        self.status_label.pack(anchor="w", pady=(10, 22))

        self.range_canvas = tk.Canvas(
            glass,
            height=88,
            bg=self.palette["card"],
            highlightthickness=0,
            bd=0,
        )
        self.range_canvas.pack(fill="x")
        self.range_canvas.bind("<Configure>", lambda _: self.draw_range_meter())

        input_row = tk.Frame(glass, bg=self.palette["card"])
        input_row.pack(fill="x", pady=(20, 14))
        input_row.grid_columnconfigure(0, weight=1)

        self.entry_shell = tk.Frame(
            input_row, bg=self.palette["line"], padx=1, pady=1
        )
        self.entry_shell.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self.guess_var = tk.StringVar()
        self.guess_entry = tk.Entry(
            self.entry_shell,
            textvariable=self.guess_var,
            bg=self.palette["chip"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 18),
            justify="center",
        )
        self.guess_entry.pack(fill="x", ipady=16, padx=16)
        self.guess_entry.bind("<Return>", self.submit_guess)
        self.guess_entry.bind("<FocusIn>", lambda _: self.set_entry_highlight(True))
        self.guess_entry.bind("<FocusOut>", lambda _: self.set_entry_highlight(False))

        self.guess_button = self.make_button(
            input_row,
            text="Submit Guess",
            command=self.submit_guess,
            fill=self.palette["accent_2"],
            hover="#769EFF",
        )
        self.guess_button.grid(row=0, column=1, sticky="ew")

        actions = tk.Frame(glass, bg=self.palette["card"])
        actions.pack(fill="x")
        for column in range(2):
            actions.grid_columnconfigure(column, weight=1)

        self.new_round_button = self.make_button(
            actions,
            text="New Round",
            command=self.start_new_round,
            fill="#18324F",
            hover="#24496F",
        )
        self.new_round_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.hint_button = self.make_button(
            actions,
            text="Smart Hint",
            command=self.show_smart_hint,
            fill="#173440",
            hover="#225264",
        )
        self.hint_button.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        tk.Label(
            glass,
            text="Press Enter to submit instantly. Smart hints adapt to how close your last guess was.",
            fg=self.palette["soft_text"],
            bg=self.palette["card"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(16, 0))

    def build_sidebar(self) -> None:
        card = self.side_card.winfo_children()[0]

        heading = tk.Frame(card, bg=self.palette["panel"])
        heading.pack(fill="x", padx=24, pady=(24, 18))

        tk.Label(
            heading,
            text="Live Session",
            fg=self.palette["text"],
            bg=self.palette["panel"],
            font=("Segoe UI Semibold", 20),
        ).pack(anchor="w")
        tk.Label(
            heading,
            text="Every guess sharpens the range and updates your trail in real time.",
            fg=self.palette["soft_text"],
            bg=self.palette["panel"],
            wraplength=250,
            justify="left",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(6, 0))

        self.badge = tk.Label(
            card,
            text="Ready",
            fg=self.palette["accent"],
            bg=self.palette["chip"],
            font=("Segoe UI Semibold", 11),
            padx=14,
            pady=9,
        )
        self.badge.pack(anchor="w", padx=24)

        history_shell = tk.Frame(card, bg=self.palette["line"], padx=1, pady=1)
        history_shell.pack(fill="both", expand=True, padx=24, pady=(18, 18))
        history_card = tk.Frame(history_shell, bg=self.palette["card_alt"])
        history_card.pack(fill="both", expand=True)

        tk.Label(
            history_card,
            text="Guess History",
            fg=self.palette["text"],
            bg=self.palette["card_alt"],
            font=("Segoe UI Semibold", 14),
        ).pack(anchor="w", padx=18, pady=(18, 6))

        self.history_frame = tk.Frame(history_card, bg=self.palette["card_alt"])
        self.history_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.history_placeholder = tk.Label(
            self.history_frame,
            text="Your guesses will appear here with proximity feedback.",
            fg=self.palette["soft_text"],
            bg=self.palette["card_alt"],
            wraplength=240,
            justify="left",
            font=("Segoe UI", 10),
        )
        self.history_placeholder.pack(anchor="w")

    def create_stat_tile(
        self, parent: tk.Widget, title: str, initial: str, column: int, accent: str
    ) -> tk.Label:
        shell = tk.Frame(parent, bg=self.palette["line"], padx=1, pady=1)
        shell.grid(row=0, column=column, sticky="nsew", padx=(0, 12) if column < 2 else 0)
        frame = tk.Frame(shell, bg=self.palette["card"], padx=16, pady=14)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text=title,
            fg=self.palette["soft_text"],
            bg=self.palette["card"],
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        value = tk.Label(
            frame,
            text=initial,
            fg=self.palette["text"],
            bg=self.palette["card"],
            font=("Segoe UI Semibold", 22),
        )
        value.pack(anchor="w", pady=(8, 0))

        tk.Frame(frame, bg=accent, height=3).pack(fill="x", pady=(14, 0))
        return value

    def make_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        fill: str,
        hover: str,
    ) -> tk.Label:
        button = tk.Label(
            parent,
            text=text,
            fg=self.palette["text"],
            bg=fill,
            font=("Segoe UI Semibold", 11),
            padx=18,
            pady=15,
            cursor="hand2",
        )
        button.bind("<Button-1>", lambda _: command())
        button.bind("<Enter>", lambda _: button.configure(bg=hover))
        button.bind("<Leave>", lambda _: button.configure(bg=fill))
        return button

    def set_entry_highlight(self, active: bool) -> None:
        self.entry_shell.configure(
            bg=self.palette["accent"] if active else self.palette["line"]
        )

    def start_new_round(self, announce: bool = True) -> None:
        self.target = random.randint(0, 100)
        self.guesses = []
        self.lower_bound = 0
        self.upper_bound = 100
        self.guess_var.set("")
        self.attempts_value.configure(text="0")
        self.badge.configure(text="Fresh Round", fg=self.palette["accent"])
        self.refresh_history()
        self.update_stats()
        self.draw_range_meter()
        self.guess_entry.focus_set()

        if announce:
            self.animate_status(
                "New round started. The number is hidden somewhere between 0 and 100.",
                "info",
            )

    def submit_guess(self, event=None) -> None:
        raw_value = self.guess_var.get().strip()
        if not raw_value:
            self.animate_status("Type a number first so I can evaluate your guess.", "warn")
            self.badge.configure(text="Waiting For Input", fg=self.palette["warning"])
            return

        if not raw_value.lstrip("-").isdigit():
            self.animate_status("Only whole numbers work here. Try a value from 0 to 100.", "error")
            self.badge.configure(text="Invalid Input", fg=self.palette["danger"])
            return

        guess = int(raw_value)
        if guess < 0 or guess > 100:
            self.animate_status("Stay inside the game range. Pick a number between 0 and 100.", "warn")
            self.badge.configure(text="Out Of Range", fg=self.palette["warning"])
            return

        if guess in self.guesses:
            self.animate_status(
                f"You already tried {guess}. Push into a new part of the range instead.",
                "warn",
            )
            self.badge.configure(text="Repeated Guess", fg=self.palette["warning"])
            return

        self.guesses.append(guess)
        self.guess_var.set("")
        self.attempts_value.configure(text=str(len(self.guesses)))

        proximity = self.proximity_text(guess)
        if guess < self.target:
            self.lower_bound = max(self.lower_bound, guess + 1)
            message = f"{guess} is low. Move higher. {proximity}"
            state = "info"
            badge = ("Go Higher", self.palette["accent"])
        elif guess > self.target:
            self.upper_bound = min(self.upper_bound, guess - 1)
            message = f"{guess} is high. Pull lower. {proximity}"
            state = "info"
            badge = ("Go Lower", self.palette["accent"])
        else:
            self.games_won += 1
            if self.best_score is None or len(self.guesses) < self.best_score:
                self.best_score = len(self.guesses)

            win_line = "First-try hit. That was elite." if len(self.guesses) == 1 else (
                f"Locked in. You found {self.target} in {len(self.guesses)} attempts."
            )
            self.animate_status(win_line, "success")
            self.badge.configure(text="Solved", fg=self.palette["success"])
            self.refresh_history()
            self.update_stats()
            self.draw_range_meter()
            self.launch_confetti()
            return

        self.badge.configure(text=badge[0], fg=badge[1])
        self.animate_status(message, state)
        self.refresh_history()
        self.update_stats()
        self.draw_range_meter()

    def show_smart_hint(self) -> None:
        if not self.guesses:
            self.animate_status(
                f"Open with confidence somewhere near the center. Your live range is {self.lower_bound} to {self.upper_bound}.",
                "info",
            )
            self.badge.configure(text="Center Bias Hint", fg=self.palette["accent"])
            return

        midpoint = (self.lower_bound + self.upper_bound) // 2
        spread = self.upper_bound - self.lower_bound
        if spread <= 8:
            hint = f"The answer is cornered now. Focus between {self.lower_bound} and {self.upper_bound}."
        else:
            hint = f"The range is tightening. The midpoint is {midpoint}, with room from {self.lower_bound} to {self.upper_bound}."

        self.animate_status(hint, "info")
        self.badge.configure(text="Smart Hint Active", fg=self.palette["accent"])

    def proximity_text(self, guess: int) -> str:
        distance = abs(self.target - guess)
        if distance == 0:
            return "Perfect."
        if distance <= 3:
            return "You are extremely close."
        if distance <= 7:
            return "Very warm."
        if distance <= 15:
            return "Getting close."
        if distance <= 25:
            return "Still in reach."
        return "Way off right now."

    def refresh_history(self) -> None:
        for child in self.history_frame.winfo_children():
            child.destroy()

        if not self.guesses:
            self.history_placeholder = tk.Label(
                self.history_frame,
                text="Your guesses will appear here with proximity feedback.",
                fg=self.palette["soft_text"],
                bg=self.palette["card_alt"],
                wraplength=240,
                justify="left",
                font=("Segoe UI", 10),
            )
            self.history_placeholder.pack(anchor="w")
            return

        for guess in reversed(self.guesses[-10:]):
            if guess < self.target:
                arrow = "Higher"
                tone = self.palette["accent"]
            elif guess > self.target:
                arrow = "Lower"
                tone = self.palette["warning"]
            else:
                arrow = "Correct"
                tone = self.palette["success"]

            item = tk.Frame(self.history_frame, bg=self.palette["chip"], padx=12, pady=10)
            item.pack(fill="x", pady=(0, 8))

            tk.Label(
                item,
                text=f"{guess}",
                fg=self.palette["text"],
                bg=self.palette["chip"],
                font=("Segoe UI Semibold", 13),
            ).pack(anchor="w")
            tk.Label(
                item,
                text=f"{arrow} | {self.proximity_text(guess)}",
                fg=tone,
                bg=self.palette["chip"],
                font=("Segoe UI", 10),
                wraplength=220,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))

    def update_stats(self) -> None:
        self.score_value.configure(text="-" if self.best_score is None else str(self.best_score))
        self.rounds_value.configure(text=str(self.games_won))
        self.attempts_value.configure(text=str(len(self.guesses)))

    def draw_range_meter(self) -> None:
        self.range_canvas.delete("all")
        width = max(self.range_canvas.winfo_width(), 560)
        self.range_canvas.create_text(
            0,
            4,
            anchor="nw",
            text="Live Range",
            fill=self.palette["soft_text"],
            font=("Segoe UI", 10),
        )

        x1, x2 = 18, width - 18
        y = 50
        self.range_canvas.create_line(
            x1, y, x2, y, fill=self.palette["line"], width=12, capstyle="round"
        )

        left = x1 + (x2 - x1) * (self.lower_bound / 100)
        right = x1 + (x2 - x1) * (self.upper_bound / 100)
        self.range_canvas.create_line(
            left,
            y,
            right,
            y,
            fill=self.palette["accent"],
            width=12,
            capstyle="round",
        )

        for marker in (0, 25, 50, 75, 100):
            x = x1 + (x2 - x1) * (marker / 100)
            self.range_canvas.create_text(
                x,
                y + 24,
                text=str(marker),
                fill=self.palette["soft_text"],
                font=("Segoe UI", 9),
            )

        self.range_canvas.create_text(
            left,
            y - 24,
            text=str(self.lower_bound),
            fill=self.palette["accent"],
            font=("Segoe UI Semibold", 10),
        )
        self.range_canvas.create_text(
            right,
            y - 24,
            text=str(self.upper_bound),
            fill=self.palette["accent"],
            font=("Segoe UI Semibold", 10),
        )

        if self.guesses:
            guess = self.guesses[-1]
            x = x1 + (x2 - x1) * (guess / 100)
            self.range_canvas.create_oval(
                x - 8, y - 8, x + 8, y + 8, fill=self.palette["text"], outline=""
            )
            self.range_canvas.create_text(
                x,
                y - 28,
                text=f"Last: {guess}",
                fill=self.palette["text"],
                font=("Segoe UI", 9),
            )

    def animate_status(self, message: str, tone: str) -> None:
        tone_map = {
            "info": self.palette["accent"],
            "success": self.palette["success"],
            "warn": self.palette["warning"],
            "error": self.palette["danger"],
        }
        final_color = tone_map.get(tone, self.palette["accent"])
        self.status_label.configure(fg=final_color, text="")

        if self.status_animation is not None:
            self.root.after_cancel(self.status_animation)
            self.status_animation = None

        def reveal(index: int = 0) -> None:
            self.status_label.configure(text=message[:index])
            if index <= len(message):
                self.status_animation = self.root.after(14, reveal, index + 1)
            else:
                self.status_animation = None
                self.pulse_label(self.status_label, final_color)

        reveal()

    def pulse_label(self, label: tk.Label, base_color: str) -> None:
        bright = self.mix_hex(base_color, "#FFFFFF", 0.35)
        sequence = [bright, base_color, bright, base_color]

        def step(index: int = 0) -> None:
            if index >= len(sequence):
                return
            label.configure(fg=sequence[index])
            self.root.after(85, step, index + 1)

        step()

    def launch_confetti(self) -> None:
        self.particles = []
        width = max(self.root.winfo_width(), 1000)
        colors = [
            self.palette["accent"],
            self.palette["success"],
            self.palette["warning"],
            "#FFFFFF",
        ]
        for _ in range(36):
            self.particles.append(
                {
                    "x": random.randint(120, width - 120),
                    "y": random.randint(-140, -10),
                    "size": random.randint(6, 12),
                    "vy": random.uniform(2.4, 5.6),
                    "vx": random.uniform(-1.6, 1.6),
                    "spin": random.uniform(-0.25, 0.25),
                    "angle": random.uniform(0, math.pi * 2),
                    "color": random.choice(colors),
                }
            )
        self.animate_confetti(0)

    def animate_confetti(self, frame: int) -> None:
        self.background.delete("fx")
        if frame > 45:
            return

        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["angle"] += particle["spin"]
            size = particle["size"]
            wobble = math.sin(particle["angle"]) * size
            self.background.create_oval(
                particle["x"] - size,
                particle["y"] - size / 2 + wobble * 0.15,
                particle["x"] + size,
                particle["y"] + size / 2 + wobble * 0.15,
                fill=particle["color"],
                outline="",
                tags="fx",
            )

        self.root.after(22, self.animate_confetti, frame + 1)

    @staticmethod
    def mix_color(start: tuple[int, int, int], end: tuple[int, int, int], t: float) -> str:
        red = int(start[0] + (end[0] - start[0]) * t)
        green = int(start[1] + (end[1] - start[1]) * t)
        blue = int(start[2] + (end[2] - start[2]) * t)
        return f"#{red:02x}{green:02x}{blue:02x}"

    def mix_hex(self, first: str, second: str, t: float) -> str:
        first_rgb = tuple(int(first[i : i + 2], 16) for i in (1, 3, 5))
        second_rgb = tuple(int(second[i : i + 2], 16) for i in (1, 3, 5))
        return self.mix_color(first_rgb, second_rgb, t)


def main() -> None:
    root = tk.Tk()
    app = GuessTheNumberApp(root)
    app.draw_range_meter()
    root.mainloop()


if __name__ == "__main__":
    main()
