import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from file_io import read_signal
from operations import add_signals, multiply_signal , subtract_signals , square_signal , normalize_signal , accumulate_signal
from quantization import quantize_signal
from quant_window import QuantWindow

from plotting import plot_signal, show_empty

from frequency_domain import (compute_spectrum, modify_component, remove_dc,
                              reconstruct, reconstruct_from_signal)
from freq_window import FrequencyWindow


NONE = "(none)"


class SignalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Signal Processing Framework")
        self.geometry("1000x720")
        self.signals = []                       # every loaded / computed Signal

        self.top_var = tk.StringVar(value=NONE)
        self.bottom_var = tk.StringVar(value=NONE)
        self.mode_var = tk.StringVar(value="both")
        self.spectrum = None          # the current spectrum
        self.spectrum_source = None   # the signal it came from

        self._build_menu()
        self._build_controls()
        self._build_plot()
        self._redraw()
        

    # ---------------- layout ----------------
    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Signal...", command=self.on_load)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        arith = tk.Menu(menubar, tearoff=0)
        arith.add_command(label="Addition", command=self.on_add)
        arith.add_command(label="Subtraction", command=self.on_subtract)
        arith.add_command(label="Multiplication", command=self.on_multiply)
        arith.add_command(label="Squaring", command=self.on_square)
        arith.add_command(label="Normalization", command=self.on_normalize)
        arith.add_command(label="Accumulation", command=self.on_accumulate)
        menubar.add_cascade(label="Arithmetic Operations", menu=arith)

        quant_menu = tk.Menu(menubar, tearoff=0)
        quant_menu.add_command(label="Quantize Signal...", command=self.on_quantize_window)
        menubar.add_cascade(label="Quantization", menu=quant_menu)

        freq = tk.Menu(menubar, tearoff=0)
        freq.add_command(label="Fourier Transform...", command=self.on_dft)
        freq.add_command(label="Dominant Frequencies", command=self.on_dominant)
        freq.add_command(label="Modify Components...", command=self.on_modify)
        freq.add_command(label="Remove DC Component", command=self.on_remove_dc)
        freq.add_command(label="Reconstruct (IDFT)", command=self.on_reconstruct)
        freq.add_command(label="Save Spectrum to File...", command=self.on_save_spectrum)
        menubar.add_cascade(label="Frequency Domain", menu=freq)

        self.config(menu=menubar)

    def _build_controls(self):
        bar = ttk.Frame(self, padding=8)
        bar.pack(fill="x")

        ttk.Label(bar, text="Top plot:").pack(side="left")
        self.top_box = ttk.Combobox(bar, textvariable=self.top_var,
                                    state="readonly", width=22)
        self.top_box.pack(side="left", padx=(4, 12))

        ttk.Label(bar, text="Bottom plot:").pack(side="left")
        self.bottom_box = ttk.Combobox(bar, textvariable=self.bottom_var,
                                       state="readonly", width=22)
        self.bottom_box.pack(side="left", padx=(4, 12))

        for text, value in (("Continuous", "continuous"),
                            ("Discrete", "discrete"),
                            ("Both", "both")):
            ttk.Radiobutton(bar, text=text, value=value, variable=self.mode_var,
                            command=self._redraw).pack(side="left", padx=2)

        ttk.Button(bar, text="Quantize Signal...", command=self.on_quantize_window).pack(side="right", padx=6)

        self.top_box.bind("<<ComboboxSelected>>", lambda e: self._redraw())
        self.bottom_box.bind("<<ComboboxSelected>>", lambda e: self._redraw())
        self._refresh_choices()

    def _build_plot(self):
      self.fig = Figure(figsize=(9, 6), dpi=100)
      self.ax_top = self.fig.add_subplot(2, 1, 1)
      self.ax_bottom = self.fig.add_subplot(2, 1, 2)
      self.canvas = FigureCanvasTkAgg(self.fig, master=self)
      toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
      toolbar.update()
      toolbar.pack(side="bottom", fill="x")
      self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    # ---------------- helpers ----------------
    def _unique_name(self, name):
        existing = {s.name for s in self.signals}
        if name not in existing:
            return name
        i = 2
        while f"{name} ({i})" in existing:
            i += 1
        return f"{name} ({i})"

    def _store(self, signal):
        signal.name = self._unique_name(signal.name)
        self.signals.append(signal)
        self._refresh_choices()
        return signal

    def _find(self, name):
        for s in self.signals:
            if s.name == name:
                return s
        return None

    def _refresh_choices(self):
        values = [NONE] + [s.name for s in self.signals]
        self.top_box["values"] = values
        self.bottom_box["values"] = values

    def _pick_signals(self, title, multiple=True):
        if not self.signals:
            messagebox.showinfo(title, "Load a signal first (File > Load Signal).")
            return []
        win = tk.Toplevel(self)
        win.title(title)
        win.transient(self)
        win.grab_set()
        ttk.Label(win, text="Select signal(s):").pack(padx=10, pady=(10, 0))
        lb = tk.Listbox(win, selectmode=tk.MULTIPLE if multiple else tk.SINGLE,
                        exportselection=False, width=40, height=10)
        for s in self.signals:
            lb.insert(tk.END, s.name)
        lb.pack(padx=10, pady=10)
        chosen = []

        def ok():
            chosen.extend(self.signals[i] for i in lb.curselection())
            win.destroy()

        ttk.Button(win, text="OK", command=ok).pack(pady=(0, 10))
        self.wait_window(win)
        return chosen

    def _redraw(self):
        mode = self.mode_var.get()
        for ax, var in ((self.ax_top, self.top_var), (self.ax_bottom, self.bottom_var)):
            ax.clear()
            sig = self._find(var.get())
            if sig is None:
                show_empty(ax)
            else:
                plot_signal(ax, sig, mode)
        self.fig.tight_layout()
        self.canvas.draw_idle()

    # ---------------- callbacks ----------------
    def on_load(self):
        paths = filedialog.askopenfilenames(
            title="Load signal", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        for path in paths:
            try:
                sig = self._store(read_signal(path))
            except Exception as e:
                messagebox.showerror("Could not read file", f"{path}\n\n{e}")
                continue
            if self.top_var.get() == NONE:
                self.top_var.set(sig.name)
            elif self.bottom_var.get() == NONE:
                self.bottom_var.set(sig.name)
        self._redraw()

    def on_add(self):
        chosen = self._pick_signals("Addition", multiple=True)
        if not chosen:
            return
        if len(chosen) < 2:
            messagebox.showwarning("Addition", "Select at least two signals.")
            return
        try:
            result = self._store(add_signals(chosen))
        except ValueError as e:
            messagebox.showerror("Addition", str(e))
            return
        self.top_var.set(chosen[0].name)
        self.bottom_var.set(result.name)
        self._redraw()

    def on_multiply(self):
        chosen = self._pick_signals("Multiplication", multiple=False)
        if not chosen:
            return
        k = simpledialog.askfloat("Multiplication", "Constant value:", parent=self)
        if k is None:
            return
        try:
            result = self._store(multiply_signal(chosen[0], k))
        except ValueError as e:
            messagebox.showerror("Multiplication", str(e))
            return
        self.top_var.set(chosen[0].name)
        self.bottom_var.set(result.name)
        self._redraw()

    def on_subtract(self):
        if len(self.signals) < 2:
            messagebox.showinfo("Subtraction", "Please load at least two signals first.")
            return

        win = tk.Toplevel(self)
        win.title("Subtract Signals (A - B)")
        win.transient(self)
        win.grab_set()

        ttk.Label(win, text="Signal A (Minuend):").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        a_var = tk.StringVar(value=self.signals[0].name)
        box_a = ttk.Combobox(win, textvariable=a_var, state="readonly", values=[s.name for s in self.signals], width=30)
        box_a.grid(row=0, column=1, padx=10, pady=8)

        ttk.Label(win, text="Signal B (Subtrahend):").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        b_var = tk.StringVar(value=self.signals[1].name if len(self.signals) > 1 else self.signals[0].name)
        box_b = ttk.Combobox(win, textvariable=b_var, state="readonly", values=[s.name for s in self.signals], width=30)
        box_b.grid(row=1, column=1, padx=10, pady=8)

        def ok():
            sig_a = self._find(a_var.get())
            sig_b = self._find(b_var.get())
            win.destroy()
            if not sig_a or not sig_b:
                return
            try:
                res = self._store(subtract_signals(sig_a, sig_b))
            except ValueError as e:
                messagebox.showerror("Subtraction", str(e))
                return
            self.top_var.set(sig_a.name)
            self.bottom_var.set(res.name)
            self._redraw()

        ttk.Button(win, text="Subtract (A - B)", command=ok).grid(row=2, column=0, columnspan=2, pady=12)
        self.wait_window(win)

    def on_square(self):
        chosen = self._pick_signals("Squaring", multiple=False)
        if not chosen:
            return
        try:
            result = self._store(square_signal(chosen[0]))
        except ValueError as e:
            messagebox.showerror("Squaring", str(e))
            return
        self.top_var.set(chosen[0].name)
        self.bottom_var.set(result.name)
        self._redraw()

    def on_normalize(self):
        chosen = self._pick_signals("Normalization", multiple=False)
        if not chosen:
            return
        win = tk.Toplevel(self)
        win.title("Select Normalization Range")
        win.transient(self)
        win.grab_set()

        mode_choice = tk.StringVar(value="0to1")
        ttk.Label(win, text="Choose normalization range:").pack(padx=15, pady=(10, 5))
        ttk.Radiobutton(win, text="Normalize from 0 to 1", value="0to1", variable=mode_choice).pack(anchor="w", padx=20, pady=2)
        ttk.Radiobutton(win, text="Normalize from -1 to 1", value="-1to1", variable=mode_choice).pack(anchor="w", padx=20, pady=2)

        def ok():
            m = mode_choice.get()
            win.destroy()
            try:
                result = self._store(normalize_signal(chosen[0], m))
            except ValueError as e:
                messagebox.showerror("Normalization", str(e))
                return
            self.top_var.set(chosen[0].name)
            self.bottom_var.set(result.name)
            self._redraw()

        ttk.Button(win, text="OK", command=ok).pack(pady=10)
        self.wait_window(win)

    def on_accumulate(self):
        chosen = self._pick_signals("Accumulation", multiple=False)
        if not chosen:
            return
        try:
            result = self._store(accumulate_signal(chosen[0]))
        except ValueError as e:
            messagebox.showerror("Accumulation", str(e))
            return
        self.top_var.set(chosen[0].name)
        self.bottom_var.set(result.name)
        self._redraw()

    def on_quantize_window(self):
        QuantWindow(self)



        # ---------------- Task 3 callbacks ----------------

        
    def _need_spectrum(self, title):
        if self.spectrum is None:
            messagebox.showinfo(title, "Run Frequency Domain > Fourier Transform first.")
            return False
        return True

    def on_dft(self):
        chosen = self._pick_signals("Fourier Transform", multiple=False)
        if not chosen:
            return
        fs = simpledialog.askfloat("Sampling frequency",
                                   "Enter the sampling frequency (Hz):", parent=self)
        if fs is None:
            return
        try:
            spec = compute_spectrum(chosen[0], fs)
        except ValueError as e:
            messagebox.showerror("Fourier Transform", str(e))
            return
        self.spectrum = spec
        self.spectrum_source = chosen[0]
        FrequencyWindow(self, spec, "Fourier Transform")

    def on_dominant(self):
        if self._need_spectrum("Dominant Frequencies"):
            FrequencyWindow(self, self.spectrum, "Dominant Frequencies")

    def on_modify(self):
        if not self._need_spectrum("Modify Components"):
            return
        spec = self.spectrum
        k = simpledialog.askinteger("Modify Components",
                                    f"Bin index (0 to {spec.n - 1}):", parent=self)
        if k is None:
            return
        amp = simpledialog.askfloat("Modify Components",
                                    "New amplitude, normalized 0-1 (Cancel = keep):",
                                    parent=self, minvalue=0.0)
        phase = simpledialog.askfloat("Modify Components",
                                      "New phase in radians (Cancel = keep):", parent=self)
        try:
            self.spectrum = modify_component(spec, k, amplitude=amp, phase=phase)
        except ValueError as e:
            messagebox.showerror("Modify Components", str(e))
            return
        FrequencyWindow(self, self.spectrum, "Modified spectrum")

    def on_remove_dc(self):
        if not self._need_spectrum("Remove DC"):
            return
        self.spectrum = remove_dc(self.spectrum)
        FrequencyWindow(self, self.spectrum, "DC removed")

    def on_reconstruct(self):
        if self.spectrum is not None:
            result = self._store(reconstruct(self.spectrum))
            source = self.spectrum_source or result
            self.top_var.set(source.name)
            self.bottom_var.set(result.name)
            self._redraw()
            return

        chosen = self._pick_signals("Reconstruct (IDFT)", multiple=False)
        if not chosen:
            return
        sig = chosen[0]
        if sig.signal_type != 1:
            messagebox.showerror("Reconstruct (IDFT)", "Selected signal is not in frequency domain.")
            return
        try:
            result = self._store(reconstruct_from_signal(sig))
        except Exception as e:
            messagebox.showerror("Reconstruct (IDFT)", str(e))
            return
        self.top_var.set(sig.name)
        self.bottom_var.set(result.name)
        self._redraw()

    def on_save_spectrum(self):
        if not self._need_spectrum("Save Spectrum"):
            return
        path = filedialog.asksaveasfilename(
            title="Save Spectrum",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            from file_io import write_spectrum
            write_spectrum(path, self.spectrum)
            messagebox.showinfo("Save Spectrum", f"Saved successfully to: {path}")
        except Exception as e:
            messagebox.showerror("Save Spectrum Failed", str(e))    
