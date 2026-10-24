import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from frequency_domain import dominant_frequencies, reconstruct
from file_io import write_spectrum


class FrequencyWindow(tk.Toplevel):
    """Amplitude vs frequency, phase vs frequency, and the dominant-frequency table."""

    def __init__(self, master, spec, title="Frequency Domain"):
        super().__init__(master)
        self.master = master
        self.spec = spec
        self.title(title)
        self.geometry("1100x680")

        info = f"{spec.name}  |  N = {spec.n}  |  Fs = {spec.fs:g} Hz  |  resolution = {spec.fs / spec.n:g} Hz"
        ttk.Label(self, text=info, padding=8, font=("Segoe UI", 10, "bold")).pack(fill="x")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        fig = Figure(figsize=(7, 6), dpi=100)
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        freqs = spec.frequencies

        ax1.stem(freqs, spec.normalized_amplitudes)
        ax1.axhline(0.5, color="red", linestyle="--", linewidth=0.8, label="Dominant Threshold (0.5)")
        ax1.set_title("Normalized Amplitude vs Frequency")
        ax1.set_xlabel("Frequency (Hz)")
        ax1.set_ylabel("Amplitude (0-1)")
        ax1.legend(loc="upper right")
        ax1.grid(True, alpha=0.3)

        ax2.stem(freqs, spec.phases)
        ax2.set_title("Phase vs Frequency")
        ax2.set_xlabel("Frequency (Hz)")
        ax2.set_ylabel("Phase (rad)")
        ax2.grid(True, alpha=0.3)

        fig.tight_layout()
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)
        canvas = FigureCanvasTkAgg(fig, master=left)
        NavigationToolbar2Tk(canvas, left).update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

        right = ttk.Frame(body, padding=8)
        right.pack(side="right", fill="y")
        ttk.Label(right, text="Dominant Frequencies (amp > 0.5):", font=("Segoe UI", 9, "bold")).pack(pady=(0, 4))
        cols = ("bin", "freq (Hz)", "amplitude", "phase")
        table = ttk.Treeview(right, columns=cols, show="headings", height=20)
        for c, w in zip(cols, (50, 90, 85, 85)):
            table.heading(c, text=c)
            table.column(c, width=w, anchor="center")
        table.pack(side="top", fill="both", expand=True)
        for k, f, a, p in dominant_frequencies(spec):
            table.insert("", "end", values=(k, f"{f:.4g}", f"{a:.4f}", f"{p:.4f}"))

        # Bottom toolbar with actions
        btn_frame = ttk.Frame(right, padding=(0, 10, 0, 0))
        btn_frame.pack(side="bottom", fill="x")

        ttk.Button(btn_frame, text="Save Spectrum...", command=self._save_spectrum).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Reconstruct (IDFT)", command=self._reconstruct).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(fill="x", pady=2)

    def _save_spectrum(self):
        path = filedialog.asksaveasfilename(
            title="Save Spectrum",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            write_spectrum(path, self.spec)
            messagebox.showinfo("Saved", f"Spectrum saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _reconstruct(self):
        try:
            recon = reconstruct(self.spec)
            if hasattr(self.master, "_store"):
                stored = self.master._store(recon)
                if hasattr(self.master, "bottom_var"):
                    self.master.bottom_var.set(stored.name)
                if hasattr(self.master, "_redraw"):
                    self.master._redraw()
            messagebox.showinfo("IDFT", f"Reconstructed signal '{recon.name}' sent to main window!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
