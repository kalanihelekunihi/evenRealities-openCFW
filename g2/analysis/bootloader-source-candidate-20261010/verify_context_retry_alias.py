#!/usr/bin/env python3
"""Platform retry alias versus locked stock with controlled transaction results."""
import hashlib
import importlib.util
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/initializer_callbacks"
spec = importlib.util.spec_from_file_location("interrupt_verify", BASE / "verify_context_interrupt.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/context_retry_alias.c"
SOURCE = BASE / "context_retry.c"
INDEX_BASE = 0x20000374
CFG = 0x20004000
HANDLE = 0x2001455c


class Machine(v.Machine):
    def __init__(self, source, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        self.events = []
        self.results = []

    def code(self, uc, pc, size, user):
        if pc in (0x42c988, 0x41f9d8, 0x41d92c):
            r0 = uc.reg_read(v.a.UC_ARM_REG_R0)
            r1 = uc.reg_read(v.a.UC_ARM_REG_R1)
            r2 = uc.reg_read(v.a.UC_ARM_REG_R2)
            if pc == 0x42c988:
                result = self.results.pop(0) if self.results else 3
                self.events.append(["transaction", r0, r1, r2, result])
            elif pc == 0x41f9d8:
                result = 0
                self.events.append(["delay", r0])
            else:
                result = 7
                self.events.append(["power-update", r0, r1])
            uc.reg_write(v.a.UC_ARM_REG_R0, result)
            uc.reg_write(v.a.UC_ARM_REG_PC, uc.reg_read(v.a.UC_ARM_REG_LR))
            return
        super().code(uc, pc, size, user)

    def call(self, index, results, literal):
        self.events = []
        self.results = list(results)
        self.cpu.mem_write(0x434158, literal)
        row = INDEX_BASE + ((index & 255) << 4)
        self.cpu.mem_write(row + 4, struct.pack("<II", HANDLE, CFG))
        self.cpu.mem_write(CFG, struct.pack("<II", 0x12345678, 0x87654321))
        self.done = False
        self.cpu.reg_write(v.a.UC_ARM_REG_R0, index)
        self.cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
        self.cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP | 1)
        entry = self.symbols["opencfw_boot_context_retry"] if self.source else 0x43048e
        self.cpu.emu_start(entry | 1, v.STOP + 2, count=300000)
        assert self.done
        return {"return": self.cpu.reg_read(v.a.UC_ARM_REG_R0),
                "events": list(self.events),
                "row": bytes(self.cpu.mem_read(row + 4, 8)).hex(),
                "config": bytes(self.cpu.mem_read(CFG, 8)).hex()}


def main():
    blob = v.BLOB.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == v.LOCKED_SHA
    literal = blob[0x434158 - v.BASE:0x43415c - v.BASE]
    with tempfile.TemporaryDirectory(prefix="bootloader-context-retry-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T",
                        str(Path(__file__).with_name("context-retry-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.elf.elf_info(elf)
        stock, source = Machine(False), Machine(True, segs, syms)
        source.symbols["opencfw_boot_context_retry"] = syms["opencfw_bl_config_retry"]
        cases = []
        for index in [0, 1, 2, 3, 4, 260]:
            for results in [[0], [3, 0], [3, 3, 0], [3] * 1000]:
                observed = [m.call(index, results, literal) for m in [stock, source]]
                assert observed[0] == observed[1], (index, len(results), observed)
                cases.append({"index": index, "results": len(results),
                              "event_tail": observed[0]["events"][-3:],
                              "return": observed[0]["return"],
                              "event_count": len(observed[0]["events"])})
        trace = {hex(pc): raw for pc, raw in stock.trace.items()}
        used = {int(pc, 16) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.LOCKED_SHA,
                  "source_elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
                  "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "alias_sha256": hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  "stock_entry": "0x43048f", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Platform-finish passes row index 0 through 4; index 260 tests low-byte wrap. Stock literal at 0x434158 is a locked comparison input only.",
                             "Transaction, delay and power-register calls are controlled cuts. Loop count and ordered arguments are compared; no physical retry timing or lower provider effect is established."]}
        Path(__file__).with_name("context-retry-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
