"""
Automated Test Suite for DSP Task 2
Verifies:
1. Arithmetic Operations:
   - Subtraction: Signal2 - Signal1 == signal1-signal2.txt
   - Subtraction: signal3 - Signal1 == signal1-signal3.txt
   - Squaring: Signal1^2 == Output squaring signal 1.txt
   - Normalization: Signal1 (-1 to 1) == normalize of signal 1 (from -1 to 1)-- output.txt
   - Normalization: Signal2 (0 to 1) == normlize signal 2 (from 0 to 1 )-- output.txt
   - Accumulation: Signal1 == output accumulation for signal1.txt
2. Signal Quantization:
   - TestCase 1 (3 bits): Quan1_input.txt vs Quan1_Out.txt (using QuanTest1)
   - TestCase 2 (4 levels): Quan2_input.txt vs Quan2_Out.txt (using QuanTest2)
"""

import os
import sys

# Ensure root directory and Quantization directory are in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

Q_DIR = os.path.join(ROOT_DIR, "Task 2", "Quantization")
if Q_DIR not in sys.path:
    sys.path.insert(0, Q_DIR)

from file_io import read_signal
from operations import (
    subtract_signals,
    square_signal,
    normalize_signal,
    accumulate_signal,
)
from quantization import quantize_signal
from QuanTest1 import QuantizationTest1
from QuanTest2 import QuantizationTest2


def compare_signal(test_name, expected_file_path, actual_indices, actual_samples):
    if not os.path.exists(expected_file_path):
        print(f"[FAIL] [{test_name}] Output file not found: {expected_file_path}")
        return False

    with open(expected_file_path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    # Skip 3 header lines
    data_lines = lines[3:]
    expected_indices = []
    expected_samples = []
    for line in data_lines:
        parts = line.split()
        if len(parts) >= 2:
            expected_indices.append(int(parts[0]))
            expected_samples.append(float(parts[1]))

    if len(expected_samples) != len(actual_samples) or len(expected_indices) != len(actual_indices):
        print(f"[FAIL] [{test_name}] Length mismatch (Expected {len(expected_samples)}, got {len(actual_samples)})")
        return False

    for i in range(len(actual_indices)):
        if actual_indices[i] != expected_indices[i]:
            print(f"[FAIL] [{test_name}] Index mismatch at sample {i}")
            return False

    for i in range(len(actual_samples)):
        diff = abs(actual_samples[i] - expected_samples[i])
        if diff >= 0.01:
            print(f"[FAIL] [{test_name}] Value mismatch at index {actual_indices[i]} (Expected {expected_samples[i]}, got {actual_samples[i]})")
            return False

    print(f"[PASS] [{test_name}] Passed successfully!")
    return True


def run_tests():
    print("=" * 60)
    print("Running DSP Task 2 Test Suite")
    print("=" * 60)

    t1_in = os.path.join(ROOT_DIR, "Task 1", "input")
    t2_arith = os.path.join(ROOT_DIR, "Task 2", "output_arthemtic_operations")
    t2_quant = os.path.join(ROOT_DIR, "Task 2", "Quantization")

    s1 = read_signal(os.path.join(t1_in, "Signal1.txt"))
    s2 = read_signal(os.path.join(t1_in, "Signal2.txt"))
    s3 = read_signal(os.path.join(t1_in, "signal3.txt"))

    all_passed = True

    # --- Part 1: Arithmetic Operations ---
    print("\n--- Testing Arithmetic Operations ---")

    # Subtraction 1: s2 - s1 == 1000
    sub12 = subtract_signals(s2, s1)
    if not compare_signal("Subtraction (Signal2 - Signal1)",
                          os.path.join(t2_arith, "signal1-signal2.txt"),
                          sub12.indices, sub12.amplitudes):
        all_passed = False

    # Subtraction 2: s3 - s1 == 2000
    sub13 = subtract_signals(s3, s1)
    if not compare_signal("Subtraction (signal3 - Signal1)",
                          os.path.join(t2_arith, "signal1-signal3.txt"),
                          sub13.indices, sub13.amplitudes):
        all_passed = False

    # Squaring: s1^2
    sq1 = square_signal(s1)
    if not compare_signal("Squaring (Signal1^2)",
                          os.path.join(t2_arith, "Output squaring signal 1.txt"),
                          sq1.indices, sq1.amplitudes):
        all_passed = False

    # Normalization: s1 from -1 to 1
    norm1 = normalize_signal(s1, "-1to1")
    if not compare_signal("Normalization (Signal1: -1 to 1)",
                          os.path.join(t2_arith, "normalize of signal 1 (from -1 to 1)-- output.txt"),
                          norm1.indices, norm1.amplitudes):
        all_passed = False

    # Normalization: s2 from 0 to 1
    norm2 = normalize_signal(s2, "0to1")
    if not compare_signal("Normalization (Signal2: 0 to 1)",
                          os.path.join(t2_arith, "normlize signal 2 (from 0 to 1 )-- output.txt"),
                          norm2.indices, norm2.amplitudes):
        all_passed = False

    # Accumulation: running sum of s1
    acc1 = accumulate_signal(s1)
    if not compare_signal("Accumulation (Signal1)",
                          os.path.join(t2_arith, "output accumulation for signal1.txt"),
                          acc1.indices, acc1.amplitudes):
        all_passed = False

    # --- Part 2: Quantization Tests ---
    print("\n--- Testing Quantization ---")

    # TestCase 1: 3 bits
    q1_sig = read_signal(os.path.join(t2_quant, "Quan1_input.txt"))
    res_q1 = quantize_signal(q1_sig, num_bits=3)
    out_q1 = os.path.join(t2_quant, "Quan1_Out.txt")
    print("Testing Quantization TestCase 1 (bits = 3):")
    QuantizationTest1(out_q1, res_q1.encoded_values, res_q1.quantized_values)

    # TestCase 2: 4 levels
    q2_sig = read_signal(os.path.join(t2_quant, "Quan2_input.txt"))
    res_q2 = quantize_signal(q2_sig, num_levels=4)
    out_q2 = os.path.join(t2_quant, "Quan2_Out.txt")
    print("Testing Quantization TestCase 2 (levels = 4):")
    QuantizationTest2(out_q2, res_q2.interval_indices, res_q2.encoded_values, res_q2.quantized_values, res_q2.sampled_error)

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TASK 2 TESTS PASSED WITH 100% ACCURACY!")
    else:
        print("[WARNING] Some tests failed. Please review errors above.")
    print("=" * 60)
    return all_passed


if __name__ == "__main__":
    run_tests()
