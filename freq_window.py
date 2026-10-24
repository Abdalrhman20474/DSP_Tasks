import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from frequency_domain import dominant_frequencies


class FrequencyWindow(tk.Toplevel):
    """Amplitude vs frequency, phase vs frequency, and the dominant-frequency table."""

    def __init__(self, master, spec, title="Frequency Domain"):
        super().__init__(master)
        self.title(title)
        self.geometry("1100x650")

        info = f"{spec.name}  |  N = {spec.n}  |  Fs = {spec.fs:g} Hz  |  resolution = {spec.fs / spec.n:g} Hz"
        ttk.Label(self, text=info, padding=8).pack(fill="x")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        fig = Figure(figsize=(7, 6), dpi=100)
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        freqs = spec.frequencies

        ax1.stem(freqs, spec.normalized_amplitudes)
        ax1.axhline(0.5, color="red", linestyle="--", linewidth=0.8)
        ax1.set_title("Normalized amplitude vs frequency")
        ax1.set_xlabel("Frequency (Hz)"); ax1.set_ylabel("Amplitude (0-1)")
        ax1.grid(True, alpha=0.3)

        ax2.stem(freqs, spec.phases)
        ax2.set_title("Phase vs frequency")
        ax2.set_xlabel("Frequency (Hz)"); ax2.set_ylabel("Phase (rad)")
        ax2.grid(True, alpha=0.3)

        fig.tight_layout()
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)
        canvas = FigureCanvasTkAgg(fig, master=left)
        NavigationToolbar2Tk(canvas, left).update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

        right = ttk.Frame(body)
        right.pack(side="right", fill="y")
        ttk.Label(right, text="Dominant frequencies (amplitude > 0.5)").pack(pady=(0, 4))
        cols = ("bin", "freq (Hz)", "amplitude", "phase")
        table = ttk.Treeview(right, columns=cols, show="headings", height=25)
        for c, w in zip(cols, (50, 90, 85, 85)):
            table.heading(c, text=c)
            table.column(c, width=w, anchor="center")
        table.pack(side="left", fill="y")
        for k, f, a, p in dominant_frequencies(spec):
            table.insert("", "end", values=(k, f"{f:.4g}", f"{a:.4f}", f"{p:.4f}"))