"""College Test Runner for Task 1.
Runs the exact test comparisons defined by the college TAs using the sample input
and output files provided in 'College files/Task1 files+test'.
"""

import os
import sys

# Ensure Task 1 modules are importable
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from file_io import read_signal
from operations import add_signals, multiply_signal


def compare_signal(test_name, expected_file_path, actual_indices, actual_samples):
    """Compares actual indices and samples against the college expected output file."""
    if not os.path.exists(expected_file_path):
        print(f"❌ [{test_name}] Output file not found: {expected_file_path}")
        return False

    with open(expected_file_path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    # Skip 3 header lines (SignalType, IsPeriodic, N)
    data_lines = lines[3:]
    expected_indices = []
    expected_samples = []
    for line in data_lines:
        parts = line.split()
        if len(parts) >= 2:
            expected_indices.append(int(parts[0]))
            expected_samples.append(float(parts[1]))

    # 1. Length check
    if len(expected_samples) != len(actual_samples) or len(expected_indices) != len(actual_indices):
        print(f"[FAIL] [{test_name}] Length mismatch (Expected {len(expected_samples)}, got {len(actual_samples)})")
        return False

    # 2. Index check
    for i in range(len(actual_indices)):
        if actual_indices[i] != expected_indices[i]:
            print(f"[FAIL] [{test_name}] Index mismatch at sample {i} (Expected {expected_indices[i]}, got {actual_indices[i]})")
            return False

    # 3. Amplitude value check (tolerance 0.01)
    for i in range(len(actual_samples)):
        diff = abs(actual_samples[i] - expected_samples[i])
        if diff >= 0.01:
            print(f"[FAIL] [{test_name}] Value mismatch at index {actual_indices[i]} (Expected {expected_samples[i]}, got {actual_samples[i]})")
            return False

    print(f"[PASS] [{test_name}] Passed successfully!")
    return True


def run_all_college_tests():
    print("=" * 60)
    print("Running Official College Test Suite (Task 1)")
    print("=" * 60)

    base_in = os.path.join(current_dir, "input")
    base_out = os.path.join(current_dir, "output")

    # Load input signals
    s1 = read_signal(os.path.join(base_in, "Signal1.txt"))
    s2 = read_signal(os.path.join(base_in, "Signal2.txt"))
    s3 = read_signal(os.path.join(base_in, "signal3.txt"))

    all_passed = True

    # Test 1: Addition of Signal 1 + Signal 2
    sum_1_2 = add_signals([s1, s2])
    out_1_2 = os.path.join(base_out, "Signal1+signal2.txt")
    if not compare_signal("Addition: Signal1 + Signal2", out_1_2, sum_1_2.indices, sum_1_2.amplitudes):
        all_passed = False

    # Test 2: Addition of Signal 1 + Signal 3
    sum_1_3 = add_signals([s1, s3])
    out_1_3 = os.path.join(base_out, "signal1+signal3.txt")
    if not compare_signal("Addition: Signal1 + Signal3", out_1_3, sum_1_3.indices, sum_1_3.amplitudes):
        all_passed = False

    # Test 3: Multiply Signal 1 by 5
    mul_1_5 = multiply_signal(s1, 5)
    out_1_5 = os.path.join(base_out, "MultiplySignalByConstant-Signal1 - by 5.txt")
    if not compare_signal("Multiplication: Signal1 * 5", out_1_5, mul_1_5.indices, mul_1_5.amplitudes):
        all_passed = False

    # Test 4: Multiply Signal 2 by 10
    mul_2_10 = multiply_signal(s2, 10)
    out_2_10 = os.path.join(base_out, "MultiplySignalByConstant-signal2 - by 10.txt")
    if not compare_signal("Multiplication: Signal2 * 10", out_2_10, mul_2_10.indices, mul_2_10.amplitudes):
        all_passed = False

    print("=" * 60)
    if all_passed:
        print("[SUCCESS] ALL COLLEGE TESTS PASSED WITH 100% ACCURACY!")
    else:
        print("[WARNING] Some tests failed. Please review the errors above.")
    print("=" * 60)


if __name__ == "__main__":
    run_all_college_tests()
