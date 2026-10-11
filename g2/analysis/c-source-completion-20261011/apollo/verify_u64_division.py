#!/usr/bin/env python3
"""Host arithmetic check of source 0x42287c; no stock execution claim."""
import ctypes
import json
import pathlib
import random
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/bootloader/source_candidate_20261010/u64_division_42287c.c"
OUTPUT = ROOT / "g2/build/c-source-completion-20261011/apollo/u64_division_host.so"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-shared", "-fPIC", str(SOURCE), "-o", str(OUTPUT)], check=True)
function = ctypes.CDLL(str(OUTPUT)).opencfw_provider_42287c
function.argtypes = [ctypes.c_uint32] * 4
function.restype = ctypes.c_uint64
mask = (1 << 64) - 1
edges = [0, 1, 2, 3, 0xffff, 0x10000, 0xffffffff,
         0x100000000, 0x100000001, 0x8000000000000000, mask]
cases = [(a, b) for a in edges for b in edges]
rng = random.Random(0x42287c)
cases += [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(100000)]
for numerator, denominator in cases:
    actual = function(numerator & 0xffffffff, numerator >> 32,
                      denominator & 0xffffffff, denominator >> 32)
    expected = numerator if denominator == 0 else numerator // denominator
    assert actual == expected, (hex(numerator), hex(denominator), hex(actual), hex(expected))
receipt = {"status": "PASS", "cases": len(cases),
           "scope": "host arithmetic quotient including divisor-zero stock pseudocode rule; no stock instruction execution, ABI register oracle, or production admission"}
print(json.dumps(receipt))
