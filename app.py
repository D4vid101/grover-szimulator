"""Tkinter interface for the Grover search demonstration."""

import math
import random
import tkinter as tk
from tkinter import ttk

from grover import optimal_iterations, simulate


PAPER = "#e9eef4"
SHEET = "#fffcf8"
INK = "#1b2430"
FAINT = "#5b6776"
NAVY = "#2c5289"
BRICK = "#c23a2b"
OCHRE = "#c3922a"
GOOD = "#1d7a58"
RULE = "#d5dde6"

COPY = {
    "initial": (
        "Egyenletes szuperpozíció",
        "Hadamardok után minden bázisállapot ugyanarról az 1/√N amplitúdóról indul. A cél esélye még csak 1/N.",
    ),
    "oracle": (
        "Orákulum",
        "A megjelölt amplitúdó előjelet vált. A mérési valószínűségek nem változnak, csak a fázis.",
    ),
    "diffusion": (
        "Diffúzió",
        "A diffúzió a kezdőállapot irányára tükröz. Az orákulummal együtt 2θ-val forgatja az állapotot; a cél esélye csökkenhet is.",
    ),
}


class GroverApp:
    def __init__(self, root):
        self.root = root
        root.title("Grover-szimulátor")
        root.geometry("1180x760")
        root.minsize(800, 640)
        root.configure(bg=PAPER)
        self.qubits = tk.StringVar(value="2")
        self.target = tk.StringVar(value="2")
        self.iterations = tk.StringVar(value="1")
        self.status = tk.StringVar()
        self.measure_text = tk.StringVar()
        self.position = 0
        self.history = []
        self.sample = None
        self.playing = None

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TButton", padding=(10, 5), background=SHEET)
        style.configure("Accent.TButton", background=NAVY, foreground="#f7f9fc")
        style.map("Accent.TButton", background=[("active", "#1e3b66")])

        header = tk.Frame(root, bg=PAPER, padx=22, pady=12)
        header.pack(fill="x")
        tk.Label(
            header, text="Grover-szimulátor", fg=INK, bg=PAPER, anchor="center",
            font=("Noto Serif", 34, "bold"),
        ).pack(fill="x")

        inputs = tk.Frame(root, bg=PAPER, padx=22)
        inputs.pack(fill="x")
        for title, variable, minimum, maximum in (
            ("Qubitek, n", self.qubits, 1, 8),
            ("Célindex", self.target, 0, 255),
            ("Iterációk, k", self.iterations, 0, 40),
        ):
            field = tk.Frame(inputs, bg=PAPER)
            field.pack(side="left", padx=(0, 12))
            self.label(field, title).pack(anchor="w")
            ttk.Spinbox(field, from_=minimum, to=maximum, textvariable=variable, width=7).pack()
        ttk.Button(inputs, text="k ≈ π√N / 4", command=self.suggest).pack(side="left", padx=(0, 8), anchor="s")
        ttk.Button(inputs, text="Indítás", style="Accent.TButton", command=self.run).pack(side="left", padx=(0, 8), anchor="s")
        ttk.Button(inputs, text="Mérés", command=self.measure).pack(side="left", anchor="s")
        tk.Label(root, textvariable=self.status, bg=PAPER, fg=BRICK, anchor="w", padx=22).pack(fill="x")

        nav = tk.Frame(root, bg=PAPER, padx=22)
        nav.pack(fill="x", pady=(2, 8))
        self.back = ttk.Button(nav, text="← Előző", command=lambda: self.step(-1))
        self.next = ttk.Button(nav, text="Következő →", command=lambda: self.step(1))
        self.play = ttk.Button(nav, text="Lejátszás", command=self.toggle_play)
        self.back.pack(side="left", padx=(0, 8))
        self.next.pack(side="left", padx=(0, 8))
        self.play.pack(side="left", padx=(0, 14))
        self.step_title = self.label(nav, "", INK, 12, True)
        self.step_title.pack(side="left")
        self.metrics = self.label(nav, "", NAVY, 10, True)
        self.metrics.pack(side="right")

        plots = tk.Frame(root, bg=PAPER, padx=22)
        plots.pack(fill="both", expand=True)
        plots.columnconfigure(0, weight=3, uniform="plot")
        plots.columnconfigure(1, weight=2, uniform="plot")
        plots.rowconfigure(0, weight=1)
        self.bars = tk.Canvas(plots, bg=SHEET, highlightthickness=1, highlightbackground=INK)
        self.plane = tk.Canvas(plots, bg=SHEET, highlightthickness=1, highlightbackground=INK)
        self.bars.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.plane.grid(row=0, column=1, sticky="nsew")
        for canvas in (self.bars, self.plane):
            canvas.bind("<Configure>", lambda event: self.draw())

        foot = tk.Frame(root, bg=PAPER, padx=22, pady=8)
        foot.pack(fill="x")
        self.explanation = self.label(foot, "", INK, 10)
        self.explanation.pack(fill="x")
        self.side = self.label(foot, "", FAINT, 9)
        self.side.pack(fill="x")
        tk.Label(foot, textvariable=self.measure_text, bg=PAPER, fg=BRICK, anchor="w").pack(fill="x")

        root.bind("<Left>", lambda event: self.arrow(event, -1))
        root.bind("<Right>", lambda event: self.arrow(event, 1))
        root.bind("<space>", lambda event: self.space(event))
        self.run()

    def ket(self, index):
        qubits = (len(self.history[0].amplitudes) - 1).bit_length()
        return f"|{index:0{qubits}b}⟩"

    @staticmethod
    def label(parent, text, color=FAINT, size=10, bold=False):
        return tk.Label(
            parent,
            text=text,
            fg=color,
            bg=PAPER,
            anchor="w",
            font=("Noto Sans", size, "bold" if bold else "normal"),
        )

    def suggest(self):
        try:
            qubits = int(self.qubits.get())
            if not 1 <= qubits <= 8:
                raise ValueError
        except ValueError:
            self.status.set("Az ajánláshoz n legyen 1 és 8 közötti egész.")
            return
        self.iterations.set(str(optimal_iterations(1 << qubits)))
        self.status.set("")

    def run(self):
        self.stop_play()
        try:
            qubits, target, iterations = (
                int(value.get()) for value in (self.qubits, self.target, self.iterations)
            )
        except ValueError:
            self.status.set("Mindhárom mezőbe egész számot írj.")
            return
        try:
            history = simulate(qubits, target, iterations)
        except ValueError as error:
            self.status.set(str(error))
            return
        self.history = history
        self.position = 0
        self.sample = None
        self.status.set("")
        self.measure_text.set("")
        self.refresh()

    def arrow(self, event, delta):
        if event.widget.winfo_class() not in {"TSpinbox", "TEntry"}:
            self.stop_play()
            self.move(delta)

    def space(self, event):
        if event.widget.winfo_class() not in {"TSpinbox", "TEntry"}:
            self.toggle_play()

    def step(self, delta):
        self.stop_play()
        self.move(delta)

    def move(self, delta):
        nxt = max(0, min(self.position + delta, len(self.history) - 1))
        if nxt == self.position:
            if delta > 0:
                self.stop_play()
            return
        self.position = nxt
        self.sample = None
        self.measure_text.set("")
        self.refresh()

    def toggle_play(self):
        if self.playing:
            self.stop_play()
            return
        if self.position == len(self.history) - 1:
            self.position = -1
        self.play.config(text="Megállít")
        self.move(1)
        if self.position < len(self.history) - 1:
            self.playing = self.root.after(850, self._play_tick)
        else:
            self.stop_play()

    def _play_tick(self):
        self.playing = None
        if self.position >= len(self.history) - 1:
            self.stop_play()
            return
        self.move(1)
        if self.position < len(self.history) - 1:
            self.play.config(text="Megállít")
            self.playing = self.root.after(850, self._play_tick)
        else:
            self.stop_play()

    def stop_play(self):
        if self.playing:
            self.root.after_cancel(self.playing)
            self.playing = None
        self.play.config(text="Lejátszás")

    def measure(self):
        if not self.history:
            return
        self.stop_play()
        step = self.history[self.position]
        p_mark = step.probability
        draw = random.random()
        if draw < p_mark:
            outcome = step.target
            prob = p_mark
        else:
            unmarked = [i for i in range(len(step.amplitudes)) if i != step.target]
            slot = min(int((draw - p_mark) / ((1 - p_mark) / len(unmarked))), len(unmarked) - 1)
            outcome = unmarked[slot]
            prob = (1 - p_mark) / len(unmarked)
        self.sample = outcome
        self.measure_text.set(
            f"Mérés eredménye: {self.ket(outcome)}  (ehhez az állapothoz most P = {prob:.2%})."
        )
        self.draw()

    def refresh(self):
        step = self.history[self.position]
        name, description = COPY[step.operation]
        number = f" · {step.iteration}. kör" if step.iteration else ""
        self.step_title.config(text=f"{self.position + 1}/{len(self.history)}  {name}{number}")
        self.metrics.config(text=f"P({self.ket(step.target)}) = {step.probability:.2%}")
        self.explanation.config(text=description)
        rec = optimal_iterations(len(step.amplitudes))
        k = (len(self.history) - 1) // 2
        extra = f"θ = {math.degrees(math.asin(1 / math.sqrt(len(step.amplitudes)))):.2f}°  ·  ajánlott k = {rec}"
        if len(step.amplitudes) == 2:
            extra += "  ·  Egy qubitnél a cél esélye minden iteráció után 50%."
        elif k > rec:
            extra += "  ·  k nagyobb az ajánlottnál, a tetőzés után a valószínűség csökken."
        extra += f"  ·  átlag = {step.mean:.4f}"
        self.side.config(text=extra)
        self.back.state(["!disabled"] if self.position else ["disabled"])
        self.next.state(["!disabled"] if self.position < len(self.history) - 1 else ["disabled"])
        self.draw()

    def draw(self):
        if not self.history:
            return
        step = self.history[self.position]
        previous = self.history[self.position - 1] if self.position else None
        self.draw_bars(step, previous)
        self.draw_plane(step, previous)

    @staticmethod
    def plot_text(canvas, x, y, value, color=FAINT, anchor="center", size=9, bold=False):
        canvas.create_text(
            x, y, text=value, fill=color, anchor=anchor,
            font=("Noto Sans", size, "bold" if bold else "normal"),
        )

    def draw_bars(self, step, previous):
        canvas = self.bars
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if width < 100 or height < 100:
            return
        values = step.amplitudes
        left, right, top, bottom = 54, width - 16, 58, height - 48
        middle, scale = (top + bottom) / 2, (bottom - top) / 2
        self.plot_text(canvas, 16, 20, "Amplitúdók", INK, "w", 13, True)
        self.plot_text(
            canvas, 16, 40,
            f"N = {len(values)}   ·   piros: {self.ket(step.target)} (index {step.target})",
            BRICK, "w",
        )
        for tick in (-1, -0.5, 0, 0.5, 1):
            y = middle - scale * tick
            canvas.create_line(left, y, right, y, fill=INK if tick == 0 else RULE)
            self.plot_text(canvas, left - 7, y, f"{tick:g}", anchor="e")
        mean_y = middle - scale * step.mean
        canvas.create_line(left, mean_y, right, mean_y, fill=OCHRE, dash=(3, 4))
        cell = (right - left) / len(values)
        bar_width = max(1, min(cell * 0.60, 52))
        qubits = int(math.log2(len(values)))
        label_stride = max(1, math.ceil(32 / cell))
        for index, value in enumerate(values):
            x = left + (index + 0.5) * cell
            y = middle - scale * value
            faded = self.sample is not None and self.sample != index
            color = BRICK if index == step.target else NAVY
            canvas.create_rectangle(
                x - bar_width / 2, min(y, middle),
                x + bar_width / 2, max(y, middle),
                fill=color, outline="",
                stipple="gray50" if faded else "",
            )
            if previous:
                prior_y = middle - scale * previous.amplitudes[index]
                canvas.create_line(x - bar_width / 2, prior_y, x + bar_width / 2, prior_y, fill=INK)
            if index % label_stride == 0:
                label = f"|{index:0{qubits}b}⟩" if qubits <= 4 else str(index)
                self.plot_text(canvas, x, bottom + 14, label, size=8)
        footer = "Bázisállapot  ·  fekete vonás: előző  ·  pontozott: átlag"
        self.plot_text(canvas, (left + right) / 2, height - 12, footer)

    def draw_plane(self, step, previous):
        canvas = self.plane
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if width < 100 or height < 100:
            return
        self.plot_text(canvas, 16, 20, "Grover-sík", INK, "w", 13, True)
        self.plot_text(canvas, 16, 40, "x: |s′⟩   ·   y: |w⟩", FAINT, "w")
        radius = min((width - 72) / 2, (height - 120) / 2)
        cx, cy = width / 2, (height + 10) / 2
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=RULE, width=2)
        canvas.create_line(cx - radius - 7, cy, cx + radius + 7, cy, fill=FAINT, arrow="last")
        canvas.create_line(cx, cy + radius + 7, cx, cy - radius - 7, fill=FAINT, arrow="last")
        self.plot_text(canvas, cx + radius + 16, cy - 8, "|s′⟩")
        self.plot_text(canvas, cx + 11, cy - radius - 8, "|w⟩", BRICK)
        theta0 = math.asin(1 / math.sqrt(len(step.amplitudes)))
        canvas.create_line(
            cx, cy, cx + radius * math.cos(theta0), cy - radius * math.sin(theta0),
            fill=OCHRE, width=2, dash=(4, 3), arrow="last",
        )
        if previous:
            x, y = previous.coordinates
            canvas.create_line(cx, cy, cx + radius * x, cy - radius * y, fill=RULE, width=2, dash=(4, 3), arrow="last")
        x, y = step.coordinates
        canvas.create_line(cx, cy, cx + radius * x, cy - radius * y, fill=GOOD, width=3, arrow="last")
        deg = math.degrees(math.atan2(y, x))
        self.plot_text(
            canvas, cx, height - 32,
            f"x = {x:+.4f}   y = {y:+.4f}   ∠ = {deg:.1f}°",
            GOOD, size=10, bold=True,
        )
        self.plot_text(canvas, cx, height - 14, f"okker nyíl: kezdeti |s⟩, θ = {math.degrees(theta0):.1f}°")


if __name__ == "__main__":
    window = tk.Tk()
    GroverApp(window)
    window.mainloop()
