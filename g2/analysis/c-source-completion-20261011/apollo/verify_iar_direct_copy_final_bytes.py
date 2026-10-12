#!/usr/bin/env python3
"""Bounded locked IAR copy final-byte oracle for nonoverlapping SRAM spans."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / "g2/components/bootloader/update_core/verify.py"
spec = importlib.util.spec_from_file_location("boot_verify", P)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
assert v.sha(v.BLOB) == v.SHA
v.ENTRIES["iar_copy"] = 0x4156ac

machine = v.Machine()
source = 0x20008000
destination = 0x20009000
cases = 0
for count in (0, 1, 2, 3, 4, 7, 8, 15, 16, 17, 23, 24, 28, 32, 60, 84):
    for sa in range(4):
        for da in range(4):
            payload = bytes((i * 29 + count * 7 + sa) & 255 for i in range(128))
            machine.cpu.mem_write(source, b"\x6d" * 140)
            machine.cpu.mem_write(destination, b"\xa5" * 140)
            machine.cpu.mem_write(source + sa, payload)
            machine.run("iar_copy", [destination + da, source + sa, count])
            got = bytes(machine.cpu.mem_read(destination, 140))
            want = bytearray(b"\xa5" * 140)
            want[da:da + count] = payload[:count]
            assert got == want, (count, sa, da)
            cases += 1
print(json.dumps({
    "status": "PASS_BOUNDED_IAR_COPY_FINAL_BYTES",
    "cases": cases,
    "locked_image_sha256": v.SHA,
    "source_helper_sha256": hashlib.sha256((ROOT / "g2/components/bootloader/initializer_callbacks/iar_memory_native/memory.c").read_bytes()).hexdigest(),
    "limits": "Nonoverlapping mapped SRAM spans and final bytes only; selected caller ranges, write order, overlap, and concurrent readers remain separate.",
}))
