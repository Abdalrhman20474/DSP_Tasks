"""
Automated Test Suite for DSP Task 4 (Time Domain Operations) and Task 5 (Convolution).

Tests:
1. Smoothing (Moving Average):
   - Signal1.txt with window = 3 against OutMovAvgTest1.txt
   - Signal2.txt with window = 5 against OutMovAvgTest2.txt
2. Sharpening (Derivatives):
   - First Derivative of ramp signal [1..100] -> [1, 1, ... 1] (length 99)
   - Second Derivative of ramp signal [1..100] -> [0, 0, ... 0] (length 98)
3. Shifting & Folding:
   - Folding input_fold.txt against Output_fold.txt
   - Folding + Advance/Delay (+500) against Output_ShifFoldedby500.txt
   - Folding + Advance/Delay (-500) against Output_ShiftFoldedby-500.txt
4. DC Component Removal in Time Domain:
   - Mean of output signal is 0.0
5. Convolution (Task 5):
   - Convolving Input_conv_Sig1 and Input_conv_Sig2 against expected indices & samples
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from file_io import read_signal
from signal_model import Signal
from time_domain import (
    moving_average,
    first_derivative,
    second_derivative,
    shift_signal,
    fold_signal,
    shift_folded,
    remove_dc_time,
    convolve,
)


def find_test_path(*relative_parts):
    """Finds a file whether the directory is named Task4 or Task4-5."""
    candidates = [
        os.path.join(ROOT_DIR, "Task4-5", *relative_parts),
        os.path.join(ROOT_DIR, "Task4", *relative_parts),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    # Fallback search
    for root, _, files in os.walk(ROOT_DIR):
        if relative_parts[-1] in files:
            return os.path.join(root, relative_parts[-1])
    return candidates[0]


def test_moving_average():
    print("\n--- 1. Testing Smoothing (Moving Average) ---")
    sig1_path = os.path.join(ROOT_DIR, "Task 1", "input", "Signal1.txt")
    sig2_path = os.path.join(ROOT_DIR, "Task 1", "input", "Signal2.txt")
    out1_path = find_test_path("TestCases-Task4", "TestCases", "Moving Average", "OutMovAvgTest1.txt")
    out2_path = find_test_path("TestCases-Task4", "TestCases", "Moving Average", "OutMovAvgTest2.txt")

    # Test 1: Window = 3
    s1 = read_signal(sig1_path)
    res1 = moving_average(s1, 3)
    exp1 = read_signal(out1_path)
    assert len(res1.amplitudes) == len(exp1.amplitudes), f"Length mismatch: {len(res1.amplitudes)} != {len(exp1.amplitudes)}"
    max_err1 = max(abs(a - b) for a, b in zip(res1.amplitudes, exp1.amplitudes))
    assert max_err1 < 0.01, f"Max error too large: {max_err1}"
    print(f"[PASS] Moving Average (Window=3): Passed successfully! (Max diff: {max_err1:.6f})")

    # Test 2: Window = 5
    s2 = read_signal(sig2_path)
    res2 = moving_average(s2, 5)
    exp2 = read_signal(out2_path)
    assert len(res2.amplitudes) == len(exp2.amplitudes), f"Length mismatch: {len(res2.amplitudes)} != {len(exp2.amplitudes)}"
    max_err2 = max(abs(a - b) for a, b in zip(res2.amplitudes, exp2.amplitudes))
    assert max_err2 < 0.01, f"Max error too large: {max_err2}"
    print(f"[PASS] Moving Average (Window=5): Passed successfully! (Max diff: {max_err2:.6f})")


def test_derivatives():
    print("\n--- 2. Testing Sharpening (First & Second Derivatives) ---")
    ramp = list(range(1, 101))  # 1 to 100
    ramp_sig = Signal(0, 0, list(range(len(ramp))), [float(x) for x in ramp], name="Ramp")

    # 1st derivative: Y(n) = x(n) - x(n-1) => all 1s
    d1 = first_derivative(ramp_sig)
    exp_d1 = [1.0] * 99
    assert len(d1.amplitudes) == 99, f"1st derivative length mismatch: {len(d1.amplitudes)}"
    assert all(abs(a - b) < 0.01 for a, b in zip(d1.amplitudes, exp_d1)), "1st derivative values wrong"
    print(f"[PASS] First Derivative: Passed successfully! (len={len(d1.amplitudes)}, all values=1.0)")

    # 2nd derivative: Y(n) = x(n+1) - 2x(n) + x(n-1) => all 0s
    d2 = second_derivative(ramp_sig)
    exp_d2 = [0.0] * 98
    assert len(d2.amplitudes) == 98, f"2nd derivative length mismatch: {len(d2.amplitudes)}"
    assert all(abs(a - b) < 0.01 for a, b in zip(d2.amplitudes, exp_d2)), "2nd derivative values wrong"
    print(f"[PASS] Second Derivative: Passed successfully! (len={len(d2.amplitudes)}, all values=0.0)")


def test_shifting_and_folding():
    print("\n--- 3. Testing Shifting & Folding ---")
    in_path = find_test_path("TestCases-Task4", "TestCases", "Shifting and Folding", "input_fold.txt")
    out_fold_path = find_test_path("TestCases-Task4", "TestCases", "Shifting and Folding", "Output_fold.txt")
    out_500_path = find_test_path("TestCases-Task4", "TestCases", "Shifting and Folding", "Output_ShifFoldedby500.txt")
    out_m500_path = find_test_path("TestCases-Task4", "TestCases", "Shifting and Folding", "Output_ShiftFoldedby-500.txt")

    in_sig = read_signal(in_path)

    # 1. Fold
    folded = fold_signal(in_sig)
    exp_fold = read_signal(out_fold_path)
    assert folded.indices == exp_fold.indices, "Fold indices mismatch"
    assert all(abs(a - b) < 0.01 for a, b in zip(folded.amplitudes, exp_fold.amplitudes)), "Fold amplitudes mismatch"
    print("[PASS] Fold Signal: Passed successfully!")

    # 2. Shift Folded by +500
    sf_500 = shift_folded(in_sig, 500)
    exp_500 = read_signal(out_500_path)
    assert sf_500.indices == exp_500.indices, "Shift Fold (+500) indices mismatch"
    assert all(abs(a - b) < 0.01 for a, b in zip(sf_500.amplitudes, exp_500.amplitudes)), "Shift Fold (+500) amplitudes mismatch"
    print("[PASS] Shift Fold (+500): Passed successfully!")

    # 3. Shift Folded by -500
    sf_m500 = shift_folded(in_sig, -500)
    exp_m500 = read_signal(out_m500_path)
    assert sf_m500.indices == exp_m500.indices, "Shift Fold (-500) indices mismatch"
    assert all(abs(a - b) < 0.01 for a, b in zip(sf_m500.amplitudes, exp_m500.amplitudes)), "Shift Fold (-500) amplitudes mismatch"
    print("[PASS] Shift Fold (-500): Passed successfully!")


def test_remove_dc_time():
    print("\n--- 4. Testing Remove DC Component in Time Domain ---")
    sig = read_signal(os.path.join(ROOT_DIR, "Task 1", "input", "Signal1.txt"))
    no_dc = remove_dc_time(sig)
    mean = sum(no_dc.amplitudes) / len(no_dc.amplitudes)
    assert abs(mean) < 1e-9, f"DC not removed, mean is {mean}"
    print(f"[PASS] Remove DC in Time Domain: Signal mean = {mean:.1e} (zero). Passed successfully!")


def test_convolution():
    print("\n--- 5. Testing Convolution (Task 5) ---")
    c1_path = find_test_path("Convolution-Task5", "Convolution", "Input_conv_Sig1.txt")
    c2_path = find_test_path("Convolution-Task5", "Convolution", "Input_conv_Sig2.txt")

    c1 = read_signal(c1_path)
    c2 = read_signal(c2_path)
    conv_res = convolve(c1, c2)

    expected_indices = [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    expected_samples = [1.0, 1.0, -1.0, 0.0, 0.0, 3.0, 3.0, 2.0, 1.0]

    assert len(conv_res.indices) == len(expected_indices), "Indices length mismatch"
    assert len(conv_res.amplitudes) == len(expected_samples), "Samples length mismatch"
    assert conv_res.indices == expected_indices, f"Indices mismatch: {conv_res.indices} != {expected_indices}"
    assert all(abs(a - b) < 0.01 for a, b in zip(conv_res.amplitudes, expected_samples)), "Samples mismatch"

    # Also run college ConvTest if available
    conv_dir = os.path.dirname(c1_path)
    if conv_dir not in sys.path:
        sys.path.insert(0, conv_dir)
    try:
        from ConvTest import ConvTest  # type: ignore
        ConvTest(conv_res.indices, conv_res.amplitudes)
    except Exception as e:
        print(f"College ConvTest call info: {e}")

    print("[PASS] Convolution (Task 5): Passed successfully with 100% accuracy!")


def main():
    print("=" * 60)
    print("Running DSP Task 4 & Task 5 Test Suite")
    print("=" * 60)

    test_moving_average()
    test_derivatives()
    test_shifting_and_folding()
    test_remove_dc_time()
    test_convolution()

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TASK 4 & TASK 5 TESTS PASSED WITH 100% ACCURACY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
