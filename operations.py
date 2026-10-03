from typing import List
from signal_model import Signal


def add_signals(signals: List[Signal]) -> Signal:
    """Add any number of time-domain signals, aligned by sample index.
    An index missing from a signal counts as 0 for that signal."""
    if not signals:
        raise ValueError("Select at least one signal to add.")
    for s in signals:
        if s.signal_type != 0:
            raise ValueError(f"'{s.name}' is not a time-domain signal.")

    totals = {}
    for s in signals:
        for idx, amp in zip(s.indices, s.amplitudes):
            totals[idx] = totals.get(idx, 0.0) + amp

    indices = sorted(totals)
    amplitudes = [totals[i] for i in indices]
    periodic = int(any(s.is_periodic for s in signals))
    return Signal(0, periodic, indices, amplitudes, name="sum")


