from signal_model import Signal
import os


def read_signal(path:str) -> Signal:
    with open(path,'r') as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    if len(lines) < 3:
        raise ValueError('File is too short , it’s supposed to have at least 3 lines')

    try:
        signal_type = int(lines[0])
        is_periodic = int(lines[1])
        n = int(lines[2])
    except ValueError:
        raise ValueError('Header lines must be integers')

    if signal_type not in (0,1):
        raise ValueError('signal type must be 0 (time) or 1 (freq)')

    rows = lines[3:3+n]
    if len(rows) != n:
        raise ValueError(f"expected {n} samples but got {len(rows)}")


    expected_cols = 2 if signal_type == 0 else 3
    indices , amps , phases = [] , [] , []

    for i , row in enumerate(rows,start=1):
        parts = row.split()
        if len(parts) != expected_cols:
            raise ValueError(f'Row {i}: expected {expected_cols} values, got {len(parts)}') 

        try:
            nums = [float(p) for p in parts]
        except ValueError:
            raise ValueError(f"Row {i}: non-numeric value.")
        indices.append(nums[0])
        amps.append(nums[1])
        if signal_type == 1:
            phases.append(nums[2])

    return Signal(signal_type, is_periodic, indices, amps, phases, name=os.path.basename(path)) 