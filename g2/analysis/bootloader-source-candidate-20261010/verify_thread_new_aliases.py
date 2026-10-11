#!/usr/bin/env python3
"""Compare each thread-new caller alias with locked stock and selected source."""
import importlib.util
import itertools
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/thread_creation"
spec = importlib.util.spec_from_file_location("thread_verify", BASE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/thread_new_aliases.c"
SOURCE = BASE / "thread_creation.c"
NAMES = ["opencfw_boot_dfu_thread_new", "opencfw_provider_4160fe"]


def main():
    assert v.v.sha(v.v.BLOB) == v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-thread-new-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(BASE / "module.ld"),
                        *(str(o) for o in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segments, syms = v.v.elf.elf_info(elf)
        ledger, trace = {}, {}
        attrs = [None, [0] * 9,
                 [0x434134, 0, 0x20026ac0, 112, 0x20018aa0, 0x4000, 48, 1, 0],
                 [0x4341a4, 0, 0x20026b30, 112, 0x20020e00, 0x2000, 46, 1, 0],
                 [0x433f68, 0, 0x20026a50, 112, 0x200f3800, 3072, 38, 0, 0]]
        for index, values in [(1, [1, 2, 0x100]), (3, [111, 112]),
                              (5, [0, 1, 4, 0x40000]), (6, [0, 1, 56, 57])]:
            for value in values:
                row = [0] * 9
                row[index] = value
                attrs.append(row)
        for name in NAMES:
            cases = []
            for guard, entry, attr, status in itertools.product(
                    [0, 1], [0, 0x42e2f9, 0x42e645], attrs, [0, 1, 2]):
                pair = [v.Machine(), v.Machine(True, segments, syms)]
                pair[1].symbols["thread_new"] = syms[name]
                observed = []
                for m in pair:
                    m.guard = guard
                    m.dynamic_status = status
                    if attr is not None:
                        m.cpu.mem_write(v.ATTR, struct.pack("<9I", *attr))
                    result = m.run("thread_new", [entry, 0x1234,
                                                   v.ATTR if attr is not None else 0])
                    observed.append([result["return"], result["events"]])
                assert observed[0] == observed[1], (name, guard, entry, attr, status, observed)
                trace.update(pair[0].trace)
                cases.append({"guard": guard, "entry": entry, "attribute": attr,
                              "kernel_status": status, "observed": observed[0]})
            ledger[name] = {"stock_entry": "0x4160ff", "cases": len(cases),
                            "comparisons": cases}
        used = {int(pc, 0) + offset for pc, raw in trace.items()
                for offset in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "original_sha256": v.v.SHA,
                  "source_elf_sha256": v.v.sha(elf), "alias_sha256": v.v.sha(ALIAS),
                  "source_sha256": v.v.sha(SOURCE), "cases": sum(x["cases"] for x in ledger.values()),
                  "distinct_original_trace_bytes": len(used), "aliases": ledger,
                  "limits": ["Each alias is independently entered with its caller-compatible three-word ABI; static and dynamic attribute paths are compared.",
                             "Context guard and kernel creator bodies are controlled cuts. No scheduler, allocator, physical device or IRQ behavior is established.",
                             "Compatible M4 execution is compared; M55 compilation, relocation and archive linking are checked separately."]}
        output = Path(__file__).with_name("thread-new-aliases-comparison.json")
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
