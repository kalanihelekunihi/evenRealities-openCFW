#!/usr/bin/env python3
"""Differentially execute locked 36x32 timing scan and source implementation."""
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
STOP, SP, HANDLE_SLOT, TABLE, OUTPUT = 0x08000000, 0x2002F000, 0x200270DC, 0x20000244, 0x20003000
SOURCE_HOOKS = {
    "opencfw_hal_mspi_control": "control",
    "opencfw_bl_mspi_status_transfer": "transfer",
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
        self.control_index = 0
        self.transfer_index = 0
        self.cpu.mem_map(v.BASE, 0x25000)
        if source:
            for seg in segments:
                lo = seg["address"] & ~4095
                hi = (seg["address"] + seg["memory_size"] + 4095) & ~4095
                self.cpu.mem_map(lo, hi - lo)
                self.cpu.mem_write(seg["address"], seg["data"])
                if seg["flags"] & 1:
                    self.exec_ranges.append((seg["address"], seg["address"] + len(seg["data"])))
            self.cpu.mem_map(0x0001F000, 0x1000)
        else:
            self.cpu.mem_write(v.BASE, v.BLOB.read_bytes())
            self.exec_ranges = [(v.BASE, v.BASE + v.BLOB.stat().st_size)]
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(STOP, 0x10000)
        self.w(HANDLE_SLOT, self.fixture.get("handle", 0x20006000))
        table = self.fixture["profiles"]
        assert len(table) == 216
        self.cpu.mem_write(TABLE, table)
        self.cpu.mem_write(OUTPUT, b"\xaa" * 8)
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def w(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def u(self, address):
        return struct.unpack("<I", self.cpu.mem_read(address, 4))[0]

    def args(self):
        return [self.cpu.reg_read(reg) for reg in
                (a.UC_ARM_REG_R0, a.UC_ARM_REG_R1, a.UC_ARM_REG_R2, a.UC_ARM_REG_R3)]

    def cstr(self, ptr):
        out = bytearray()
        while len(out) < 512:
            ch = self.cpu.mem_read(ptr + len(out), 1)[0]
            if ch == 0:
                return out.decode("ascii")
            out.append(ch)
        raise AssertionError(("unterminated c string", hex(ptr)))

    def ret(self, value=0):
        self.cpu.reg_write(a.UC_ARM_REG_R0, value & 0xffffffff)
        self.cpu.reg_write(a.UC_ARM_REG_PC, self.cpu.reg_read(a.UC_ARM_REG_LR))

    def kind(self, pc):
        if not self.source:
            return {0x426C10: "memset", 0x4251C0: "control",
                    0x4205F4: "transfer", 0x4176CE: "log"}.get(pc)
        for symbol, kind in SOURCE_HOOKS.items():
            if self.symbols[symbol] & ~1 == pc:
                return kind
        return None

    def code(self, uc, pc, size, _):
        if pc == STOP:
            uc.emu_stop()
            return
        kind = self.kind(pc)
        if kind is None:
            assert any(lo <= pc < hi for lo, hi in self.exec_ranges), ("unexpected execution", hex(pc))
            if not self.source:
                self.trace[hex(pc)] = bytes(uc.mem_read(pc, size)).hex()
            return
        r0, r1, r2, r3 = self.args()
        if kind == "memset":
            uc.mem_write(r0, bytes([r1 & 0xff]) * r2)
            self.ret(r0)
        elif kind == "control":
            raw = bytes(uc.mem_read(r2, 6))
            self.events.append(["control", r0, r1, raw.hex()])
            self.control_index += 1
            self.ret(self.fixture.get("control_status", 0))
        elif kind == "transfer":
            sp = uc.reg_read(a.UC_ARM_REG_SP)
            length = self.u(sp)
            index = self.transfer_index
            self.transfer_index += 1
            errors = self.fixture.get("read_errors", {})
            status = errors.get(index, 0)
            masks = self.fixture["masks"]
            row, step = index // 32, index % 32
            accepted = bool((masks[row] >> step) & 1)
            # Stock and source transfer fixtures model the three JEDEC bytes in
            # one little-endian word, then use the provider's byte conversion.
            raw = 0x00C23925 if accepted else 0x00ADBEEF
            if status == 0:
                uc.mem_write(r3, struct.pack("<I", raw))
            self.events.append(["jedec", r0, r1, r2, length, status,
                                raw & 0x00ffffff if status == 0 else None])
            self.ret(status)
        elif kind == "log":
            sp = uc.reg_read(a.UC_ARM_REG_SP)
            line = self.u(sp)
            count = {0x1C6: 2, 0x1CD: 6, 0x1D3: 1, 0x2D8: 0}.get(line)
            assert count is not None, ("unexpected timing logger line", hex(line))
            values = [r0, self.cstr(r1), self.cstr(r2), self.cstr(r3), line,
                      self.cstr(self.u(sp + 4))]
            values.extend(self.u(sp + 8 + i * 4) for i in range(count))
            self.events.append(["log", *values])
            self.ret()

    def run(self):
        self.cpu.reg_write(a.UC_ARM_REG_R0, OUTPUT)
        self.cpu.reg_write(a.UC_ARM_REG_R1, 0x11223344)
        self.cpu.reg_write(a.UC_ARM_REG_R2, 0x55667788)
        self.cpu.reg_write(a.UC_ARM_REG_R3, 0x99AABBCC)
        self.cpu.reg_write(a.UC_ARM_REG_SP, SP)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        entry = self.symbols["opencfw_provider_420002"] & ~1 if self.source else 0x420002
        self.cpu.emu_start(entry | 1, STOP + 2, count=10000000)
        return {"return": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "output": bytes(self.cpu.mem_read(OUTPUT, 6)).hex(),
                "control_calls": self.control_index,
                "transfer_calls": self.transfer_index,
                "events": self.events,
                "sp": self.cpu.reg_read(a.UC_ARM_REG_SP),
                "callee_saved": [self.cpu.reg_read(reg) for reg in
                    (a.UC_ARM_REG_R4, a.UC_ARM_REG_R5, a.UC_ARM_REG_R6, a.UC_ARM_REG_R7,
                     a.UC_ARM_REG_R8, a.UC_ARM_REG_R9, a.UC_ARM_REG_R10, a.UC_ARM_REG_R11)]}


def profiles():
    out = bytearray()
    for i in range(36):
        out.extend(((i + 3) & 0xff, (i + 7) & 0xff, (i * 3 + 1) & 0xff,
                    (i * 5 + 2) & 0xff, 0x55, (i * 7 + 8) & 0xff))
    return bytes(out)


def masks_for(kind):
    masks = [0] * 36
    if kind == "all_hit":
        return [0xffffffff] * 36
    if kind == "prefix_tie":
        masks[3] = sum(1 << bit for bit in [31, 0, 1, 2, 3, 4])
        masks[4] = 0x1f
        masks[8] = 0x7
        return masks
    if kind == "multiple_windows":
        masks[2] = 0x00000FF0
        masks[5] = 0x00003C3F
        masks[9] = 0x001F0000
        masks[13] = 0x0000001F
        return masks
    return masks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--profile-table", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert digest(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    summaries, traces = [], {}
    authentic_profiles = args.profile_table.read_bytes()
    assert len(authentic_profiles) == 216
    fixtures = [
        ("all_miss", masks_for("all_miss"), {}, profiles()),
        ("all_hit_control_errors_ignored", masks_for("all_hit"), {"control_status": 9}, profiles()),
        ("prefix_tie_wrap_center", masks_for("prefix_tie"), {}, profiles()),
        ("multiple_windows", masks_for("multiple_windows"), {}, profiles()),
        ("read_failures_do_not_set_bits", masks_for("all_hit"),
         {"read_errors": {0: 7, 67: 3, 1151: 11}}, profiles()),
        ("official_runtime_table", masks_for("prefix_tie"), {}, authentic_profiles),
    ]
    for name, masks, opts, profile_bytes in fixtures:
        fixture = {"profiles": profile_bytes, "masks": masks, **opts}
        pair = [Machine(fixture=fixture), Machine(True, segments, symbols, fixture)]
        values = [m.run() for m in pair]
        assert {k: v for k, v in values[0].items() if k != "events"} == \
               {k: v for k, v in values[1].items() if k != "events"}, (name, values)
        assert values[0]["events"] == values[1]["events"], (name, "provider trace mismatch")
        traces.update(pair[0].trace)
        ev = values[0]["events"]
        summaries.append({"case": name, "return": values[0]["return"],
            "output": values[0]["output"], "control_calls": values[0]["control_calls"],
            "transfer_calls": values[0]["transfer_calls"],
            "event_count": len(ev),
            "event_sha256": hashlib.sha256(json.dumps(ev, separators=(",", ":")).encode()).hexdigest(),
            "log_events": [x for x in ev if x[0] == "log"],
            "sp": values[0]["sp"], "callee_saved": values[0]["callee_saved"]})

    used = {int(pc, 0) + i for pc, raw in traces.items()
            for i in range(len(bytes.fromhex(raw)))}
    source_paths = [ROOT / "g2/components/bootloader/nor_mspi_power/timing_scan.c",
        ROOT / "g2/components/bootloader/nor_mspi_power/timing_scan.h",
        ROOT / "g2/components/bootloader/nor_init/nor_init.c",
        HERE / "Makefile.scan", HERE / "timing_scan.ld", HERE / Path(__file__).name,
        HERE / "extract_profile_table.py"]
    report = {"status": "PASS", "cases": len(summaries), "comparisons": summaries,
        "original_sha256": v.SHA, "source_elf_sha256": digest(args.elf),
        "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in source_paths},
        "runtime_profile_table_sha256": digest(args.profile_table),
        "distinct_original_trace_bytes": len(used), "original_trace": traces,
        "limits": [
            "Locked 0x420002 instructions execute against compiled source. The six-byte profile table at runtime address 0x20000244 is the same synthetic input on both sides; this profile validates generic scan logic, not how startup populates this RAM table.",
            "HAL control and JEDEC transfer use synthetic callbacks. JEDEC values model expected ID 0x2539c2 or mismatch; no physical flash/MSPI, power, or actual calibration is exercised.",
            "Logger calls are captured from synthetic hooks. Delay and electrical timing are absent from the scan itself. No complete image or byte identity claim."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": len(summaries),
        "distinct_original_trace_bytes": len(used), "source_elf_sha256": report["source_elf_sha256"]}))


if __name__ == "__main__":
    main()
