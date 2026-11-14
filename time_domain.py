from signal_model import Signal


def _require_time(signal):
    if signal.signal_type != 0:
        raise ValueError(f"'{signal.name}' is not a time-domain signal.")
    if not signal.amplitudes:
        raise ValueError(f"'{signal.name}' is empty.")


def _require_unit_steps(signal):
    """Neighbouring samples must be one index apart (needed by convolution)."""
    for a, b in zip(signal.indices, signal.indices[1:]):
        if b - a != 1:
            raise ValueError(f"'{signal.name}': sample indices must go up in steps of 1.")




#1: smoothing
def moving_average(signal, window):
    _require_time(signal)
    n = len(signal.amplitudes)
    if window != int(window) or window < 1:
        raise ValueError("Number of points must be a whole number of at least 1.")
    window = int(window)
    if window > n:
        raise ValueError(f"Number of points ({window}) is larger than the signal length ({n}).")
    out = [sum(signal.amplitudes[i:i + window]) / window for i in range(n - window + 1)]
    return Signal(0, 0, list(range(len(out))), out,
                  name=f"MovAvg{window}({signal.name})")




#2: sharpening
def first_derivative(signal):
    """y(n) = x(n) - x(n-1), defined for n = 1 .. N-1."""
    _require_time(signal)
    x = signal.amplitudes
    if len(x) < 2:
        raise ValueError("The first derivative needs at least 2 samples.")
    out = [x[i] - x[i - 1] for i in range(1, len(x))]
    return Signal(0, 0, list(range(len(out))), out, name=f"FirstDeriv({signal.name})")


def second_derivative(signal):
    """y(n) = x(n+1) - 2x(n) + x(n-1), defined for n = 1 .. N-2."""
    _require_time(signal)
    x = signal.amplitudes
    if len(x) < 3:
        raise ValueError("The second derivative needs at least 3 samples.")
    out = [x[i + 1] - 2 * x[i] + x[i - 1] for i in range(1, len(x) - 1)]
    return Signal(0, 0, list(range(len(out))), out, name=f"SecondDeriv({signal.name})")





#3: delaying/advancing signal by k steps
def shift_signal(signal, k):
    """k > 0 delays by k steps (y(n) = x(n-k)); k < 0 advances."""
    _require_time(signal)
    if k != int(k):
        raise ValueError("The number of steps must be a whole number.")
    k = int(k)
    return Signal(0, signal.is_periodic, [i + k for i in signal.indices],
                  list(signal.amplitudes), name=f"Shift{k:+d}({signal.name})")





#4&5: folding & delaying/advancing a folded signal
def fold_signal(signal):
    """y(n) = x(-n)."""
    _require_time(signal)
    pairs = sorted(zip((-i for i in signal.indices), signal.amplitudes))
    return Signal(0, signal.is_periodic, [p[0] for p in pairs], [p[1] for p in pairs],
                  name=f"Fold({signal.name})")


def shift_folded(signal, k):
    folded = fold_signal(signal)
    shifted = shift_signal(folded, k)
    shifted.name = f"Fold+Shift{int(k):+d}({signal.name})"
    return shifted


############### Farouk Part #################




#6: removing DC
def remove_dc_time(signal):
    _require_time(signal)
    mean = sum(signal.amplitudes) / len(signal.amplitudes)
    return Signal(0, signal.is_periodic, list(signal.indices),
                  [a - mean for a in signal.amplitudes], name=f"NoDC({signal.name})")



#7: convolution
def convolve(a, b):
    _require_time(a); _require_time(b)
    _require_unit_steps(a); _require_unit_steps(b)
    n1, n2 = len(a.amplitudes), len(b.amplitudes)
    out = [0.0] * (n1 + n2 - 1)
    for i, x in enumerate(a.amplitudes):
        for j, h in enumerate(b.amplitudes):
            out[i + j] += x * h
    start = a.indices[0] + b.indices[0]
    return Signal(0, 0, [start + i for i in range(len(out))], out,
                  name=f"Conv({a.name},{b.name})")
