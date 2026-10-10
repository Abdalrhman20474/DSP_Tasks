"""
Automated Test Suite for DSP Task 1
Verifies:
1. Signal Addition:
   - Signal1.txt + Signal2.txt == Signal1+signal2.txt
   - Signal1.txt + signal3.txt == signal1+signal3.txt
2. Signal Multiplication:
   - Signal1.txt * 5 == MultiplySignalByConstant-Signal1 - by 5.txt
   - Signal2.txt * 10 == MultiplySignalByConstant-signal2 - by 10.txt
"""

import os
import sys

# Ensure root directory is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from file_io import read_signal
from operations import add_signals, multiply_signal


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
    print("Running DSP Task 1 Test Suite")
    print("=" * 60)

    base_in = os.path.join(ROOT_DIR, "Task 1", "input")
    base_out = os.path.join(ROOT_DIR, "Task 1", "output")

    s1 = read_signal(os.path.join(base_in, "Signal1.txt"))
    s2 = read_signal(os.path.join(base_in, "Signal2.txt"))
    s3 = read_signal(os.path.join(base_in, "signal3.txt"))

    all_passed = True

    # Test 1: Addition s1 + s2
    sum12 = add_signals([s1, s2])
    out12 = os.path.join(base_out, "Signal1+signal2.txt")
    if not compare_signal("Addition: Signal1 + Signal2", out12, sum12.indices, sum12.amplitudes):
        all_passed = False

    # Test 2: Addition s1 + s3
    sum13 = add_signals([s1, s3])
    out13 = os.path.join(base_out, "signal1+signal3.txt")
    if not compare_signal("Addition: Signal1 + signal3", out13, sum13.indices, sum13.amplitudes):
        all_passed = False

    # Test 3: Multiplication s1 * 5
    mul1 = multiply_signal(s1, 5)
    out_mul1 = os.path.join(base_out, "MultiplySignalByConstant-Signal1 - by 5.txt")
    if not compare_signal("Multiplication: Signal1 * 5", out_mul1, mul1.indices, mul1.amplitudes):
        all_passed = False

    # Test 4: Multiplication s2 * 10
    mul2 = multiply_signal(s2, 10)
    out_mul2 = os.path.join(base_out, "MultiplySignalByConstant-signal2 - by 10.txt")
    if not compare_signal("Multiplication: Signal2 * 10", out_mul2, mul2.indices, mul2.amplitudes):
        all_passed = False

    print("=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TASK 1 TESTS PASSED WITH 100% ACCURACY!")
    else:
        print("[WARNING] Some tests failed. Please review errors above.")
    print("=" * 60)
    return all_passed


if __name__ == "__main__":
    run_tests()
