#!/usr/bin/env python3
"""Compare bounded main-init dispatcher calls; all callee services are cuts."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location(
    "startupv", ROOT / "g2/components/bootloader/startup/verify.py"
)
startup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(startup)
v = startup.v
v.ENTRIES["main_init"] = 0x41B862

SLOT = 0x200004F4
SLOT_TARGETS = [0x2003F001, 0x2003F101]
PROVIDERS = {
    0x41F9D8, 0x41F9F8, 0x41F846, 0x41AC44, 0x41AC5A, 0x41FA50,
    0x41E1E8, 0x41E266, 0x41BA80, 0x415FAE, 0x41FD70, 0x420476,
    0x421210, 0x4176CE,
}


class MainInitMachine(startup.Machine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode_result = 0
        self.slot_target = SLOT_TARGETS[0]
        self.spin_seen = set()

    def cstring(self, address):
        data = bytearray()
        while len(data) < 256:
            byte = self.cpu.mem_read(address + len(data), 1)[0]
            if byte == 0:
                return bytes(data).decode("ascii")
            data.append(byte)
        raise AssertionError(("unterminated test string", hex(address)))

    def code(self, uc, pc, size, user):
        if pc in PROVIDERS:
            r0, r1, r2, r3 = self.args()
            if pc == 0x41F9D8:
                self.events.append(["0x41f9d8", r0])
            elif pc in {0x41F9F8, 0x41AC44, 0x41FA50, 0x41E1E8,
                        0x41FD70, 0x420476, 0x421210}:
                self.events.append([hex(pc)])
            elif pc in {0x41F846, 0x41AC5A, 0x41E266}:
                self.events.append([hex(pc), r0])
            elif pc == 0x41BA80:
                self.events.append(["0x41ba80", r0, self.mode_result])
                self.ret(self.mode_result)
                return
            elif pc == 0x415FAE:
                self.events.append(["0x415fae", r0, r1, self.cstring(r0)])
            elif pc == 0x4176CE:
                sp = uc.reg_read(v.a.UC_ARM_REG_SP)
                line, message = self.u(sp), self.u(sp + 4)
                self.events.append([
                    "0x4176ce", r0, r1, r2, r3, line, message,
                    self.cstring(r1), self.cstring(r2), self.cstring(r3),
                    self.cstring(message),
                ])
            self.ret()
            return

        if pc == (self.slot_target & ~1):
            self.events.append(["indirect-slot", self.slot_target])
            self.ret()
            return

        if self.source:
            spin = self.symbols["opencfw_boot_main_terminal_spin"] & ~1
            if pc == spin:
                if pc in self.spin_seen:
                    self.finished = True
                    uc.emu_stop()
                    return
                self.spin_seen.add(pc)
                self.events.append(["terminal-spin"])
                super().code(uc, pc, size, user)
                return
        elif pc == 0x41B8C4:
            if pc in self.spin_seen:
                self.finished = True
                uc.emu_stop()
                return
            self.spin_seen.add(pc)
            self.events.append(["terminal-spin"])
            super().code(uc, pc, size, user)
            return

        super().code(uc, pc, size, user)


def expected_events(mode_result, slot_target):
    events = [
        ["0x41f9d8", 200], ["0x41f9f8"], ["0x41f846", 1],
        ["0x41ac44"], ["0x41ac5a", 1], ["0x41fa50"],
        ["0x41e1e8"], ["0x41e266", 1], ["0x41ba80", 2, mode_result],
    ]
    if mode_result != 0:
        events.append([
            "0x415fae", 0x43198C, mode_result,
            "Error switching to high performance mode. error num = %d\r\n",
        ])
    events += [
        ["0x41fd70"], ["0x420476"], ["0x421210"],
        ["0x4176ce", 4, 0x434124, 0x431340, 0x43411C, 0x2E, 0x433360,
         "main",
         "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\config\\main.c",
         "main", ">>> Even Bootloader start <<<"],
        ["indirect-slot", slot_target], ["terminal-spin"],
    ]
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    trace, cases = {}, []

    for mode_result in [0, 7, 0xFFFFFFFF]:
        for slot_target in SLOT_TARGETS:
            machines = [MainInitMachine(), MainInitMachine(True, segments, symbols)]
            for machine in machines:
                machine.mode_result = mode_result
                machine.slot_target = slot_target
                machine.w(SLOT, slot_target)
            results = [machine.run("main_init", [0]) for machine in machines]
            assert results[0]["events"] == results[1]["events"], (
                mode_result, hex(slot_target), results[0]["events"], results[1]["events"]
            )
            assert results[0]["events"] == expected_events(mode_result, slot_target), (
                mode_result, hex(slot_target), results[0]["events"]
            )
            trace.update(machines[0].trace)
            cases.append({
                "mode_status": mode_result,
                "slot_target": hex(slot_target),
                "calls": results[0]["events"],
            })

    used = {
        int(pc, 0) + offset
        for pc, raw in trace.items()
        for offset in range(len(bytes.fromhex(raw)))
    }
    sources = [p for p in HERE.iterdir()
               if p.suffix in {".c", ".h", ".ld", ".py"} or p.name == "Makefile"]
    report = {
        "status": "PASS",
        "cases": len(cases),
        "distinct_original_trace_bytes": len(used),
        "original_trace": trace,
        "original_sha256": v.SHA,
        "elf_sha256": v.sha(args.elf),
        "source_sha256": {p.name: v.sha(p) for p in sources},
        "comparisons": cases,
        "limits": [
            "Only dispatcher 0x41B862 through the indirect callback and terminal spin is reconstructed; callees are synthetic at their exact stock entries.",
            "Mode-check statuses 0, 7 and 0xFFFFFFFF exercise the conditional error-log branch; mode-check implementation is not reconstructed here.",
            "Allocator (0x41FD70), NOR/MSPI initializer (0x420476), filesystem initializer (0x421210), init table, hardware helpers and both loggers are explicit synthetic providers.",
            "The RAM function slot at 0x200004F4 is fixture-populated with one of two synthetic callbacks; no real startup table publication or callback behavior is claimed.",
            "The four log strings are source-defined constants at their original addresses. No physical hardware, allocator state, NOR/filesystem state, or full boot flow is exercised.",
            "This source profile and bounded trace do not establish complete bootloader source coverage, byte identity, or a hardware boot claim.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
