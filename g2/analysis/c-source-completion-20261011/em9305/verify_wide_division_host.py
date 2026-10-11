"""Host arithmetic qualification only; does not execute the stock ARC image."""
import ctypes, random, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
source = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_sync_divide.c"
with tempfile.TemporaryDirectory() as directory:
    output = Path(directory) / "quotient.dylib"
    subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-dynamiclib", str(source), "-o", str(output)], check=True)
    library = ctypes.CDLL(str(output))
    function = library.opencfw_em9305_sleep_sync_divide
    function.argtypes = [ctypes.c_uint32] * 4
    function.restype = ctypes.c_uint64
    values = [0,1,2,0xffffffff,0x100000000,0x7fffffffffffffff,0x8000000000000000,0xffffffffffffffff]
    pairs = [(n,d) for n in values for d in values]
    randomizer = random.Random(9305)
    pairs += [(randomizer.getrandbits(64),randomizer.getrandbits(64)) for _ in range(2048)]
    for numerator,denominator in pairs:
        actual = function(numerator & 0xffffffff,numerator >> 32,denominator & 0xffffffff,denominator >> 32)
        expected = numerator // denominator if denominator else 0x7fffffffffffffff
        assert actual == expected, (numerator,denominator,actual,expected)
    print(f"PASS {len(pairs)} host arithmetic cases; stock ARC execution unverified")
