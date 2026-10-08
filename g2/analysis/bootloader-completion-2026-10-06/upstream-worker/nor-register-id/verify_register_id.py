#!/usr/bin/env python3
"""Compare stock 0x41d90e against its C source over the full accepted range."""
import argparse
import hashlib
import importlib.util
import json
import random
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ, arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
COMP = ROOT / "g2/components/bootloader/nor_mspi_init"
spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py"
)
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)
spec = importlib.util.spec_from_file_location(
    "bootv", ROOT / "g2/components/bootloader/update_core/verify.py"
)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

BASE = 0x410000
STOP = 0x08000000
REGISTER_BASE = 0x40010000
OUTPUT = 0x20001000
STACK = 0x2003F000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source, segments=(), symbols=None):
        self.source = source
        self.symbols = symbols or {}
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.uc.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.uc.mem_map(BASE, 0x25000)
        self.uc.mem_map(0x20000000, 0x40000)
        self.uc.mem_map(REGISTER_BASE, 0x1000)
        self.uc.mem_map(STOP, 0x10000)
        self.exec_ranges = []
        if source:
            for segment in segments:
                self.uc.mem_write(segment["address"], segment["data"])
                if segment["flags"] & 1:
                    self.exec_ranges.append((segment["address"],
                                             segment["address"] + len(segment["data"])))
        else:
            self.uc.mem_write(BASE, v.BLOB.read_bytes())
            self.exec_ranges = [(BASE, BASE + v.BLOB.stat().st_size)]
        self.finished = False
        self.reads = []
        self.trace = {}
        self.uc.hook_add(UC_HOOK_CODE, self.code)
        self.uc.hook_add(UC_HOOK_MEM_READ, self.mem_read)

    def mem_read(self, uc, access, address, size, value, user):
        if REGISTER_BASE <= address < REGISTER_BASE + 0x1000:
            self.reads.append([address, size])

    def code(self, uc, pc, size, user):
        if STOP <= pc < STOP + 4:
            self.finished = True
            uc.emu_stop()
            return
        if self.source:
            assert any(lo <= pc < hi for lo, hi in self.exec_ranges), (
                "source escaped its ELF", hex(pc), self.case
            )
        else:
            assert 0x41D90E <= pc < 0x41D92C, ("stock escaped function", hex(pc))
            self.trace[hex(pc)] = bytes(uc.mem_read(pc, size)).hex()

    def run(self, register_id, out_pointer):
        self.case = (register_id, out_pointer)
        self.finished = False
        self.reads.clear()
        self.uc.mem_write(OUTPUT, struct.pack("<I", 0xD15EA5ED))
        for reg, value in ((a.UC_ARM_REG_R0, register_id),
                           (a.UC_ARM_REG_R1, out_pointer)):
            self.uc.reg_write(reg, value)
        self.uc.reg_write(a.UC_ARM_REG_SP, STACK)
        self.uc.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        start = 0x41D90E if not self.source else (
            self.symbols["opencfw_read_mspi_register_id"] & ~1
        )
        self.uc.emu_start(start | 1, STOP + 0x10000, count=10000)
        assert self.finished, ("function did not return", self.case,
                               hex(self.uc.reg_read(a.UC_ARM_REG_PC)))
        return {
            "status": self.uc.reg_read(a.UC_ARM_REG_R0),
            "output": struct.unpack("<I", self.uc.mem_read(OUTPUT, 4))[0],
            "reads": list(self.reads),
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert sha(v.BLOB) == v.SHA
    _, segments, symbols = elf.elf_info(args.elf)
    stock = Machine(False)
    source = Machine(True, segments, symbols)

    rng = random.Random(0x41D90E)
    table = [rng.getrandbits(32) for _ in range(0xE0)]
    stock.uc.mem_write(REGISTER_BASE, struct.pack("<" + "I" * len(table), *table))
    source.uc.mem_write(REGISTER_BASE, struct.pack("<" + "I" * len(table), *table))

    cases = []
    for register_id in range(0xE0):
        original = stock.run(register_id, OUTPUT)
        reconstructed = source.run(register_id, OUTPUT)
        assert original == reconstructed == {
            "status": 0, "output": table[register_id],
            "reads": [[REGISTER_BASE + register_id * 4, 4]],
        }, (hex(register_id), original, reconstructed)
        cases.append({"register_id": register_id, "value": hex(table[register_id]),
                      "read_address": hex(REGISTER_BASE + register_id * 4),
                      "width": 4})

    edge_cases = []
    for register_id, out_pointer, expected in (
        (0xE0, OUTPUT, 5), (0xFF, OUTPUT, 5), (0xFFFFFFFF, OUTPUT, 5),
        (0, 0, 6), (0xDF, 0, 6), (0xE0, 0, 5),
    ):
        original = stock.run(register_id, out_pointer)
        reconstructed = source.run(register_id, out_pointer)
        assert original == reconstructed and original["status"] == expected
        assert original["reads"] == []
        edge_cases.append({"register_id": hex(register_id),
                           "out_pointer": hex(out_pointer),
                           "status": expected})

    tracked = [COMP / "register_id.c", COMP / "register_id.h",
               HERE / "register_id.ld", HERE / "Makefile",
               HERE / "verify_register_id.py"]
    trace_bytes = {int(pc, 0) + i for pc, raw in stock.trace.items()
                   for i in range(len(bytes.fromhex(raw)))}
    report = {
        "status": "PASS",
        "valid_cases": len(cases),
        "edge_cases": edge_cases,
        "distinct_original_instruction_bytes": len(trace_bytes),
        "original_sha256": v.SHA,
        "source_elf_sha256": sha(args.elf),
        "source_sha256": {str(path.relative_to(ROOT)): sha(path)
                          for path in tracked},
        "original_trace": stock.trace,
        "limits": [
            "All 224 accepted IDs execute original/source instructions and match a deterministic synthetic 32-bit register value at 0x40010000 + ID*4.",
            "Boundary fixtures confirm stock returns 5 for IDs >=0xe0 before checking a null output pointer, and returns 6 for null output with an in-range ID; these paths perform no register read.",
            "The locked literal establishes the base address 0x40010000. The local Apollo510 SDK subset does not name this block, so no peripheral or register semantic label is assigned.",
            "MMIO is synthetic Unicorn RAM. No hardware read or behavior is established.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "valid_cases": len(cases),
                      "edge_cases": len(edge_cases),
                      "original_bytes": len(trace_bytes)}, indent=2))


if __name__ == "__main__":
    main()
