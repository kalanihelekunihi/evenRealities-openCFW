#!/usr/bin/env python3
"""Differentially execute stock and readable NOR program/erase code.

Only calls below the command layer (mode setup, mutex/timing helpers, PIO
command execution and diagnostic sinks) are deterministic synthetic cuts.
"""
import argparse
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootverify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

ENTRIES = {
    "program": (0x420B0C, "opencfw_provider_420b0c"),
    "erase": (0x420A08, "opencfw_provider_420a08"),
    "wren": (0x420984, "opencfw_provider_420984"),
    "wrdi": (0x4209C4, "opencfw_provider_4209c4"),
}
SLOT = 0x200270DC
HANDLE = 0x20006000
SOURCE = 0x20008000
STUBS = {
    0x41FF08: "before", 0x420F10: "write_mode",
    0x420E8C: "restore_mode", 0x4207F4: "delay",
    0x4207A2: "wait", 0x41FF1E: "after",
}

for key, (address, _) in ENTRIES.items():
    v.ENTRIES["nor_write_" + key] = address


class Machine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None, fixture=None):
        super().__init__(source, segments, symbols)
        self.fixture = fixture or {}
        self.provider_events = []
        self.transfer_index = 0
        self.delay_index = 0
        if source:
            for name, (_, symbol) in ENTRIES.items():
                self.symbols["opencfw_boot_nor_write_" + name] = \
                    self.symbols[symbol]

    def _take(self, field, index=0):
        value = self.fixture.get(field, 0)
        if isinstance(value, list):
            return value[index] if index < len(value) else 0
        return value

    def _string(self, pointer):
        data = bytearray()
        for offset in range(256):
            byte = self.cpu.mem_read(pointer + offset, 1)[0]
            if byte == 0:
                break
            data.append(byte)
        return data.decode("ascii", errors="replace")

    def code(self, uc, pc, size, user):
        if pc in STUBS:
            name = STUBS[pc]
            self.provider_events.append([name])
            result = 0
            if name == "delay":
                result = self._take("delay_status", self.delay_index)
                self.delay_index += 1
            elif name == "wait":
                result = self.fixture.get("wait_status", 0)
                self.provider_events[-1].append(self.args()[0])
            self.ret(result)
            return
        if pc == 0x42069E:
            instruction, address, send_address, buffer = self.args()
            length = self.u(uc.reg_read(v.a.UC_ARM_REG_SP))
            event = ["transfer", instruction, address, send_address,
                     buffer, length]
            result = self._take("transfer_status", self.transfer_index)
            self.transfer_index += 1
            self.provider_events.append(event + [result])
            self.ret(result)
            return
        if pc == 0x415FAE:
            registers = self.args()
            fmt = self._string(registers[0])
            count = fmt.count("%")
            values = registers[1:]
            if count > len(values):
                sp = uc.reg_read(v.a.UC_ARM_REG_SP)
                values += [self.u(sp + 4 * index)
                           for index in range(count - len(values))]
            self.provider_events.append(["printf", fmt, values[:count]])
            self.ret(0)
            return
        if pc == 0x4176CE:
            level, module, file, function = self.args()
            sp = uc.reg_read(v.a.UC_ARM_REG_SP)
            line = self.u(sp)
            fmt = self.u(sp + 4)
            self.provider_events.append(["log", level, self._string(module),
                self._string(function), line, self._string(fmt)])
            self.ret(0)
            return
        super().code(uc, pc, size, user)

    def invoke(self, name, args, fixture):
        self.fixture = fixture
        self.provider_events = []
        self.transfer_index = self.delay_index = 0
        self.w(SLOT, fixture.get("handle", HANDLE))
        result = self.run("nor_write_" + name, args)
        return {"return": result["return"], "providers": self.provider_events}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases = []
    trace = {}

    fixtures = [
        ("erase", [0x12000], {}),
        ("erase", [0x12001], {}),
        ("erase", [0x02000000], {}),
        ("erase", [0x12000], {"handle": 0}),
        ("erase", [0x12000], {"delay_status": 9}),
        ("erase", [0x12000], {"transfer_status": 7}),
        ("erase", [0x12000], {"transfer_status": [0, 8]}),
        ("erase", [0x12000], {"delay_status": [0, 9]}),
        ("erase", [0x12000], {"transfer_status": [0, 0, 10]}),
        ("program", [0x120F1, SOURCE, 0x120], {}),
        ("program", [0x12000, SOURCE, 0], {}),
        ("program", [0x12000, 0, 1], {}),
        ("program", [0x12000, SOURCE, 1], {"handle": 0}),
        ("program", [0x02000000, SOURCE, 1], {}),
        ("program", [0x01FFFFFF, SOURCE, 2], {}),
        ("program", [0x120F1, SOURCE, 0x120], {"delay_status": 7}),
        ("program", [0x120F1, SOURCE, 0x120], {"transfer_status": 7}),
        ("program", [0x120F1, SOURCE, 0x120], {"transfer_status": [0, 8]}),
        ("program", [0x120F1, SOURCE, 0x120], {"wait_status": 1}),
        ("program", [0x120F1, SOURCE, 0x120], {"transfer_status": [0, 0, 9]}),
        ("program", [0x120F1, SOURCE, 0x120], {"delay_status": [0, 0, 7]}),
        ("program", [0x120F1, SOURCE, 0x120], {"transfer_status": [0, 0, 0, 0, 10]}),
        ("program", [0x01FFFFFF, SOURCE, 2], {"transfer_status": [0, 0, 0, 0, 0, 5]}),
        ("wren", [], {}),
        ("wren", [], {"transfer_status": 5}),
        ("wrdi", [], {}),
        ("wrdi", [], {"transfer_status": 6}),
    ]
    for name, values, fixture in fixtures:
        pair = [Machine(fixture=fixture),
                Machine(True, segments, dict(symbols), fixture=fixture)]
        for machine in pair:
            machine.cpu.mem_write(SOURCE, bytes((i * 7 + 3) & 0xFF
                                                for i in range(0x400)))
        try:
            results = [machine.invoke(name, values, fixture) for machine in pair]
        except Exception:
            print("case failed", name, values, fixture,
                  [(machine.source, hex(machine.cpu.reg_read(
                      v.a.UC_ARM_REG_PC))) for machine in pair])
            raise
        assert results[0] == results[1], (name, values, fixture, results)
        trace.update(pair[0].trace)
        cases.append({"function": name, "arguments": values,
                      "fixture": fixture, "result": results[0]})

    original = v.BLOB.read_bytes()
    sha = v.sha(v.BLOB)
    ranges = {name: [address - v.BASE, end - v.BASE]
              for name, address, end in [
                  ("sector erase", 0x420A08, 0x420ADA),
                  ("page program", 0x420B0C, 0x420C14),
                  ("write enable", 0x420984, 0x4209BE),
                  ("write disable", 0x4209C4, 0x4209FC)]}
    function_hashes = {
        name: __import__("hashlib").sha256(original[start:end]).hexdigest()
        for name, (start, end) in ranges.items()}
    used = {int(pc, 0) + offset for pc, raw in trace.items()
            for offset in range(len(bytes.fromhex(raw)))}
    result = {
        "status": "PASS", "cases": len(cases),
        "original_sha256": sha,
        "source_elf_sha256": v.sha(args.elf),
        "source_sha256": {p.name: v.sha(p) for p in
            [HERE / "verify_nor_write.py", ROOT / "g2/components/bootloader/nor_write/nor_write.c",
             ROOT / "g2/components/bootloader/nor_write/nor_write.h",
             ROOT / "g2/components/bootloader/nor_write/module.ld"]},
        "stock_function_ranges_sha256": function_hashes,
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace, "comparisons": cases,
        "limits": [
            "Original 0x420a08/0x420b0c/0x420984/0x4209c4 instructions execute against synthetic handles and deterministic provider return sequences.",
            "Mutex/state transitions, NOR command execution, mode setup/restore, delay/wait completion, logging and transfer-error sinks are intercepted at exact stock call boundaries. No flash is read or changed.",
            "The underlying PIO command builder at 0x42069e is a separately recovered source component; this fixture treats its validated ABI as a command-transfer boundary.",
            "Delay values 1, 5, 10, 1000, 500 and 1000 are raw stock arguments; their physical units or elapsed time are not inferred here.",
            "No power-loss/retry/cache coherency or installed filesystem behavior is claimed. The source ELF retains external provider aliases and is not a standalone boot image.",
        ]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in
        ("status", "cases", "distinct_original_instruction_bytes",
         "stock_function_ranges_sha256")}, indent=2))


if __name__ == "__main__":
    main()
