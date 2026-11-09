"""Tkinter interface for the Grover search demonstration."""

import math
import tkinter as tk
from tkinter import ttk

from grover import optimal_iterations, simulate


BG = "#0f172a"
PANEL = "#17243a"
GRID = "#33445f"
INK = "#f0f5ff"
MUTED = "#afc0d8"
BLUE = "#79abff"
GOLD = "#ffc775"
MINT = "#64e4bf"
PINK = "#ffa0a8"

OPERATIONS = {
    "initial": ("Szuperpozíció", "Minden bázisállapot azonos amplitúdóról indul."),
    "oracle": ("Orákulum", "A keresett állapot amplitúdója előjelet vált. A mérési valószínűségek változatlanok."),
    "diffusion": ("Diffúzió", "Minden amplitúdó tükröződik az orákulum utáni amplitúdók átlaga körül."),
}


class GroverApp:
    def __init__(self, root):
        self.root = root
        root.title("Grover-szimulátor")
        root.geometry("1120x720")
        root.minsize(760, 620)
        root.configure(bg=BG)
        self.qubits = tk.StringVar(value="2")
        self.target = tk.StringVar(value="2")
        self.iterations = tk.StringVar(value="1")
        self.status = tk.StringVar()
        self.position = 0
        self.history = []

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TButton", padding=(10, 5))
        style.configure("Accent.TButton", background="#236454", foreground="white")
        style.map("Accent.TButton", background=[("active", "#317c69")])

        header = tk.Frame(root, bg=BG, padx=22, pady=12)
        header.pack(fill="x")
        self.label(header, "KVANTUMINFORMATIKAI ALKALMAZÁSOK  /  3. FELADAT", MINT, 9, True).pack(anchor="w")
        self.label(header, "Grover-szimulátor", INK, 25, True).pack(anchor="w")
        self.label(header, "Kövesd ugyanazt a kvantumállapotot az amplitúdók és a geometria nézetében.").pack(anchor="w")

        inputs = tk.Frame(root, bg=BG, padx=22)
        inputs.pack(fill="x")
        for title, variable, minimum, maximum in (
            ("Qubitek", self.qubits, 1, 8),
            ("Célindex", self.target, 0, 255),
            ("Iterációk", self.iterations, 0, 40),
        ):
            field = tk.Frame(inputs, bg=BG)
            field.pack(side="left", padx=(0, 12))
            self.label(field, title).pack(anchor="w")
            ttk.Spinbox(field, from_=minimum, to=maximum, textvariable=variable, width=7).pack()
        ttk.Button(inputs, text="Ajánlott iteráció", command=self.suggest).pack(side="left", padx=(0, 8), anchor="s")
        ttk.Button(inputs, text="Új futás", style="Accent.TButton", command=self.run).pack(side="left", anchor="s")
        tk.Label(root, textvariable=self.status, bg=BG, fg=PINK, anchor="w", padx=22).pack(fill="x")

        nav = tk.Frame(root, bg=BG, padx=22)
        nav.pack(fill="x", pady=(2, 8))
        self.back = ttk.Button(nav, text="← Előző", command=lambda: self.move(-1))
        self.next = ttk.Button(nav, text="Következő →", command=lambda: self.move(1))
        self.back.pack(side="left", padx=(0, 8))
        self.next.pack(side="left", padx=(0, 14))
        self.step_title = self.label(nav, "", INK, 12, True)
        self.step_title.pack(side="left")
        self.metrics = self.label(nav, "", MINT, 10, True)
        self.metrics.pack(side="right")

        plots = tk.Frame(root, bg=BG, padx=22)
        plots.pack(fill="both", expand=True)
        plots.columnconfigure(0, weight=3, uniform="plot")
        plots.columnconfigure(1, weight=2, uniform="plot")
        plots.rowconfigure(0, weight=1)
        self.bars = tk.Canvas(plots, bg=PANEL, highlightthickness=0)
        self.plane = tk.Canvas(plots, bg=PANEL, highlightthickness=0)
        self.bars.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.plane.grid(row=0, column=1, sticky="nsew")
        for canvas in (self.bars, self.plane):
            canvas.bind("<Configure>", lambda event: self.draw())
        self.explanation = self.label(root, "", MUTED, 10)
        self.explanation.pack(fill="x", padx=22, pady=(10, 12))
        root.bind("<Left>", lambda event: self.arrow(event, -1))
        root.bind("<Right>", lambda event: self.arrow(event, 1))
        self.run()

    @staticmethod
    def label(parent, text, color=MUTED, size=10, bold=False):
        return tk.Label(parent, text=text, fg=color, bg=BG, anchor="w",
                        font=("Segoe UI", size, "bold" if bold else "normal"))

    def suggest(self):
        try:
            qubits = int(self.qubits.get())
            if not 1 <= qubits <= 8:
                raise ValueError
        except ValueError:
            self.status.set("Az ajánláshoz 1 és 8 közötti egész qubitszámot adj meg.")
            return
        self.iterations.set(str(optimal_iterations(1 << qubits)))
        self.status.set("")

    def run(self):
        try:
            qubits, target, iterations = (int(value.get()) for value in
                                          (self.qubits, self.target, self.iterations))
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
        self.status.set("")
        self.refresh()

    def arrow(self, event, delta):
        if event.widget.winfo_class() not in {"TSpinbox", "TEntry"}:
            self.move(delta)

    def move(self, delta):
        self.position = max(0, min(self.position + delta, len(self.history) - 1))
        self.refresh()

    def refresh(self):
        step = self.history[self.position]
        name, description = OPERATIONS[step.operation]
        number = f" · {step.iteration}. iteráció" if step.iteration else ""
        self.step_title.config(text=f"{self.position + 1}/{len(self.history)}  {name}{number}")
        self.metrics.config(text=f"P(cél) = {step.probability:.2%}")
        self.explanation.config(text=description)
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
    def plot_text(canvas, x, y, value, color=MUTED, anchor="center", size=9, bold=False):
        canvas.create_text(x, y, text=value, fill=color, anchor=anchor,
                           font=("Segoe UI", size, "bold" if bold else "normal"))

    def draw_bars(self, step, previous):
        canvas = self.bars
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if width < 100 or height < 100:
            return
        values = step.amplitudes
        left, right, top, bottom = 51, width - 17, 66, height - 52
        middle, scale = (top + bottom) / 2, (bottom - top) / 2
        self.plot_text(canvas, 16, 23, "01   Valószínűségi amplitúdók", INK, "w", 13, True)
        self.plot_text(canvas, 16, 46, f"N = {len(values)}   ·   Arany: cél |{step.target}>", GOLD, "w")
        for tick in (-1, -.5, 0, .5, 1):
            y = middle - scale * tick
            canvas.create_line(left, y, right, y, fill=MUTED if tick == 0 else GRID)
            self.plot_text(canvas, left - 7, y, f"{tick:g}", anchor="e")
        cell = (right - left) / len(values)
        bar_width = max(1, min(cell * .60, 52))
        label_stride = max(1, math.ceil(26 / cell))
        for index, value in enumerate(values):
            x = left + (index + .5) * cell
            y = middle - scale * value
            color = GOLD if index == step.target else BLUE
            canvas.create_rectangle(x - bar_width / 2, min(y, middle),
                                    x + bar_width / 2, max(y, middle),
                                    fill=color, outline="")
            if previous:
                prior_y = middle - scale * previous.amplitudes[index]
                canvas.create_line(x - bar_width / 2, prior_y, x + bar_width / 2, prior_y, fill=INK)
            if index % label_stride == 0:
                self.plot_text(canvas, x, bottom + 13, str(index))
        footer = "Bázisállapot indexe"
        if previous:
            footer += "  ·  Fehér vonal: előző amplitúdó"
        self.plot_text(canvas, (left + right) / 2, height - 14, footer)

    def draw_plane(self, step, previous):
        canvas = self.plane
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if width < 100 or height < 100:
            return
        self.plot_text(canvas, 16, 23, "02   Geometriai nézet", INK, "w", 13, True)
        self.plot_text(canvas, 16, 46, "x: nem célállapotok   ·   y: célállapot", MUTED, "w")
        radius = min((width - 69) / 2, (height - 128) / 2)
        cx, cy = width / 2, (height + 8) / 2
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=GRID, width=2)
        canvas.create_line(cx - radius - 7, cy, cx + radius + 7, cy, fill=MUTED, arrow="last")
        canvas.create_line(cx, cy + radius + 7, cx, cy - radius - 7, fill=MUTED, arrow="last")
        self.plot_text(canvas, cx + radius + 16, cy - 8, "x")
        self.plot_text(canvas, cx + 11, cy - radius - 8, "y")
        if previous:
            x, y = previous.coordinates
            canvas.create_line(cx, cy, cx + radius * x, cy - radius * y,
                               fill=MUTED, width=2, dash=(4, 3), arrow="last")
        x, y = step.coordinates
        canvas.create_line(cx, cy, cx + radius * x, cy - radius * y, fill=MINT, width=3, arrow="last")
        self.plot_text(canvas, cx, height - 34, f"x = {x:+.4f}     y = {y:+.4f}", MINT, size=11, bold=True)
        if previous:
            self.plot_text(canvas, cx, height - 14, "Szaggatott nyíl: előző állapot")


if __name__ == "__main__":
    window = tk.Tk()
    GroverApp(window)
    window.mainloop()
