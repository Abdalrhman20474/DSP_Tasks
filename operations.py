from typing import List
from signal_model import Signal



def _require_time_domain(*signals):
    for s in signals:
        if s.signal_type != 0:
            raise ValueError(f"'{s.name}' is not a time-domain signal.")




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


def multiply_signal(signal: Signal, constant: float) -> Signal:
    """Multiply a signal by a constant scalar to amplify, attenuate, or invert."""
    if not isinstance(constant, (int, float)):
        raise ValueError("Constant must be a numeric value (int or float).")

    indices = list(signal.indices)
    amplitudes = [amp * constant for amp in signal.amplitudes]
    return Signal(
        signal_type=signal.signal_type,
        is_periodic=signal.is_periodic,
        indices=indices,
        amplitudes=amplitudes,
        phases=list(signal.phases),
        name=f"{signal.name} * {constant}",
    )




def subtract_signals(a: Signal, b: Signal) -> Signal:
    """a - b, aligned by index (a missing index counts as 0)."""
    _require_time_domain(a, b)
    result = {}
    for idx, amp in zip(a.indices, a.amplitudes):
        result[idx] = result.get(idx, 0.0) + amp
    for idx, amp in zip(b.indices, b.amplitudes):
        result[idx] = result.get(idx, 0.0) - amp
    indices = sorted(result)
    return Signal(0, int(a.is_periodic and b.is_periodic), indices,
                  [result[i] for i in indices], name=f"{a.name} - {b.name}")






def square_signal(signal: Signal) -> Signal:
    """Every amplitude x becomes x * x."""
    _require_time_domain(signal)
    return Signal(0, signal.is_periodic, list(signal.indices),
                  [x * x for x in signal.amplitudes], name=f"square({signal.name})")





def normalize_signal(signal: Signal, mode: str) -> Signal:
    """mode '0to1'  -> (x - min) / (max - min)
       mode '-1to1' -> 2 * (x - min) / (max - min) - 1"""
    _require_time_domain(signal)
    if mode not in ("0to1", "-1to1"):
        raise ValueError("mode must be '0to1' or '-1to1'.")
    lo, hi = min(signal.amplitudes), max(signal.amplitudes)
    if hi == lo:
        raise ValueError("Cannot normalize a constant signal (max equals min).")
    span = hi - lo
    if mode == "0to1":
        out = [(x - lo) / span for x in signal.amplitudes]
    else:
        out = [2 * (x - lo) / span - 1 for x in signal.amplitudes]
    return Signal(0, signal.is_periodic, list(signal.indices), out,
                  name=f"normalize[{mode}]({signal.name})")






def accumulate_signal(signal: Signal) -> Signal:
    """Running sum: y[n] = x[0] + x[1] + ... + x[n]."""
    _require_time_domain(signal)
    pairs = sorted(zip(signal.indices, signal.amplitudes))
    running, out = 0.0, []
    for _, amp in pairs:
        running += amp
        out.append(running)
    return Signal(0, signal.is_periodic, [i for i, _ in pairs], out,
                  name=f"accumulate({signal.name})")