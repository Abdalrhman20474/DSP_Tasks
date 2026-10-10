from dataclasses import dataclass , field
from typing import List



@dataclass
class Signal:
    signal_type: int
    is_periodic: int
    indices: List[float]
    amplitudes: List[float]
    phases: List[float] = field(default_factory = list)
    name: str = "signal"