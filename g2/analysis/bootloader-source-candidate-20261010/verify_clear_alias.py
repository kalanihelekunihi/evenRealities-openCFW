#!/usr/bin/env python3
"""NOR timing fill alias versus locked stock and selected source memset."""
import hashlib
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("boot_verify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/clear_alias.c"
SOURCE = ROOT / "g2/components/bootloader/filesystem/runtime_memory.c"
DEST = 0x20032020


def main():
    assert v.sha(v.BLOB) == v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-clear-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "memory.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-ffunction-sections", "-fdata-sections", "-c", str(source),
                            "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "--gc-sections", "-T",
                        str(Path(__file__).with_name("clear-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.elf.elf_info(elf)
        v.ENTRIES["clear"] = 0x426c10
        trace, cases = {}, []
        for offset, value, length in itertools.product(
                [0, 1, 2, 3], [0, 1, 0x7f, 0xff, 0x1234],
                [0, 1, 2, 5, 6, 7, 16, 31, 32, 63]):
            destination = DEST + offset
            pair = [v.Machine(), v.Machine(True, segs, dict(syms))]
            pair[1].symbols["opencfw_boot_clear"] = syms["opencfw_bl_clear"]
            observed = []
            for m in pair:
                m.cpu.mem_write(DEST - 4, b"\xa5" * 80)
                result = m.run("clear", [destination, value, length])
                observed.append({"return": result["return"],
                                 "memory": bytes(m.cpu.mem_read(DEST - 4, 80)).hex()})
            assert observed[0] == observed[1], (offset, value, length, observed)
            trace.update(pair[0].trace)
            cases.append({"offset": offset, "value": value, "length": length,
                          "return": observed[0]["return"], "memory": observed[0]["memory"]})
        used = {int(pc, 0) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.SHA, "source_elf_sha256": v.sha(elf),
                  "source_sha256": v.sha(SOURCE), "alias_sha256": v.sha(ALIAS),
                  "stock_entry": "0x426c11", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Authored NOR timing wrapper passes stack destination, value zero and length six; pointer/return ABI is tested as additional evidence although caller ignores the return.",
                             "Synthetic RAM comparison covers local fill and canaries only; whole NOR timing and actual hardware behavior are outside this test."]}
        Path(__file__).with_name("clear-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
