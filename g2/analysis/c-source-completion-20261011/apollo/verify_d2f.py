#!/usr/bin/env python3
"""Host bit comparison for the pinned compiler-rt double-to-float source."""
from pathlib import Path
import ctypes
import hashlib
import json
import random
import subprocess

root = Path(__file__).resolve().parents[4]
base = root / "g2/components/bootloader/source_candidate_20261010/compiler_rt_20_1_8"
vendor = root / "third-party/upstream/llvm-compiler-rt-format-20.1.8"
out = root / "g2/build/c-source-completion-20261011/apollo"
out.mkdir(parents=True, exist_ok=True)
library = out / "libd2f_oracle.dylib"
subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-fno-builtin",
                "-I" + str(vendor), str(base / "truncdfsf2.c"),
                str(Path(__file__).with_name("d2f_oracle.c")), "-o", str(library)],
               check=True)
module = ctypes.CDLL(str(library))
for name in ("source_bits", "hardware_bits"):
    fn = getattr(module, name)
    fn.argtypes = [ctypes.c_uint64]
    fn.restype = ctypes.c_uint32

fixtures = [0, 1, 0x8000000000000000, 0x7ff0000000000000,
            0xfff0000000000000, 0x7ff8000000000000,
            0x7ff0000000000001, 0x3ff0000000000000,
            0x36a0000000000000, 0x3800000000000000,
            0x47efffffffffffff]
randomizer = random.Random(20261011)
fixtures.extend(randomizer.getrandbits(64) for _ in range(100000))
for exponent in (873, 874, 875, 895, 896, 897, 1149, 1150, 1151):
    for sign in (0, 1):
        for mantissa in (0, 1, (1 << 51) - 1, 1 << 51,
                         (1 << 52) - 2, (1 << 52) - 1):
            fixtures.append((sign << 63) | (exponent << 52) | mantissa)
for sign in (0, 1):
    for payload in (1, 1 << 50, 1 << 51, (1 << 52) - 1):
        fixtures.append((sign << 63) | (0x7ff << 52) | payload)

mismatch = []
for raw in fixtures:
    source = module.source_bits(raw)
    hardware = module.hardware_bits(raw)
    if source != hardware:
        mismatch.append({"input": hex(raw), "source": hex(source),
                         "hardware": hex(hardware)})
receipt = {
    "status": "PASS" if not mismatch else "FAIL",
    "cases": len(fixtures), "mismatches": mismatch[:20],
    "source_sha256": hashlib.sha256((base / "truncdfsf2.c").read_bytes()).hexdigest(),
    "implementation_sha256": hashlib.sha256((base / "fp_trunc_impl.inc").read_bytes()).hexdigest(),
    "header_sha256": hashlib.sha256((base / "fp_trunc.h").read_bytes()).hexdigest(),
    "oracle_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "limits": ["Host round-to-nearest hardware comparison, not ARM ABI or stock bootloader body comparison.",
               "NaN payload and signed zero bits are compared exactly for the selected fixtures.",
               "Finite random and threshold fixtures do not exhaust all 2^64 encodings or dynamic FP rounding modes."],
}
(out / "d2f-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({key: receipt[key] for key in ("status", "cases")}))
raise SystemExit(int(bool(mismatch)))
