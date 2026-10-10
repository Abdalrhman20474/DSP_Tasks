from dataclasses import dataclass
from typing import List, Optional
import math
from signal_model import Signal


@dataclass
class QuantizationResult:
    levels: int
    num_bits: int
    delta: float
    interval_indices: List[int]
    encoded_values: List[str]
    quantized_values: List[float]
    sampled_error: List[float]
    quantized_signal: Signal
    error_signal: Signal
    original_signal: Signal


def quantize_signal(
    signal: Signal,
    num_bits: Optional[int] = None,
    num_levels: Optional[int] = None
) -> QuantizationResult:
    """
    Quantize an input time-domain signal.
    Accepts either number of bits (b) or number of levels (L).
    If bits is given -> L = 2^b
    If levels is given -> b = ceil(log2(L))
    """
    if signal.signal_type != 0:
        raise ValueError("Only time-domain signals can be quantized.")

    if not signal.amplitudes:
        raise ValueError("Signal has no samples to quantize.")

    if num_bits is None and num_levels is None:
        raise ValueError("Must provide either num_bits or num_levels.")

    if num_bits is not None and num_bits <= 0:
        raise ValueError("num_bits must be a positive integer.")

    if num_levels is not None and num_levels <= 0:
        raise ValueError("num_levels must be a positive integer.")

    if num_bits is not None:
        levels = 2 ** num_bits
        bits = num_bits
    else:
        levels = num_levels
        bits = int(math.ceil(math.log2(levels)))

    x_min = min(signal.amplitudes)
    x_max = max(signal.amplitudes)

    if x_min == x_max:
        raise ValueError("Cannot quantize a flat/constant signal (max equals min).")

    delta = (x_max - x_min) / levels

    interval_indices: List[int] = []
    encoded_values: List[str] = []
    quantized_values: List[float] = []
    sampled_error: List[float] = []

    for x in signal.amplitudes:
        idx = int((x - x_min) / delta)
        if idx >= levels:
            idx = levels - 1
        
        interval_idx = idx + 1  # 1-based index
        code = format(idx, f"0{bits}b")
        midpoint = round(x_min + (idx + 0.5) * delta, 3)
        err = round(midpoint - x, 3)

        interval_indices.append(interval_idx)
        encoded_values.append(code)
        quantized_values.append(midpoint)
        sampled_error.append(err)

    quantized_signal = Signal(
        signal_type=0,
        is_periodic=signal.is_periodic,
        indices=list(signal.indices),
        amplitudes=quantized_values,
        name=f"Quantized({signal.name}, L={levels})"
    )

    error_signal = Signal(
        signal_type=0,
        is_periodic=signal.is_periodic,
        indices=list(signal.indices),
        amplitudes=sampled_error,
        name=f"QuantError({signal.name})"
    )

    return QuantizationResult(
        levels=levels,
        num_bits=bits,
        delta=delta,
        interval_indices=interval_indices,
        encoded_values=encoded_values,
        quantized_values=quantized_values,
        sampled_error=sampled_error,
        quantized_signal=quantized_signal,
        error_signal=error_signal,
        original_signal=signal,
    )
