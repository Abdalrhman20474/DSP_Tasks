MODES = ("continuous", "discrete", "both")


def plot_signal(ax, signal, mode="both"):
    """Draw one signal on a matplotlib Axes.
    continuous -> line plot, discrete -> stem plot, both -> the two together."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")

    x, y = signal.indices, signal.amplitudes

    if mode in ("continuous", "both"):
        ax.plot(x, y, linewidth=1.5)

    if mode in ("discrete", "both"):
        markerline, stemlines, _ = ax.stem(x, y, basefmt=" ")
        # 1001 points would look like a solid block with big markers
        markerline.set_markersize(6 if len(x) <= 50 else 2)
        stemlines.set_linewidth(1.0 if len(x) <= 50 else 0.4)

    ax.set_title(signal.name)
    ax.set_xlabel("n" if signal.signal_type == 0 else "Frequency")
    ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=0.3)


def show_empty(ax, text="No signal selected"):
    ax.text(0.5, 0.5, text, ha="center", va="center", transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])