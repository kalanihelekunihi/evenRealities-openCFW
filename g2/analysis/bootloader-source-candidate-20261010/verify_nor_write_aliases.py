#!/usr/bin/env python3
"""Filesystem NOR program/erase aliases versus locked stock and selected source."""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/nor_write"
spec = importlib.util.spec_from_file_location("nor_verify", ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-write/verify_nor_write.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/nor_write_aliases.c"
SOURCE = BASE / "nor_write.c"


def main():
    assert v.v.sha(v.v.BLOB) == v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-nor-write-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft", "-fshort-enums",
                            "-ffreestanding", "-fno-builtin", "-std=c11", "-O2",
                            "-fwrapv", "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(BASE / "module.ld"),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
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
            ("program", [0x120f1, v.SOURCE, 0x120], {}),
            ("program", [0x12000, v.SOURCE, 0], {}),
            ("program", [0x12000, 0, 1], {}),
            ("program", [0x12000, v.SOURCE, 1], {"handle": 0}),
            ("program", [0x02000000, v.SOURCE, 1], {}),
            ("program", [0x01ffffff, v.SOURCE, 2], {}),
            ("program", [0x120f1, v.SOURCE, 0x120], {"delay_status": 7}),
            ("program", [0x120f1, v.SOURCE, 0x120], {"transfer_status": 7}),
            ("program", [0x120f1, v.SOURCE, 0x120], {"transfer_status": [0, 8]}),
            ("program", [0x120f1, v.SOURCE, 0x120], {"wait_status": 1}),
            ("program", [0x120f1, v.SOURCE, 0x120], {"transfer_status": [0, 0, 9]}),
            ("program", [0x120f1, v.SOURCE, 0x120], {"delay_status": [0, 0, 7]}),
            ("program", [0x120f1, v.SOURCE, 0x120], {"transfer_status": [0, 0, 0, 0, 10]}),
            ("program", [0x01ffffff, v.SOURCE, 2], {"transfer_status": [0, 0, 0, 0, 0, 5]}),
        ]
        ledger, trace = {"program": [], "erase": []}, {}
        for name, args, fixture in fixtures:
            pair = [v.Machine(fixture=fixture),
                    v.Machine(True, segs, dict(syms), fixture=fixture)]
            alias = "opencfw_boot_nor_prog" if name == "program" else "opencfw_boot_nor_erase"
            pair[1].symbols["opencfw_boot_nor_write_" + name] = syms[alias]
            for m in pair:
                m.cpu.mem_write(v.SOURCE, bytes((i * 7 + 3) & 255 for i in range(0x400)))
            observed = [m.invoke(name, args, fixture) for m in pair]
            assert observed[0] == observed[1], (name, args, fixture, observed)
            trace.update(pair[0].trace)
            ledger[name].append({"arguments": args, "fixture": fixture,
                                 "observed": observed[0]})
        used = {int(pc, 0) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(fixtures),
                  "original_sha256": v.v.SHA, "source_elf_sha256": v.v.sha(elf),
                  "source_sha256": v.v.sha(SOURCE), "alias_sha256": v.v.sha(ALIAS),
                  "aliases": {"opencfw_boot_nor_prog": {"stock_entry": "0x420b0d", "comparisons": ledger["program"]},
                              "opencfw_boot_nor_erase": {"stock_entry": "0x420a09", "comparisons": ledger["erase"]}},
                  "distinct_original_trace_bytes": len(used),
                  "limits": ["Filesystem calls pass address/source/length or address in the expected ARM32 registers and consume status.",
                             "Mode setup/restore, delay/wait, PIO transfers and diagnostic sinks are controlled cuts at stock entries. No flash was read or changed.",
                             "Compatible M4 execution is compared; M55 archive compilation and direct relocations are checked separately. Formatter R1 behavior remains unresolved."]}
        Path(__file__).with_name("nor-write-aliases-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
