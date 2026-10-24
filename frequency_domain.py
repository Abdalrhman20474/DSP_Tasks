import cmath
import math
from dataclasses import dataclass
from typing import List

from signal_model import Signal

EPS_REL = 1e-9   # amplitudes below EPS_REL * max are treated as "empty" bins


def transform(data, inverse=False):
    """DFT (inverse=False) or IDFT (inverse=True) of a list of numbers."""
    n_total = len(data)
    sign = 1 if inverse else -1
    out = []
    for k in range(n_total):
        total = 0j
        for n in range(n_total):
            angle = sign * 2 * math.pi * ((k * n) % n_total) / n_total
            total += data[n] * cmath.exp(1j * angle)
        out.append(total / n_total if inverse else total)
    return out





@dataclass
class Spectrum:
    """Frequency-domain data. complex_values is the single source of truth."""
    fs: float
    complex_values: List[complex]
    name: str = "spectrum"

    @property
    def n(self):
        return len(self.complex_values)

    @property
    def frequencies(self):
        return [k * self.fs / self.n for k in range(self.n)]

    @property
    def amplitudes(self):
        return [abs(x) for x in self.complex_values]

    @property
    def max_amplitude(self):
        return max(self.amplitudes) if self.n else 0.0

    @property
    def normalized_amplitudes(self):
        m = self.max_amplitude
        return [a / m for a in self.amplitudes] if m > 0 else self.amplitudes

    @property
    def phases(self):
        m = self.max_amplitude
        return [math.atan2(x.imag, x.real) if abs(x) > EPS_REL * m else 0.0
                for x in self.complex_values]


def compute_spectrum(signal, fs):
    if signal.signal_type != 0:
        raise ValueError("Fourier transform needs a time-domain signal.")
    if not signal.amplitudes:
        raise ValueError("The signal is empty.")
    if fs <= 0:
        raise ValueError("Sampling frequency must be greater than zero.")
    values = transform(signal.amplitudes, inverse=False)
    return Spectrum(fs, values, name=f"DFT({signal.name})")



def dominant_frequencies(spec, threshold=0.5):
    """[(k, frequency, normalized amplitude, phase), ...] above threshold."""
    norm, phases, freqs = spec.normalized_amplitudes, spec.phases, spec.frequencies
    return [(k, freqs[k], norm[k], phases[k])
            for k in range(spec.n) if norm[k] > threshold]




def modify_component(spec, k, amplitude=None, phase=None, normalized=True):
    """Return a NEW spectrum with bin k (and its mirror bin) changed."""
    n = spec.n
    if not 0 <= k < n:
        raise ValueError(f"Bin index must be between 0 and {n - 1}.")
    if amplitude is not None and amplitude < 0:
        raise ValueError("Amplitude cannot be negative.")

    old = spec.complex_values[k]
    new_amp = abs(old) if amplitude is None else amplitude
    if amplitude is not None and normalized:
        new_amp = amplitude * spec.max_amplitude
    new_phase = spec.phases[k] if phase is None else phase
    new_value = cmath.rect(new_amp, new_phase)

    values = list(spec.complex_values)
    mirror = (n - k) % n
    if mirror == k:                       # DC (or Nyquist): must stay real
        values[k] = complex(new_value.real, 0.0)
    else:
        values[k] = new_value
        values[mirror] = new_value.conjugate()
    return Spectrum(spec.fs, values, name=spec.name)