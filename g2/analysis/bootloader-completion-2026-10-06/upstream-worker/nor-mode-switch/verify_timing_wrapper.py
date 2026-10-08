#!/usr/bin/env python3
"""Compare stock 0x4201ba wrapper to linked source scan/core/wrapper."""
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
STOP, SP, HANDLE_SLOT, TABLE, CURRENT = 0x08000000, 0x2002F000, 0x200270DC, 0x20000244, 0x2000023C
SOURCE_HOOKS = {
    "opencfw_hal_mspi_control": "control",
    "opencfw_bl_mspi_status_transfer": "transfer",
    "opencfw_bl_log": "log",
    "opencfw_bl_clear": "clear",
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
        self.w(HANDLE_SLOT, 0x20006000)
        self.cpu.mem_write(TABLE, self.fixture["profiles"])
        self.cpu.mem_write(CURRENT, b"\x91\x82\x73\x64\x55\x46\x37\x28")
        self.cpu.mem_write(SP - 0x10, b"\x10\x21\x32\x43\x54\x65" + self.fixture["tail"])
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
            if not ch:
                return out.decode("ascii")
            out.append(ch)
        raise AssertionError(("unterminated string", hex(ptr)))

    def ret(self, value=0):
        self.cpu.reg_write(a.UC_ARM_REG_R0, value & 0xffffffff)
        self.cpu.reg_write(a.UC_ARM_REG_PC, self.cpu.reg_read(a.UC_ARM_REG_LR))

    def kind(self, pc):
        if not self.source:
            return {0x426C10: "clear", 0x4251C0: "control",
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
        if kind == "clear":
            uc.mem_write(r0, bytes([r1 & 0xff]) * r2)
            self.ret(r0)
        elif kind == "control":
            self.events.append(["control", r0, r1, bytes(uc.mem_read(r2, 6)).hex()])
            self.control_index += 1
            self.ret(0)
        elif kind == "transfer":
            sp = uc.reg_read(a.UC_ARM_REG_SP)
            length = self.u(sp)
            i = self.transfer_index
            self.transfer_index += 1
            accepted = bool((self.fixture["mask"] >> (i % 32)) & 1)
            raw = 0x00C23925 if accepted else 0x00ADBEEF
            uc.mem_write(r3, struct.pack("<I", raw))
            self.events.append(["jedec", r0, r1, r2, length, raw & 0xffffff])
            self.ret(0)
        elif kind == "log":
            sp = uc.reg_read(a.UC_ARM_REG_SP)
            line = self.u(sp)
            count = {0x1C6: 2, 0x1CD: 6, 0x1D3: 1, 0x1F3: 6,
                     0x1FB: 6}.get(line, 0 if line == 0x2D8 else None)
            assert count is not None, ("unexpected logger line", hex(line))
            values = [r0, self.cstr(r1), self.cstr(r2), self.cstr(r3), line,
                      self.cstr(self.u(sp + 4))]
            values.extend(self.u(sp + 8 + i * 4) for i in range(count))
            self.events.append(["log", *values])
            self.ret()

    def run(self):
        self.cpu.reg_write(a.UC_ARM_REG_R0, 0)
        self.cpu.reg_write(a.UC_ARM_REG_R1, 0x11223344)
        self.cpu.reg_write(a.UC_ARM_REG_R2, 0x55667788)
        self.cpu.reg_write(a.UC_ARM_REG_R3, 0x99AABBCC)
        self.cpu.reg_write(a.UC_ARM_REG_SP, SP)
        self.cpu.reg_write(a.UC_ARM_REG_R7, 0xabcdef01)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        entry = self.symbols["opencfw_provider_4201ba"] & ~1 if self.source else 0x4201BA
        self.cpu.emu_start(entry | 1, STOP + 2, count=10000000)
        return {"return": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "current_timing_8": bytes(self.cpu.mem_read(CURRENT, 8)).hex(),
                "control_calls": self.control_index, "transfer_calls": self.transfer_index,
                "events": self.events, "sp": self.cpu.reg_read(a.UC_ARM_REG_SP),
                "callee_saved": [self.cpu.reg_read(reg) for reg in
                    (a.UC_ARM_REG_R4, a.UC_ARM_REG_R5, a.UC_ARM_REG_R6, a.UC_ARM_REG_R7,
                     a.UC_ARM_REG_R8, a.UC_ARM_REG_R9, a.UC_ARM_REG_R10, a.UC_ARM_REG_R11)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--profile-table", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert digest(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    profiles = args.profile_table.read_bytes()
    assert len(profiles) == 216
    fixtures = [("all_pass_preserve_a55a", 0xffffffff, b"\xa5\x5a"),
                ("all_miss_preserve_3cc3", 0, b"\x3c\xc3"),
                ("tie_wrap_center", 0x8000003f, b"\x69\x96")]
    summaries, traces = [], {}
    for label, mask, tail in fixtures:
        fixture = {"profiles": profiles, "mask": mask, "tail": tail}
        pair = [Machine(fixture=fixture), Machine(True, segments, symbols, fixture)]
        values = [m.run() for m in pair]
        assert values[0] == values[1], (label, {k: [x.get(k) for x in values]
                                               for k in values[0] if values[0][k] != values[1][k]})
        traces.update(pair[0].trace)
        events = values[0]["events"]
        summaries.append({"case": label, "current_timing_8": values[0]["current_timing_8"],
            "control_calls": values[0]["control_calls"], "transfer_calls": values[0]["transfer_calls"],
            "event_count": len(events), "events_sha256": hashlib.sha256(
                json.dumps(events, separators=(",", ":")).encode()).hexdigest(),
            "logs": [event for event in events if event[0] == "log"],
            "sp": values[0]["sp"], "callee_saved": values[0]["callee_saved"]})
    used = {int(pc, 0) + i for pc, raw in traces.items()
            for i in range(len(bytes.fromhex(raw)))}
    sources = [ROOT / "g2/components/bootloader/nor_mspi_power/timing_scan.c",
        ROOT / "g2/components/bootloader/nor_commands/nor_commands.c",
        ROOT / "g2/components/bootloader/nor_commands/nor_timing_wrapper.S",
        ROOT / "g2/components/bootloader/nor_init/nor_init.c",
        HERE / "Makefile.wrapper", HERE / "timing_wrapper.ld", HERE / Path(__file__).name]
    report = {"status": "PASS", "cases": len(summaries), "comparisons": summaries,
        "original_sha256": v.SHA, "source_elf_sha256": digest(args.elf),
        "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources},
        "runtime_profile_table_sha256": digest(args.profile_table),
        "distinct_original_trace_bytes": len(used), "original_trace": traces,
        "limits": [
            "This profile links and executes the source 0x4201ba assembly ABI wrapper, nor_commands.c core, timing_scan.c, and nor_init.c JEDEC helper together against original 0x4201ba and the original full timing scan. HAL control and JEDEC I/O are synthetic deterministic callbacks; no physical flash/MSPI is exercised.",
            "The six-byte scan table is extracted by executing the locked startup scatter expander for record 0x433104 and is seeded identically on both sides. This locates the table within the official scatter-expanded data block but does not make the compressed stream source-generated.",
            "The last two bytes of the eight-byte global timing copy are caller-stack fixture inputs; they are not initialized by the six-byte timing scan. Raw delay/electrical calibration is not tested. No whole-image or byte-identical build claim."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": len(summaries),
        "distinct_original_trace_bytes": len(used), "source_elf_sha256": report["source_elf_sha256"]}))


if __name__ == "__main__":
    main()
