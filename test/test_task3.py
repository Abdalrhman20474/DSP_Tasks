"""
Automated Test Suite for DSP Task 3
Verifies:
1. Discrete Fourier Transform (DFT):
   - Computes DFT on Task3/Testing/DFT/input_Signal_DFT.txt
   - Compares Amplitude against Output_Signal_DFT_A,Phase.txt via SignalComapreAmplitude
   - Compares Phase against Output_Signal_DFT_A,Phase.txt via SignalComaprePhaseShift
2. Inverse Discrete Fourier Transform (IDFT):
   - Reads Task3/Testing/IDFT/Input_Signal_IDFT_A,Phase.txt
   - Reconstructs time-domain signal using IDFT
   - Compares against Task3/Testing/IDFT/Output_Signal_IDFT.txt via SignalComapreAmplitude
3. Roundtrip Test (Time -> DFT -> IDFT -> Time):
   - Confirms full reconstruction preserves the original samples
4. Dominant Frequencies:
   - Verifies detection of frequency components with normalized amplitude > 0.5
5. DC Component Removal:
   - Verifies F(0) = 0 and reconstructed signal has zero mean
6. Component Modification (Doctor's Note #2):
   - Tests modifying bin k and verifies amplitude even symmetry & phase odd symmetry
"""

import os
import sys

# Ensure root and Task3/Testing are in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

T3_DIR = os.path.join(ROOT_DIR, "Task3", "Testing")
if T3_DIR not in sys.path:
    sys.path.insert(0, T3_DIR)

from file_io import read_signal
from frequency_domain import (
    compute_spectrum,
    dominant_frequencies,
    modify_component,
    remove_dc,
    reconstruct,
    reconstruct_from_signal,
)
from signalcompare import SignalComapreAmplitude, SignalComaprePhaseShift


def run_tests():
    print("=" * 60)
    print("Running DSP Task 3 Test Suite")
    print("=" * 60)

    dft_in_path = os.path.join(T3_DIR, "DFT", "input_Signal_DFT.txt")
    dft_out_path = os.path.join(T3_DIR, "DFT", "Output_Signal_DFT_A,Phase.txt")
    idft_in_path = os.path.join(T3_DIR, "IDFT", "Input_Signal_IDFT_A,Phase.txt")
    idft_out_path = os.path.join(T3_DIR, "IDFT", "Output_Signal_IDFT.txt")

    all_passed = True

    # ---------------- 1. DFT Test ----------------
    print("\n--- 1. Testing Discrete Fourier Transform (DFT) ---")
    sig_dft_in = read_signal(dft_in_path)
    spec = compute_spectrum(sig_dft_in, fs=8.0)

    # Read expected output
    with open(dft_out_path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()][3:]
    exp_amps = [float(ln.split()[0].rstrip("fF")) for ln in lines]
    exp_phases = [float(ln.split()[1].rstrip("fF")) for ln in lines]

    amp_ok = SignalComapreAmplitude(spec.amplitudes, exp_amps)
    phase_ok = SignalComaprePhaseShift(spec.phases, exp_phases)

    if amp_ok:
        print("[PASS] DFT Amplitude Test: Passed successfully!")
    else:
        print("[FAIL] DFT Amplitude Test: Failed!")
        all_passed = False

    if phase_ok:
        print("[PASS] DFT Phase Test: Passed successfully!")
    else:
        print("[FAIL] DFT Phase Test: Failed!")
        all_passed = False

    # ---------------- 2. IDFT Test ----------------
    print("\n--- 2. Testing Inverse Discrete Fourier Transform (IDFT) ---")
    sig_idft_in = read_signal(idft_in_path)
    recon_sig = reconstruct_from_signal(sig_idft_in)

    with open(idft_out_path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()][3:]
    exp_recon_amps = [float(ln.split()[1].rstrip("fF")) for ln in lines]

    idft_ok = SignalComapreAmplitude(recon_sig.amplitudes, exp_recon_amps)
    if idft_ok:
        print("[PASS] IDFT Reconstruction Test: Passed successfully!")
    else:
        print("[FAIL] IDFT Reconstruction Test: Failed!")
        all_passed = False

    # ---------------- 3. Roundtrip Test ----------------
    print("\n--- 3. Testing Roundtrip Reconstruction (Time -> DFT -> IDFT -> Time) ---")
    rt_recon = reconstruct(spec)
    rt_ok = SignalComapreAmplitude(rt_recon.amplitudes, sig_dft_in.amplitudes)
    if rt_ok:
        print("[PASS] Roundtrip Reconstruction Test: Passed successfully!")
    else:
        print("[FAIL] Roundtrip Reconstruction Test: Failed!")
        all_passed = False

    # ---------------- 4. Dominant Frequencies ----------------
    print("\n--- 4. Testing Dominant Frequencies (amp > 0.5) ---")
    dom = dominant_frequencies(spec, threshold=0.5)
    print(f"Dominant components found: {len(dom)}")
    for k, f_val, a_val, p_val in dom:
        print(f"  Bin {k}: Freq = {f_val} Hz, Normalized Amp = {a_val:.4f}, Phase = {p_val:.4f} rad")
    if len(dom) > 0 and all(a > 0.5 for _, _, a, _ in dom):
        print("[PASS] Dominant Frequencies Test: Passed successfully!")
    else:
        print("[FAIL] Dominant Frequencies Test: Failed!")
        all_passed = False

    # ---------------- 5. Remove DC Component ----------------
    print("\n--- 5. Testing Remove DC Component (F(0)) ---")
    spec_no_dc = remove_dc(spec)
    if abs(spec_no_dc.complex_values[0]) < 1e-9:
        recon_no_dc = reconstruct(spec_no_dc)
        mean_amp = sum(recon_no_dc.amplitudes) / len(recon_no_dc.amplitudes)
        if abs(mean_amp) < 1e-4:
            print("[PASS] Remove DC Component Test: F(0) = 0 and signal mean = 0. Passed successfully!")
        else:
            print(f"[FAIL] Reconstructed signal has non-zero mean: {mean_amp}")
            all_passed = False
    else:
        print("[FAIL] DC component was not set to 0!")
        all_passed = False

    # ---------------- 6. Component Modification & Symmetry ----------------
    print("\n--- 6. Testing Component Modification & Symmetry (Doctor's Note #2) ---")
    k_test = 1
    new_amp = 15.0
    new_phase = 0.5
    modified = modify_component(spec, k=k_test, amplitude=new_amp, phase=new_phase, normalized=False)
    mirror = (spec.n - k_test) % spec.n

    # Check amplitude symmetry (even)
    amp_k = abs(modified.complex_values[k_test])
    amp_mirror = abs(modified.complex_values[mirror])

    # Check phase anti-symmetry (odd)
    phase_k = modified.phases[k_test]
    phase_mirror = modified.phases[mirror]

    if abs(amp_k - amp_mirror) < 1e-4 and abs(phase_k + phase_mirror) < 1e-4:
        print(f"[PASS] Symmetry verified: Bin {k_test} (Amp={amp_k:.2f}, Phase={phase_k:.2f}) == "
              f"Mirror {mirror} (Amp={amp_mirror:.2f}, Phase={phase_mirror:.2f})")
    else:
        print(f"[FAIL] Symmetry mismatch! Bin {k_test}: ({amp_k}, {phase_k}), Mirror {mirror}: ({amp_mirror}, {phase_mirror})")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TASK 3 TESTS PASSED WITH 100% ACCURACY!")
    else:
        print("[WARNING] Some tests failed. Please review the output above.")
    print("=" * 60)
    return all_passed


if __name__ == "__main__":
    run_tests()
