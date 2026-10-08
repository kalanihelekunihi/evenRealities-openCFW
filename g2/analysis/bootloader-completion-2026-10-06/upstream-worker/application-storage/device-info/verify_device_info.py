#!/usr/bin/env python3
"""Differentially execute stock 0x41d294 vs readable source under Unicorn."""
import argparse
import hashlib
import importlib.util
import json
import random
import struct
from pathlib import Path

from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_CODE, UC_HOOK_MEM_READ)
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
COMP = ROOT / "g2/components/bootloader/application_storage"
spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)
specv = importlib.util.spec_from_file_location(
    "bootv", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(specv)
specv.loader.exec_module(v)

IMAGE_BASE = v.BASE
IMAGE = v.BLOB
IMAGE_SHA = v.SHA
STOP = 0x08000000
SOURCE_DELAY = 0x08000200
OUTPUT = 0x20001000
STACK = 0x2003F000
STATUS = 0x40020000
RANGE_TABLE = 0x43401C
CLOCK_TABLE = 0x433754
DEBUG_BASE = 0xE00F0000
DEBUG_REGS = (0xE00FEFE0, 0xE00FEFE4, 0xE00FEFE8, 0xE00FEFEC,
              0xE00FEFFC, 0xE00FEFF8, 0xE00FEFF4, 0xE00FEFF0)
STATUS_REGS = tuple(STATUS + offset for offset in range(0, 0x18, 4))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source, segments=(), symbols=None):
        self.source = source
        self.symbols = symbols or {}
        self.finished = False
        self.trace = {}
        self.reads = []
        self.delays = []
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.uc.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.uc.mem_map(IMAGE_BASE, 0x25000)
        if source:
            self.exec_ranges = []
            for segment in segments:
                lo = segment["address"] & ~0xfff
                hi = (segment["address"] + segment["memory_size"] + 0xfff) & ~0xfff
                if not (IMAGE_BASE <= lo < IMAGE_BASE + 0x25000):
                    self.uc.mem_map(lo, hi-lo)
                self.uc.mem_write(segment["address"], segment["data"])
                if segment["flags"] & 1:
                    self.exec_ranges.append((segment["address"],
                                             segment["address"] + len(segment["data"])))
        else:
            self.uc.mem_write(IMAGE_BASE, IMAGE.read_bytes())
            self.exec_ranges = [(IMAGE_BASE, IMAGE_BASE + IMAGE.stat().st_size)]
        self.uc.mem_map(0x20000000, 0x40000)
        self.uc.mem_map(0x40020000, 0x1000)
        self.uc.mem_map(DEBUG_BASE, 0x10000)
        self.uc.mem_map(STOP, 0x10000)
        self.uc.hook_add(UC_HOOK_CODE, self.code)
        self.uc.hook_add(UC_HOOK_MEM_READ, self.mem_read)

    def word(self, address):
        return struct.unpack("<I", self.uc.mem_read(address, 4))[0]

    def put_word(self, address, value):
        self.uc.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def mem_read(self, uc, access, address, size, value, user):
        if address in STATUS_REGS or address in DEBUG_REGS or \
           address in (RANGE_TABLE, RANGE_TABLE+2, RANGE_TABLE+4, RANGE_TABLE+6) or \
           CLOCK_TABLE <= address < CLOCK_TABLE+24:
            self.reads.append((address, size))

    def code(self, uc, pc, size, user):
        if pc == STOP:
            self.finished = True
            uc.emu_stop()
            return
        if pc == SOURCE_DELAY or (not self.source and pc == 0x41F9E6):
            amount = uc.reg_read(a.UC_ARM_REG_R0)
            self.delays.append(amount)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if self.source:
            assert any(lo <= pc < hi for lo, hi in self.exec_ranges), \
                ("source executed outside source ELF", hex(pc))
        else:
            assert 0x41D294 <= pc < 0x41D3E4, \
                ("stock escaped bounded function", hex(pc))
            self.trace[hex(pc)] = bytes(uc.mem_read(pc, size)).hex()

    def setup(self, values):
        self.finished = False
        self.trace.clear()
        self.reads.clear()
        self.delays.clear()
        self.uc.mem_write(OUTPUT, b"\xcc" * 64)
        for i, value in enumerate(values["status"]):
            self.put_word(STATUS + i*4, value)
        for address, value in zip(DEBUG_REGS, values["debug"]):
            self.put_word(address, value)
        self.uc.reg_write(a.UC_ARM_REG_R0, OUTPUT)
        self.uc.reg_write(a.UC_ARM_REG_R1, 0)
        self.uc.reg_write(a.UC_ARM_REG_SP, STACK)
        self.uc.reg_write(a.UC_ARM_REG_LR, STOP | 1)

    def run(self):
        if self.source:
            start = self.symbols["opencfw_boot_device_info_initialize"] & ~1
        else:
            start = 0x41D294
        self.uc.emu_start(start | 1, STOP + 0x10000, count=100000)
        assert self.finished, (self.source, "execution did not return",
                               hex(self.uc.reg_read(a.UC_ARM_REG_PC)))
        return {
            "record": bytes(self.uc.mem_read(OUTPUT, 64)).hex(),
            "reads": list(self.reads), "delays": list(self.delays),
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert sha(IMAGE) == IMAGE_SHA
    _, segments, symbols = elf.elf_info(args.elf)
    blob = IMAGE.read_bytes()
    cases = []
    trace = {}
    rng = random.Random(0x41D294)

    scenarios = []
    for range_mode in range(4):
        for clock_mode in range(4):
            for _ in range(4):
                status = [rng.getrandbits(32) for _ in range(6)]
                status[5] = ((status[5] & ~0x0f) | (clock_mode & 3) |
                             ((range_mode & 3) << 2))
                scenarios.append({"status": status,
                                  "debug": [rng.getrandbits(32) for _ in DEBUG_REGS],
                                  "tag": [range_mode, clock_mode]})
    # Include mode transitions with all unrelated status bits toggled.
    for raw_mode in range(16):
        status = [rng.getrandbits(32) for _ in range(6)]
        status[5] = ((rng.getrandbits(32) & ~0x0f) | raw_mode)
        scenarios.append({"status": status,
                          "debug": [rng.getrandbits(32) for _ in DEBUG_REGS],
                          "tag": ["raw", raw_mode]})

    for case_id, fixture in enumerate(scenarios):
        original = Machine(False)
        source = Machine(True, segments, symbols)
        # Table data must come from the source ELF; it cannot fall back to the
        # original image, whose non-code region is zero-filled in this machine.
        assert bytes(source.uc.mem_read(RANGE_TABLE, 8)) == \
            blob[RANGE_TABLE-IMAGE_BASE:RANGE_TABLE-IMAGE_BASE+8]
        assert bytes(source.uc.mem_read(CLOCK_TABLE, 24)) == \
            blob[CLOCK_TABLE-IMAGE_BASE:CLOCK_TABLE-IMAGE_BASE+24]
        for machine in (original, source):
            machine.setup(fixture)
        got = [machine.run() for machine in (original, source)]
        assert got[0] == got[1], (case_id, fixture["tag"],
                                  {key: (got[0][key], got[1][key])
                                   for key in got[0] if got[0][key] != got[1][key]})
        assert got[0]["delays"] == [10] * 10, (case_id, got[0]["delays"])
        trace.update(original.trace)
        cases.append({"tag": fixture["tag"],
                      "output_sha256": hashlib.sha256(
                          bytes.fromhex(got[0]["record"])).hexdigest(),
                      "delay_calls": got[0]["delays"],
                      "ordered_reads": [[hex(address), size]
                                        for address, size in got[0]["reads"]]})

    tracked = [COMP / "device_info.c", COMP / "device_info.h",
               HERE / "device_info.ld", HERE / "verify_device_info.py",
               HERE / "Makefile"]
    distinct = {int(pc, 0) + offset for pc, data in trace.items()
                for offset in range(len(bytes.fromhex(data)))}
    report = {
        "status": "PASS", "cases": len(cases),
        "distinct_original_instruction_bytes": len(distinct),
        "original_sha256": IMAGE_SHA, "source_elf_sha256": sha(args.elf),
        "source_sha256": {str(path.relative_to(ROOT)): sha(path)
                          for path in tracked},
        "function": {"stock": "0x41d294", "source": hex(
            symbols["opencfw_boot_device_info_initialize"] & ~1)},
        "comparison": cases,
        "limits": [
            "Stock helper 0x41f9e6 is intercepted as an ordered 10-microsecond delay service; actual 0x41d1c0 wait/FPU timing is not executed.",
            "MMIO at 0x40020000 and core-debug addresses 0xe00fefe0..0xe00feffc is synthetic Unicorn memory.",
            "The source references locked tables at 0x43401c and 0x433754; only their exact image bytes are supplied as source-test data.",
            "This verifies the snapshot helper only; it does not establish hardware timing, whole-image completion, or byte identity.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in
                      ("status", "cases", "distinct_original_instruction_bytes")},
                     indent=2))


if __name__ == "__main__":
    main()
