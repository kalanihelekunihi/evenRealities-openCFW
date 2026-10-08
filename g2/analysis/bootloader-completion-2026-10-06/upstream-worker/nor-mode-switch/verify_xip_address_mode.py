#!/usr/bin/env python3
"""Compare original/source XIP address-mode routines under synthetic NOR calls."""
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
STOP, SP, HANDLE_SLOT = 0x08000000, 0x2002F000, 0x200270DC
SOURCE_HOOKS = {
    "opencfw_provider_4205f4": "read",
    "opencfw_provider_42069e": "command",
    "opencfw_provider_420984": "wren",
    "opencfw_provider_4209c4": "wrdi",
    "opencfw_bl_nor_read_delay": "delay",
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
        self.events, self.trace, self.exec_ranges = [], {}, []
        self.cpu.mem_map(v.BASE, 0x25000)
        if source:
            for seg in segments:
                lo = seg["address"] & ~4095
                hi = (seg["address"] + seg["memory_size"] + 4095) & ~4095
                self.cpu.mem_map(lo, hi - lo)
                self.cpu.mem_write(seg["address"], seg["data"])
                if seg["flags"] & 1:
                    self.exec_ranges.append((seg["address"], seg["address"] + len(seg["data"])))
            self.cpu.mem_map(0x00013000, 0x1000)
        else:
            self.cpu.mem_write(v.BASE, v.BLOB.read_bytes())
            self.exec_ranges = [(v.BASE, v.BASE + v.BLOB.stat().st_size)]
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(STOP, 0x10000)
        self.w(HANDLE_SLOT, self.fixture.get("handle", 0x20006000))
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def w(self, addr, val):
        self.cpu.mem_write(addr, struct.pack("<I", val & 0xffffffff))

    def u(self, addr):
        return struct.unpack("<I", self.cpu.mem_read(addr, 4))[0]

    def args(self):
        return [self.cpu.reg_read(reg) for reg in
                (a.UC_ARM_REG_R0, a.UC_ARM_REG_R1, a.UC_ARM_REG_R2, a.UC_ARM_REG_R3)]

    def cstr(self, ptr):
        out = bytearray()
        while len(out) < 512:
            c = self.cpu.mem_read(ptr + len(out), 1)[0]
            if not c:
                return out.decode("ascii")
            out.append(c)
        raise AssertionError(("unterminated c string", hex(ptr)))

    def ret(self, value=0):
        self.cpu.reg_write(a.UC_ARM_REG_R0, value & 0xffffffff)
        self.cpu.reg_write(a.UC_ARM_REG_PC, self.cpu.reg_read(a.UC_ARM_REG_LR))

    def kind(self, pc):
        if not self.source:
            return {0x4207F4: "delay", 0x4205F4: "read",
                    0x420984: "wren", 0x42069E: "command",
                    0x4209C4: "wrdi", 0x426C10: "memset",
                    0x4176CE: "log"}.get(pc)
        for name, kind in SOURCE_HOOKS.items():
            if self.symbols[name] & ~1 == pc:
                return kind
        return None

    def code(self, uc, pc, size, _):
        if pc == STOP:
            uc.emu_stop()
            return
        kind = self.kind(pc)
        if kind is None:
            assert any(lo <= pc < hi for lo, hi in self.exec_ranges), ("unexpected PC", hex(pc))
            if not self.source:
                self.trace[hex(pc)] = bytes(uc.mem_read(pc, size)).hex()
            return
        r0, r1, r2, r3 = self.args()
        if kind == "memset":
            uc.mem_write(r0, bytes([r1 & 0xff]) * r2)
            self.ret(r0)
        elif kind == "delay":
            ix = sum(e[0] == "delay" for e in self.events)
            values = self.fixture.get("delays", [0])
            status = values[min(ix, len(values) - 1)]
            self.events.append(["delay", status])
            self.ret(status)
        elif kind == "read":
            ix = sum(e[0] == "read" for e in self.events)
            vals = self.fixture.get("reads", [(0, 0)])
            status, value = vals[min(ix, len(vals) - 1)]
            if status == 0:
                uc.mem_write(r3, bytes([value & 0xff]))
            sp = uc.reg_read(a.UC_ARM_REG_SP)
            self.events.append(["read", r0, r1, r2, self.u(sp), status,
                                value & 0xff if status == 0 else None])
            self.ret(status)
        elif kind in ("wren", "wrdi"):
            status = self.fixture.get(kind + "_status", 0)
            self.events.append([kind, status])
            self.ret(status)
        elif kind == "command":
            sp = uc.reg_read(a.UC_ARM_REG_SP)
            length = self.u(sp)
            self.events.append(["command", r0, r1, r2, r3, length,
                                self.cpu.mem_read(r3, min(1, length)).hex() if r3 and length else "",
                                self.fixture.get("command_status", 0)])
            self.ret(self.fixture.get("command_status", 0))
        elif kind == "log":
            sp = uc.reg_read(a.UC_ARM_REG_SP)
            values = [r0, self.cstr(r1), self.cstr(r2), self.cstr(r3),
                      self.u(sp), self.cstr(self.u(sp + 4))]
            self.events.append(["log", *values])
            self.ret()

    def run(self, which, args):
        for reg, value in zip((a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                               a.UC_ARM_REG_R2, a.UC_ARM_REG_R3), args):
            self.cpu.reg_write(reg, value)
        self.cpu.reg_write(a.UC_ARM_REG_SP, SP)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        if self.source:
            entry = self.symbols["opencfw_provider_" + which] & ~1
        else:
            entry = {"420890": 0x420890, "420800": 0x420800}[which]
        self.cpu.emu_start(entry | 1, STOP + 2, count=100000)
        return {"return": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "events": self.events, "sp": self.cpu.reg_read(a.UC_ARM_REG_SP),
                "callee_saved": [self.cpu.reg_read(reg) for reg in
                    (a.UC_ARM_REG_R4, a.UC_ARM_REG_R5, a.UC_ARM_REG_R6, a.UC_ARM_REG_R7,
                     a.UC_ARM_REG_R8, a.UC_ARM_REG_R9, a.UC_ARM_REG_R10, a.UC_ARM_REG_R11)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert digest(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    comparisons, traces = [], {}

    def compare(label, which, params, fixture):
        pair = [Machine(fixture=fixture), Machine(True, segments, symbols, fixture)]
        result = [m.run(which, params) for m in pair]
        assert result[0] == result[1], (label, which, params, fixture, result)
        traces.update(pair[0].trace)
        comparisons.append({"case": label, "function": which, "arguments": params,
                            "fixture": fixture, "result": result[0]})

    for handle in [0, 0x20006000]:
        compare("address_mode_handle", "420890", [0, 0, 0, 0], {"handle": handle})
    for name, fixture in [
        ("first_delay_error", {"delays": [8]}),
        ("wren_error", {"wren_status": 6}),
        ("b7_command_error", {"command_status": 7}),
        ("status_read_error_treated_nonzero", {"reads": [(9, 0)], "wrdi_status": 4}),
        ("status_bit_clear", {"reads": [(0, 0)], "wrdi_status": 0}),
        ("status_bit_set", {"reads": [(0, 0x20)], "wrdi_status": 0}),
        ("status_bit6_only_is_clear", {"reads": [(0, 0x40)], "wrdi_status": 0}),
        ("disable_error", {"reads": [(0, 0x20)], "wrdi_status": 10}),
        ("second_delay_ignored", {"delays": [0, 77], "reads": [(0, 0x20)]}),
    ]:
        compare(name, "420890", [0, 0, 0, 0], fixture)
    for name, fixture in [
        ("checker_read_error", {"reads": [(11, 0)]}),
        ("checker_bit_clear", {"reads": [(0, 0)]}),
        ("checker_bit_set", {"reads": [(0, 0x20)]}),
        ("checker_bit6_only", {"reads": [(0, 0x40)]}),
    ]:
        compare(name, "420800", [0x12345678, 0xabcdef01, 0x2468, 0xdeadbeef], fixture)

    used = {int(pc, 0) + i for pc, raw in traces.items()
            for i in range(len(bytes.fromhex(raw)))}
    sources = [ROOT / "g2/components/bootloader/nor_mspi_power/xip_address_mode.c",
               ROOT / "g2/components/bootloader/nor_mspi_power/xip_address_mode.h",
               HERE / "Makefile.xip", HERE / "xip_address_mode.ld", HERE / Path(__file__).name]
    report = {"status": "PASS", "cases": len(comparisons), "comparisons": comparisons,
              "original_sha256": v.SHA, "source_elf_sha256": digest(args.elf),
              "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources},
              "distinct_original_trace_bytes": len(used), "original_trace": traces,
              "limits": [
                  "The locked 0x420890 and 0x420800 instructions execute against a separately compiled source ELF. Delay, status transfer, command, WREN/WRDI, and logging are controlled exact-interface callbacks; original memset wrapper 0x426c10 is modeled by a byte clear.",
                  "The active handle slot and status bytes are synthetic. The provider reconstructs the firmware's four-byte-mode command/status flow; it does not prove the attached flash accepted the command or that XIP address decoding works on hardware.",
                  "Delay values are raw provider results, not physical units. No hardware, timing, full image, or byte identity is claimed."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": len(comparisons),
                      "distinct_original_trace_bytes": len(used),
                      "source_elf_sha256": report["source_elf_sha256"]}))


if __name__ == "__main__":
    main()
