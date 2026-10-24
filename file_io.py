import os
from signal_model import Signal


def read_signal(path: str) -> Signal:
    with open(path, 'r') as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    if len(lines) < 3:
        raise ValueError('File is too short, it’s supposed to have at least 3 lines')

    try:
        signal_type = int(lines[0])
        is_periodic = int(lines[1])
        n = int(lines[2])
    except ValueError:
        raise ValueError('Header lines must be integers')

    if signal_type not in (0, 1):
        raise ValueError('signal type must be 0 (time) or 1 (freq)')

    rows = lines[3:3 + n]
    if len(rows) != n:
        raise ValueError(f"expected {n} samples but got {len(rows)}")

    indices, amps, phases = [], [], []

    for i, row in enumerate(rows, start=1):
        parts = row.split()
        try:
            nums = [float(p.rstrip('fF')) for p in parts]
        except ValueError:
            raise ValueError(f"Row {i}: non-numeric value.")

        if signal_type == 0:
            if len(nums) != 2:
                raise ValueError(f'Row {i}: expected 2 values (index, amp), got {len(nums)}')
            indices.append(nums[0])
            amps.append(nums[1])
        else:
            # Frequency domain: accepts [Amp, Phase] (2 cols) or [Index/Freq, Amp, Phase] (3 cols)
            if len(nums) == 2:
                indices.append(float(i - 1))
                amps.append(nums[0])
                phases.append(nums[1])
            elif len(nums) == 3:
                indices.append(nums[0])
                amps.append(nums[1])
                phases.append(nums[2])
            else:
                raise ValueError(f'Row {i}: expected 2 or 3 values for frequency signal, got {len(nums)}')

    return Signal(signal_type, is_periodic, indices, amps, phases, name=os.path.basename(path))


def write_signal(path: str, signal: Signal) -> None:
    """Write a Signal object to a file in standard DSP format."""
    with open(path, 'w') as f:
        f.write(f"{signal.signal_type}\n")
        f.write(f"{signal.is_periodic}\n")
        f.write(f"{len(signal.amplitudes)}\n")
        if signal.signal_type == 0:
            for idx, amp in zip(signal.indices, signal.amplitudes):
                f.write(f"{int(idx)} {amp}\n")
        else:
            for amp, phase in zip(signal.amplitudes, signal.phases):
                f.write(f"{amp} {phase}\n")


def write_spectrum(path: str, spec, append_f: bool = False) -> None:
    """Write Spectrum amplitudes and phases to file matching college format."""
    amps = spec.amplitudes
    phases = spec.phases
    with open(path, 'w') as f:
        f.write("1\n0\n")
        f.write(f"{len(amps)}\n")
        suffix = "f" if append_f else ""
        for a, p in zip(amps, phases):
            f.write(f"{a}{suffix} {p}{suffix}\n")
