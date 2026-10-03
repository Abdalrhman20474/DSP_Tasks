import os, tempfile
import matplotlib
matplotlib.use("Agg")                     
import matplotlib.pyplot as plt

from signal_model import Signal
from file_io import read_signal
from operations import add_signals, multiply_signal
from plotting import plot_signal

S = "samples/"
s1 = read_signal(S + "Signal1.txt")
s2 = read_signal(S + "Signal2.txt")
s3 = read_signal(S + "signal3.txt")


def temp_file(text):
    """Write text to a temporary .txt file and return its path."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(text)
    return f.name


def expect_error(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return str(e)
    raise AssertionError("expected ValueError")


# ---- reader (your 3 sample files) ----
for s, first, last in ((s1, 0, 1000), (s2, 1000, 2000), (s3, 2000, 3000)):
    assert len(s.indices) == 1001
    assert s.indices[0] == 0 and s.indices[-1] == 1000
    assert s.amplitudes[0] == first and s.amplitudes[-1] == last
print("reader: OK")

# ---- addition, same indices ----
assert add_signals([s1, s2]).amplitudes[-1] == 3000
assert add_signals([s1, s2, s3]).amplitudes[-1] == 6000
assert add_signals([s1, s2, s3]).amplitudes[0] == 3000
print("addition (same indices): OK")

# ---- addition, different indices (signals built in code, no files needed) ----
small = Signal(0, 0, [0, 1, 2, 3], [1, 2, 3, 4], name="small")
shifted = Signal(0, 0, [5, 6, 7, 8, 9], [10, 10, 10, 10, 10], name="shifted")
r = add_signals([small, shifted])
d = dict(zip(r.indices, r.amplitudes))
assert sorted(d) == [0, 1, 2, 3, 5, 6, 7, 8, 9]
assert d[0] == 1 and d[3] == 4 and d[5] == 10 and d[9] == 10
print("addition (different indices): OK")

# ---- multiplication ----
assert multiply_signal(s1, -1).amplitudes[-1] == -1000
assert multiply_signal(s2, 0.5).amplitudes[-1] == 1000
assert multiply_signal(s2, 0.5).amplitudes[0] == 500
print("multiplication: OK")

# ---- error handling ----
print("  ", expect_error(multiply_signal, s1, "abc"))

freq_path = temp_file("1\n0\n2\n1 5 0\n2 3 1.57\n")      # frequency-domain file
freq = read_signal(freq_path)
os.remove(freq_path)
assert freq.signal_type == 1 and freq.phases == [0.0, 1.57]
print("  ", expect_error(add_signals, [s1, freq]))

bad_path = temp_file("0\n0\n5\n0 1\n1 2\n")             # says 5 samples, has 2
print("  ", expect_error(read_signal, bad_path))
os.remove(bad_path)
print("errors: OK")

# ---- plotting smoke test (two signals at once) ----
fig, (a, b) = plt.subplots(2, 1)
plot_signal(a, s1, "continuous")
plot_signal(b, add_signals([small, shifted]), "both")
fig.savefig("plot_check.png")
print("plotting: OK")