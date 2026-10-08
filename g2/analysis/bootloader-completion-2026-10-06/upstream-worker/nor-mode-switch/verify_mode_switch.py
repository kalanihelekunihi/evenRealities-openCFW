#!/usr/bin/env python3
"""Differentially execute locked NOR mode-switch instructions and C source."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootv", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

STOP = 0x08000000
SP = 0x2002F000
HANDLE_SLOT = 0x200270DC
ENTRY = 0x420C5C
HOOK_ORIGINAL = {0x4207F4, 0x4205F4, 0x420984, 0x42069E, 0x4176CE}
SOURCE_HOOKS = {
    "opencfw_bl_nor_read_delay": "delay",
    "opencfw_provider_4205f4": "read",
    "opencfw_provider_420984": "wren",
    "opencfw_provider_42069e": "write",
    "opencfw_bl_log": "log",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source=False, segments=(), symbols=None, fixture=None):
        self.source = source
        self.symbols = symbols or {}
        self.fixture = fixture or {}
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.events = []
        self.trace = {}
        self.exec_ranges = []
        self.cpu.mem_map(v.BASE, 0x25000)
        if not source:
            self.cpu.mem_write(v.BASE, v.BLOB.read_bytes())
            self.exec_ranges = [(v.BASE, v.BASE + v.BLOB.stat().st_size)]
        else:
            for seg in segments:
                lo = seg["address"] & ~4095
                hi = (seg["address"] + seg["memory_size"] + 4095) & ~4095
                if lo < STOP or lo >= STOP + 0x10000:
                    self.cpu.mem_map(lo, hi - lo)
                self.cpu.mem_write(seg["address"], seg["data"])
                if seg["flags"] & 1:
                    self.exec_ranges.append((seg["address"], seg["address"] + len(seg["data"])))
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(STOP, 0x10000)
        if source:
            self.cpu.mem_map(0x00011000, 0x1000)
        self.w(HANDLE_SLOT, self.fixture.get("handle", 0x20006000))
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def w(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def u(self, address):
        return struct.unpack("<I", self.cpu.mem_read(address, 4))[0]

    def args(self):
        return [self.cpu.reg_read(reg) for reg in
                (a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                 a.UC_ARM_REG_R2, a.UC_ARM_REG_R3)]

    def cstr(self, ptr):
        out = bytearray()
        while len(out) < 512:
            ch = self.cpu.mem_read(ptr + len(out), 1)[0]
            if ch == 0:
                return out.decode("ascii")
            out.append(ch)
        raise AssertionError(("unterminated string", hex(ptr)))

    def ret(self, value=0):
        self.cpu.reg_write(a.UC_ARM_REG_R0, value & 0xffffffff)
        self.cpu.reg_write(a.UC_ARM_REG_PC, self.cpu.reg_read(a.UC_ARM_REG_LR))

    def hook_kind(self, pc):
        if not self.source:
            return {0x4207F4: "delay", 0x4205F4: "read",
                    0x420984: "wren", 0x42069E: "write",
                    0x4176CE: "log"}.get(pc)
        for symbol, kind in SOURCE_HOOKS.items():
            if (self.symbols[symbol] & ~1) == pc:
                return kind
        return None

    def code(self, uc, pc, size, _):
        if pc == STOP:
            uc.emu_stop()
            return
        kind = self.hook_kind(pc)
        if kind is None:
            assert any(lo <= pc < hi for lo, hi in self.exec_ranges), (
                "source/original execution escaped function or fixture", hex(pc))
            if not self.source:
                self.trace[hex(pc)] = bytes(uc.mem_read(pc, size)).hex()
            return
        r0, r1, r2, r3 = self.args()
        if kind == "delay":
            self.events.append(["delay"])
            self.ret(self.fixture.get("delay_status", 0))
        elif kind == "read":
            ix = sum(event[0] == "read" for event in self.events)
            item = self.fixture.get("reads", [(0, 0)])[min(ix, len(self.fixture.get("reads", [(0, 0)])) - 1)]
            status, value = item
            if status == 0:
                uc.mem_write(r3, bytes([value & 0xff]))
            self.events.append(["read", r0, r1, r2, self.u(uc.reg_read(a.UC_ARM_REG_SP)), status,
                                value & 0xff if status == 0 else None])
            self.ret(status)
        elif kind == "wren":
            result = self.fixture.get("wren_status", 0)
            self.events.append(["wren", result])
            self.ret(result)
        elif kind == "write":
            result = self.fixture.get("write_status", 0)
            self.events.append(["write", r0, r1, r2, self.cpu.mem_read(r3, 1).hex(), result])
            self.ret(result)
        elif kind == "log":
            sp = uc.reg_read(a.UC_ARM_REG_SP)
            args = [r0, self.cstr(r1), self.cstr(r2), self.cstr(r3),
                    self.u(sp), self.cstr(self.u(sp + 4))]
            if args[4] == 0x550:
                args.append(self.cstr(self.u(sp + 8)))
            self.events.append(["log", *args])
            self.ret()

    def run(self, mode):
        self.cpu.reg_write(a.UC_ARM_REG_R0, mode)
        self.cpu.reg_write(a.UC_ARM_REG_R1, 0x11223344)
        self.cpu.reg_write(a.UC_ARM_REG_R2, 0x55667788)
        self.cpu.reg_write(a.UC_ARM_REG_R3, 0x99AABBCC)
        self.cpu.reg_write(a.UC_ARM_REG_SP, SP)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        entry = (self.symbols["opencfw_provider_420c5c"] & ~1) if self.source else ENTRY
        self.cpu.emu_start(entry | 1, STOP + 2, count=100000)
        result = {"return": self.cpu.reg_read(a.UC_ARM_REG_R0),
                  "events": self.events,
                  "sp": self.cpu.reg_read(a.UC_ARM_REG_SP),
                  "callee_saved": [self.cpu.reg_read(reg) for reg in
                                   (a.UC_ARM_REG_R4, a.UC_ARM_REG_R5,
                                    a.UC_ARM_REG_R6, a.UC_ARM_REG_R7,
                                    a.UC_ARM_REG_R8, a.UC_ARM_REG_R9,
                                    a.UC_ARM_REG_R10, a.UC_ARM_REG_R11)]}
        return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert digest(v.BLOB) == v.SHA, "locked image digest changed"
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases = []
    traces = {}
    readseq = lambda *x: {"reads": list(x)}
    fixtures = [
        ("null_handle", 1, {"handle": 0}),
        ("first_read_error", 1, readseq((7, 0))),
        ("already_clear", 0, readseq((0, 0))),
        ("already_set", 1, readseq((0, 0x40))),
        ("reserved_bits_force_rewrite", 0, readseq((0, 0x1c), (0, 0))),
        ("wren_error", 1, {**readseq((0, 0)), "wren_status": 9}),
        ("write_set", 1, readseq((0, 0), (0, 0x40))),
        ("write_clear", 0, readseq((0, 0x40), (0, 0))),
        ("clear_reserved_bits", 1, readseq((0, 0x1c), (0, 0x40))),
        ("write_error", 1, {**readseq((0, 0)), "write_status": 3}),
        ("verify_read_error", 1, readseq((0, 0), (4, 0))),
        ("verify_mismatch_set", 1, readseq((0, 0), (0, 0))),
        ("verify_mismatch_clear", 0, readseq((0, 0x40), (0, 0x40))),
        ("non_boolean_mode_2", 2, readseq((0, 0), (0, 0x40))),
        ("non_boolean_mode_ff", 0xff, readseq((0, 0), (0, 0x40))),
        ("non_boolean_mode_100", 0x100, readseq((0, 0), (0, 0))),
    ]
    for name, mode, fixture in fixtures:
        original = Machine(fixture=fixture)
        source = Machine(True, segments, symbols, fixture)
        left, right = original.run(mode), source.run(mode)
        assert left == right, (name, mode, fixture, left, right)
        traces.update(original.trace)
        cases.append({"name": name, "mode": mode, "fixture": fixture,
                      "result": left})
    used = {int(pc, 0) + offset for pc, code in traces.items()
            for offset in range(len(bytes.fromhex(code)))}
    source_paths = [ROOT / "g2/components/bootloader/nor_mspi_power/serial_mode_switch.c",
                    ROOT / "g2/components/bootloader/nor_mspi_power/serial_mode_switch.h",
                    HERE / "Makefile", HERE / "mode_switch.ld", HERE / Path(__file__).name]
    report = {
        "status": "PASS", "cases": len(cases), "comparisons": cases,
        "original_sha256": v.SHA, "source_elf_sha256": digest(args.elf),
        "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in source_paths},
        "distinct_original_trace_bytes": len(used), "original_trace": traces,
        "limits": [
            "Locked 0x420c5c instructions execute against source compiled as a separate ARM object; delay, status transfer, WREN, status write, and logger are deterministic synthetic callbacks at matching interfaces.",
            "The handle slot is the locked literal target 0x200270dc. NOR status bytes and lower-provider return values are fixture inputs; no physical flash or MSPI hardware is accessed.",
            "The delay provider's raw semantics are not a measured physical duration. This test does not establish serial-mode electrical timing, flash acceptance, XIP execution, full-image linkage, or byte identity.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": len(cases),
                      "distinct_original_trace_bytes": len(used),
                      "source_elf_sha256": report["source_elf_sha256"]}))


if __name__ == "__main__":
    main()
