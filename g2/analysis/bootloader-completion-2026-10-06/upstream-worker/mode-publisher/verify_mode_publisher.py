#!/usr/bin/env python3
"""Compare stock 0x41fadc selector and recovered lower update source."""
import argparse
import hashlib
import importlib.util
import json
import random
import struct
from pathlib import Path

from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE)
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
COMP = ROOT / "g2/components/bootloader/clock_manager"
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
RAM = 0x20000000
POWER_BASE = 0x40010000
POWER_SIZE = 0x1000
STACK = 0x2003F000
R7_SEED = 0x7192A5C3


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source, segments=(), symbols=None):
        self.source = source
        self.symbols = symbols or {}
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.uc.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.uc.mem_map(BASE, 0x25000)
        self.uc.mem_map(RAM, 0x40000)
        self.uc.mem_map(POWER_BASE, POWER_SIZE)
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
        self.trace = {}
        self.reads = []
        self.writes = []
        self.finished = False
        self.case = None
        self.uc.hook_add(UC_HOOK_CODE, self.code)
        self.uc.hook_add(UC_HOOK_MEM_READ, self.mem_read)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self.mem_write)

    def code(self, uc, pc, size, user):
        if STOP <= pc < STOP + 4:
            self.finished = True
            uc.emu_stop()
            return
        if self.source:
            assert any(lo <= pc < hi for lo, hi in self.exec_ranges), (
                "source escaped ELF", hex(pc), self.case
            )
        else:
            assert (0x41FADC <= pc < 0x41FCF6 or
                    0x41D92C <= pc < 0x41D9AA or
                    0x41B8EC <= pc < 0x41B8F4), (
                "stock escaped recovered call closure", hex(pc), self.case
            )
            self.trace[hex(pc)] = bytes(uc.mem_read(pc, size)).hex()

    def mem_read(self, uc, access, address, size, value, user):
        if RAM <= address < RAM + 0x78 or POWER_BASE <= address < POWER_BASE + POWER_SIZE:
            self.reads.append([address, size])

    def mem_write(self, uc, access, address, size, value, user):
        if POWER_BASE <= address < POWER_BASE + POWER_SIZE:
            self.writes.append([address, size, value & ((1 << (8 * size)) - 1)])

    def setup(self, module, mode, seed, primask):
        self.case = (module, mode, seed, primask)
        self.reads.clear()
        self.writes.clear()
        self.finished = False
        rng = random.Random(seed)
        values = [rng.getrandbits(32) for _ in range(30)]
        self.uc.mem_write(RAM, struct.pack("<" + "I" * len(values), *values))
        init_power = bytes(rng.getrandbits(8) for _ in range(POWER_SIZE))
        self.uc.mem_write(POWER_BASE, init_power)
        for reg, value in (
            (a.UC_ARM_REG_R0, module), (a.UC_ARM_REG_R1, mode),
            (a.UC_ARM_REG_R2, 0x22334455), (a.UC_ARM_REG_R3, 0x89ABCDEF),
            (a.UC_ARM_REG_SP, STACK), (a.UC_ARM_REG_LR, STOP | 1),
            (a.UC_ARM_REG_R4, 0x44444444), (a.UC_ARM_REG_R5, 0x55555555),
            (a.UC_ARM_REG_R6, 0x66666666), (a.UC_ARM_REG_R7, R7_SEED),
        ):
            self.uc.reg_write(reg, value)
        self.uc.reg_write(a.UC_ARM_REG_PRIMASK, primask)

    def run(self):
        if self.source:
            start = self.symbols["opencfw_publish_mspi_mode"] & ~1
        else:
            start = 0x41FADC
        self.uc.emu_start(start | 1, STOP + 0x10000, count=200000)
        assert self.finished, ("not returned", self.case,
                               hex(self.uc.reg_read(a.UC_ARM_REG_PC)))
        return {
            "return": self.uc.reg_read(a.UC_ARM_REG_R0),
            "sp": self.uc.reg_read(a.UC_ARM_REG_SP),
            "callee_saved": [self.uc.reg_read(reg) for reg in (
                a.UC_ARM_REG_R4, a.UC_ARM_REG_R5, a.UC_ARM_REG_R6,
                a.UC_ARM_REG_R7)],
            "primask": self.uc.reg_read(a.UC_ARM_REG_PRIMASK),
            "power_sha256": hashlib.sha256(
                self.uc.mem_read(POWER_BASE, POWER_SIZE)
            ).hexdigest(),
            "reads": list(self.reads),
            "writes": list(self.writes),
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert sha(v.BLOB) == v.SHA
    _, segments, symbols = elf.elf_info(args.elf)
    original = Machine(False)
    source = Machine(True, segments, symbols)

    fixtures = []
    seed = 0x41FADC
    for module in (0, 1):
        for mode in range(0x100):
            fixtures.append((module, mode, seed, (module + mode) & 1))
            seed += 1
    for module in (2, 3, 4, 0x100, 0xFFFFFFFF):
        for mode in (0, 1, 4, 6, 0x10, 0x100, 0xFFFFFFFF):
            fixtures.append((module, mode, seed, seed & 1))
            seed += 1
    for module in (0, 1):
        for mode in (0x100, 0x104, 0x106, 0x10A, 0x116, 0x118,
                     0x1FF, 0xFFFFFFFF):
            fixtures.append((module, mode, seed, seed & 1))
            seed += 1

    comparisons = []
    for module, mode, case_seed, primask in fixtures:
        original.setup(module, mode, case_seed, primask)
        source.setup(module, mode, case_seed, primask)
        left = original.run()
        right = source.run()
        assert left == right, (module, hex(mode), case_seed, left, right)
        comparisons.append({"module": module, "mode": hex(mode),
                            "primask_in": primask,
                            "update_calls": len(left["writes"]) // 3,
                            "return": hex(left["return"])})

    tracked = [COMP / "mode_publisher.c", COMP / "mode_publisher.h",
               COMP / "mode_publisher_abi.S",
               COMP / "clock_class_providers.c",
               COMP / "clock_class_providers.h", HERE / "mode_publisher.ld",
               HERE / "Makefile", HERE / "verify_mode_publisher.py"]
    original_bytes = {int(pc, 0) + i for pc, raw in original.trace.items()
                      for i in range(len(bytes.fromhex(raw)))}
    report = {
        "status": "PASS",
        "cases": len(comparisons),
        "original_sha256": v.SHA,
        "source_elf_sha256": sha(args.elf),
        "source_sha256": {str(path.relative_to(ROOT)): sha(path)
                          for path in tracked},
        "distinct_original_instruction_bytes": len(original_bytes),
        "original_trace": original.trace,
        "comparisons": comparisons,
        "limits": [
            "Stock 0x41fadc dispatch and 0x41d92c register update execute as original instructions; source uses the new C selector and compiled existing power-register provider. The 0x41b8ec PRIMASK helper also executes in stock.",
            "The selector source reads runtime values from the exact RAM addresses recovered through the stock literal pool. Fixture words are synthetic; initialization/ownership of those values remains an integration dependency.",
            "Power-register memory is synthetic Unicorn RAM. No physical peripheral behavior, timing, or MSPI mode is established.",
            "The saved-R7 return convention is preserved by a small assembly ABI wrapper; tests compare R0, SP, callee-saved registers, PRIMASK, full modeled register block, read addresses and ordered writes.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": report["cases"],
                      "original_bytes": len(original_bytes)}, indent=2))


if __name__ == "__main__":
    main()
