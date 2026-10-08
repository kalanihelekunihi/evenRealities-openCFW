#!/usr/bin/env python3
"""Differentially execute the locked 0x42c63a leaf and its compiled source."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = 0x410000
ENTRY = 0x42C63A
STOP = 0x08000000
SP = 0x2002F000
MAGIC = 0x01123456
IRQ = 0x40050000
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
LOCKED_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
elf_spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(elf_spec)
elf_spec.loader.exec_module(elf)


class Machine:
    def __init__(self, source, segments=(), symbols=None):
        self.source = source
        self.symbols = symbols or {}
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.cpu.mem_map(BASE, 0x25000)
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(STOP, 0x10000)
        self.cpu.mem_map(IRQ, 0x4000)
        self.writes = []
        self.trace = {}
        self.done = False
        if source:
            for segment in segments:
                lo = segment["address"] & ~0xfff
                hi = (segment["address"] + len(segment["data"]) + 0xfff) & ~0xfff
                if not (BASE <= lo < BASE + 0x25000 or
                        0x20000000 <= lo < 0x20040000 or
                        STOP <= lo < STOP + 0x10000 or
                        IRQ <= lo < IRQ + 0x4000):
                    self.cpu.mem_map(lo, hi - lo)
                self.cpu.mem_write(segment["address"], segment["data"])
        else:
            self.cpu.mem_write(BASE, BLOB.read_bytes())
        self.cpu.hook_add(UC_HOOK_CODE, self.code)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.memwrite)

    def memwrite(self, uc, access, address, size, value, _):
        if IRQ <= address < IRQ + 0x4000:
            self.writes.append([address, size, value & ((1 << (size * 8)) - 1)])

    def code(self, uc, pc, size, _):
        if pc == STOP:
            self.done = True
            uc.emu_stop()
            return
        if not self.source:
            assert BASE <= pc < BASE + 0x25000, ("unexpected original PC", hex(pc))
            self.trace.setdefault(pc, bytes(uc.mem_read(pc, size)).hex())

    def run(self, handle, mask, initial=0):
        self.writes.clear()
        self.done = False
        self.cpu.mem_write(0x20001000, struct.pack("<II", *handle)
                           if handle is not None else b"\0" * 8)
        if handle is not None:
            ptr = 0x20001000
        else:
            ptr = 0
        module = handle[1] if handle is not None else 0
        target = IRQ + module * 0x1000 + 0x200
        self.cpu.mem_write(target, struct.pack("<I", initial))
        for reg, value in ((a.UC_ARM_REG_R0, ptr),
                           (a.UC_ARM_REG_R1, mask),
                           (a.UC_ARM_REG_SP, SP),
                           (a.UC_ARM_REG_LR, STOP | 1)):
            self.cpu.reg_write(reg, value)
        entry = ENTRY if not self.source else self.symbols[
            "opencfw_boot_context_interrupt_enable"] & ~1
        self.cpu.emu_start(entry | 1, STOP + 2, count=1000)
        assert self.done, ("not returned", self.source,
                           hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {"return": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "writes": list(self.writes), "target_value": struct.unpack(
                    "<I", self.cpu.mem_read(target, 4))[0]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    blob = BLOB.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == LOCKED_SHA
    _, segments, symbols = elf.elf_info(args.elf)
    original, source = Machine(False), Machine(True, segments, symbols)
    handles = [None, (0, 0), (MAGIC ^ 1, 0), (MAGIC | 0xfe000000, 0)]
    cases = []
    for handle in handles:
        for mask in (0, 1, 2, 4, 0x80000000, 0xC0000001,
                     0x3FFFFFFF, 0xFFFFFFFF):
            pair = [original.run(handle, mask, 0x100),
                    source.run(handle, mask, 0x100)]
            assert pair[0] == pair[1], (handle, hex(mask), pair)
            cases.append({"handle": handle, "mask": mask,
                          "original": pair[0], "source": pair[1]})
    valid = [(MAGIC, i) for i in range(4)]
    for handle in valid:
        for mask, initial in ((1, 0), (2, 0), (4, 0), (0x24, 0x80),
                              (0x3fffffff, 0x80000000)):
            pair = [original.run(handle, mask, initial),
                    source.run(handle, mask, initial)]
            assert pair[0] == pair[1], (handle, hex(mask), pair)
            if mask == 2:
                assert pair[0]["return"] == 6, pair
            if mask == 4:
                assert pair[0]["return"] == 0, pair
            cases.append({"handle": handle, "mask": mask, "initial": initial,
                          "original": pair[0], "source": pair[1]})
    out = {"status": "PASS", "cases": len(cases), "entry": hex(ENTRY),
           "locked_sha256": LOCKED_SHA,
           "source_elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
           "compiled_source_sha256": hashlib.sha256(
               (HERE / "context_interrupt.c").read_bytes()).hexdigest(),
           "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "linker_script_sha256": hashlib.sha256(
               (HERE / "context_interrupt_module.ld").read_bytes()).hexdigest(),
           "locked_body_sha256": hashlib.sha256(blob[ENTRY - BASE:
                                                     ENTRY - BASE + 56]).hexdigest(),
           "unique_original_instruction_addresses": len(original.trace),
           "original_trace_bytes": sum(len(bytes.fromhex(x))
                                       for x in original.trace.values()),
           "limits": ["Only the bounded handle/mask/module cases in this test were exercised.",
                      "MMIO registers are Unicorn RAM, not physical interrupt-controller behavior.",
                      "This leaf test does not establish whole-callback or whole-image equivalence."],
           "comparisons": cases}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "comparisons"}, indent=2))


if __name__ == "__main__":
    main()
