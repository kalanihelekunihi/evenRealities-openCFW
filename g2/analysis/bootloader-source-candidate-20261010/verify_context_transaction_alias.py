#!/usr/bin/env python3
"""Platform transaction alias versus locked stock and selected source."""
import hashlib
import importlib.util
import itertools
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/initializer_callbacks"
spec = importlib.util.spec_from_file_location("transaction_verify", BASE / "verify_context_claim.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/context_transaction_alias.c"
SOURCE = BASE / "context_transaction.c"


def main():
    assert hashlib.sha256(v.v.BLOB.read_bytes()).hexdigest() == v.v.LOCKED_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-context-transaction-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T",
                        str(Path(__file__).with_name("context-transaction-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
        original, source = v.Machine(False, segs, syms), v.Machine(True, segs, syms)
        source.symbols["opencfw_boot_context_transaction"] = syms["opencfw_bl_config_transaction"]
        cases = []
        for module, command, retain, scenario in itertools.product(
                [0, 4, 7], [0, 1, 2, 3, 0x100, 0x102], [0, 1, 0x101], range(5)):
            handle = v.POOL + module * v.STRIDE
            observed = []
            for m in [original, source]:
                m.reset()
                flags = 0x01123456 | (0x02000000 if scenario in (2, 3, 4) else 0)
                m.cpu.mem_write(handle, struct.pack("<II", flags, module))
                m.cpu.mem_write(handle + 0x24, struct.pack("<I", 1 if scenario == 3 else 0))
                m.cpu.mem_write(handle + 0x868, bytes([0 if scenario == 0 else 1]))
                m.cpu.mem_write(handle + 0x87c, struct.pack("<I", 1 if scenario == 4 else 0))
                m.cpu.mem_write(v.v.IRQ + module * 0x1000 + 0x228, struct.pack("<I", 1 if scenario == 4 else 0))
                m.cpu.mem_write(v.v.IRQ + module * 0x1000 + 0x248, struct.pack("<I", 2 if scenario == 2 else 4))
                m.clock_status = 7 if scenario == 4 else 0
                m.lower_status = 9
                status = m.call("transaction", [handle, command, retain])
                observed.append(m.observation(status))
            assert observed[0] == observed[1], (module, command, retain, scenario, observed)
            cases.append({"module": module, "command": command, "retain": retain,
                          "scenario": scenario, "observed": observed[0]})
        trace = {hex(pc): raw for pc, raw in original.trace.items()}
        used = {int(pc, 16) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.v.LOCKED_SHA,
                  "source_elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
                  "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "alias_sha256": hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  "stock_entry": "0x42c989", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Platform-finish calls transaction with its transfer-handle word and command/retain zero; broader command, retention and busy states are compared.",
                             "Power, clock, CQ and status-poll providers are controlled cuts. MMIO is synthetic RAM; no physical transfer/timing proof."]}
        Path(__file__).with_name("context-transaction-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
