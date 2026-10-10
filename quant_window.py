import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from file_io import read_signal
from quantization import quantize_signal, QuantizationResult
from plotting import plot_signal


class QuantWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Signal Quantization")
        self.geometry("950x700")
        self.minsize(800, 550)

        self.last_result: QuantizationResult = None

        self.signal_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="bits")  # "bits" or "levels"
        self.val_var = tk.StringVar(value="3")
        self.info_var = tk.StringVar(value="Select a signal and specify bits or levels to quantize.")

        self._build_ui()
        self._refresh_signals()

    def _build_ui(self):
        # 1. Parameter Frame
        param_frame = ttk.LabelFrame(self, text="Quantization Settings", padding=10)
        param_frame.pack(fill="x", padx=10, pady=5)

        # Signal selector
        ttk.Label(param_frame, text="Signal:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.sig_box = ttk.Combobox(param_frame, textvariable=self.signal_var, state="readonly", width=25)
        self.sig_box.grid(row=0, column=1, sticky="w", padx=4, pady=4)

        ttk.Button(param_frame, text="Load File...", command=self._load_file).grid(row=0, column=2, padx=6, pady=4)

        # Mode selection: Bits vs Levels
        ttk.Label(param_frame, text="Input Type:").grid(row=0, column=3, sticky="w", padx=(15, 4), pady=4)
        ttk.Radiobutton(param_frame, text="Bits (b)", value="bits", variable=self.mode_var).grid(row=0, column=4, padx=4)
        ttk.Radiobutton(param_frame, text="Levels (L)", value="levels", variable=self.mode_var).grid(row=0, column=5, padx=4)

        # Value input
        ttk.Label(param_frame, text="Value:").grid(row=0, column=6, sticky="w", padx=(15, 4), pady=4)
        ttk.Entry(param_frame, textvariable=self.val_var, width=8).grid(row=0, column=7, padx=4, pady=4)

        # Quantize button
        ttk.Button(param_frame, text="Quantize", style="Accent.TButton" if "Accent.TButton" in ttk.Style().theme_names() else "TButton",
                   command=self.on_quantize).grid(row=0, column=8, padx=(15, 4), pady=4)

        # Info bar
        info_label = ttk.Label(self, textvariable=self.info_var, font=("Segoe UI", 9, "italic"), padding=(10, 2))
        info_label.pack(fill="x")

        # 2. Notebook tabs for Table and Plot
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Tab 1: Table
        tab_table = ttk.Frame(notebook)
        notebook.add(tab_table, text="Samples & Encoding Table")
        self._build_table(tab_table)

        # Tab 2: Visual Graphs
        tab_plot = ttk.Frame(notebook)
        notebook.add(tab_plot, text="Quantization Waveforms")
        self._build_plot(tab_plot)

        # 3. Bottom Bar
        bottom_bar = ttk.Frame(self, padding=8)
        bottom_bar.pack(fill="x")
        ttk.Button(bottom_bar, text="Send Result Signals to Main Framework",
                   command=self._send_to_main).pack(side="left", padx=5)
        ttk.Button(bottom_bar, text="Close", command=self.destroy).pack(side="right", padx=5)

    def _build_table(self, container):
        cols = ("idx", "orig", "interval", "encoded", "quantized", "error")
        self.tree = ttk.Treeview(container, columns=cols, show="headings", height=15)

        self.tree.heading("idx", text="Sample (n)")
        self.tree.heading("orig", text="Original Amplitude x[n]")
        self.tree.heading("interval", text="Interval Index")
        self.tree.heading("encoded", text="Encoded Bits")
        self.tree.heading("quantized", text="Quantized x_q[n]")
        self.tree.heading("error", text="Quantization Error e[n]")

        self.tree.column("idx", width=80, anchor="center")
        self.tree.column("orig", width=140, anchor="center")
        self.tree.column("interval", width=110, anchor="center")
        self.tree.column("encoded", width=110, anchor="center")
        self.tree.column("quantized", width=140, anchor="center")
        self.tree.column("error", width=140, anchor="center")

        scroll_y = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

    def _build_plot(self, container):
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.ax_quant = self.fig.add_subplot(2, 1, 1)
        self.ax_err = self.fig.add_subplot(2, 1, 2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=container)
        toolbar = NavigationToolbar2Tk(self.canvas, container, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side="bottom", fill="x")
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self._clear_plots()

    def _clear_plots(self):
        self.ax_quant.clear()
        self.ax_err.clear()
        self.ax_quant.set_title("Original vs Quantized Signal")
        self.ax_quant.grid(True, alpha=0.3)
        self.ax_err.set_title("Quantization Error: e[n] = x_q[n] - x[n]")
        self.ax_err.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw_idle()

    def _refresh_signals(self):
        names = [s.name for s in getattr(self.parent, "signals", [])]
        self.sig_box["values"] = names
        if names:
            if not self.signal_var.get() or self.signal_var.get() not in names:
                self.signal_var.set(names[0])

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Load Signal to Quantize",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            sig = read_signal(path)
            if hasattr(self.parent, "_store"):
                sig = self.parent._store(sig)
            self._refresh_signals()
            self.signal_var.set(sig.name)
        except Exception as e:
            messagebox.showerror("Error Reading File", str(e))

    def on_quantize(self):
        sig_name = self.signal_var.get()
        if not sig_name:
            messagebox.showwarning("Quantization", "Please select a signal to quantize.")
            return

        sig = None
        for s in getattr(self.parent, "signals", []):
            if s.name == sig_name:
                sig = s
                break

        if sig is None:
            messagebox.showerror("Quantization", f"Signal '{sig_name}' not found.")
            return

        try:
            val = int(self.val_var.get().strip())
            if val <= 0:
                raise ValueError("Value must be greater than 0.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for bits or levels.")
            return

        mode = self.mode_var.get()
        try:
            if mode == "bits":
                result = quantize_signal(sig, num_bits=val)
            else:
                result = quantize_signal(sig, num_levels=val)
        except Exception as e:
            messagebox.showerror("Quantization Failed", str(e))
            return

        self.last_result = result
        self._display_results(result)

    def _display_results(self, res: QuantizationResult):
        # 1. Update info bar
        x_min = min(res.original_signal.amplitudes)
        x_max = max(res.original_signal.amplitudes)
        self.info_var.set(
            f"Range: [{x_min:.3f}, {x_max:.3f}]  |  Levels (L): {res.levels}  |  "
            f"Bits (b): {res.num_bits}  |  Step Size (Delta): {res.delta:.4f}"
        )

        # 2. Populate table
        for item in self.tree.get_children():
            self.tree.delete(item)

        orig_amps = res.original_signal.amplitudes
        indices = res.original_signal.indices
        for i in range(len(orig_amps)):
            n = indices[i]
            x = orig_amps[i]
            interval = res.interval_indices[i]
            code = res.encoded_values[i]
            xq = res.quantized_values[i]
            err = res.sampled_error[i]
            self.tree.insert("", "end", values=(n, f"{x:.4f}", interval, code, f"{xq:.4f}", f"{err:.4f}"))

        # 3. Update Plots
        self.ax_quant.clear()
        self.ax_err.clear()

        # Top plot: Original vs Quantized
        self.ax_quant.plot(indices, orig_amps, label="Original x[n]", color="blue", alpha=0.7, linestyle="--")
        self.ax_quant.step(indices, res.quantized_values, label=f"Quantized x_q[n] (L={res.levels})",
                           color="green", where="mid")
        self.ax_quant.set_title(f"Original vs Quantized Signal ({res.original_signal.name})")
        self.ax_quant.set_ylabel("Amplitude")
        self.ax_quant.legend(loc="upper right")
        self.ax_quant.grid(True, alpha=0.3)

        # Bottom plot: Error signal
        markerline, stemlines, _ = self.ax_err.stem(indices, res.sampled_error, basefmt=" ")
        markerline.set_color("red")
        markerline.set_markersize(4)
        stemlines.set_color("red")
        stemlines.set_linewidth(0.8)
        self.ax_err.set_title("Quantization Error e[n] = x_q[n] - x[n]")
        self.ax_err.set_xlabel("Sample (n)")
        self.ax_err.set_ylabel("Error")
        self.ax_err.grid(True, alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw_idle()

    def _send_to_main(self):
        if not self.last_result:
            messagebox.showinfo("Send Results", "Please run quantization first.")
            return

        if hasattr(self.parent, "_store"):
            q_sig = self.parent._store(self.last_result.quantized_signal)
            e_sig = self.parent._store(self.last_result.error_signal)
            if hasattr(self.parent, "top_var"):
                self.parent.top_var.set(q_sig.name)
            if hasattr(self.parent, "bottom_var"):
                self.parent.bottom_var.set(e_sig.name)
            if hasattr(self.parent, "_redraw"):
                self.parent._redraw()
            messagebox.showinfo("Results Sent", "Quantized signal and error signal sent to main window top and bottom plots!")
