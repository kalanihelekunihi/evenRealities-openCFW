#!/usr/bin/env python3
"""Platform-finish interrupt alias versus locked stock and selected source."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/initializer_callbacks"
spec = importlib.util.spec_from_file_location("interrupt_verify", BASE / "verify_context_interrupt.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/context_interrupt_alias.c"
SOURCE = BASE / "context_interrupt.c"


def main():
    assert hashlib.sha256(v.BLOB.read_bytes()).hexdigest() == v.LOCKED_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-context-interrupt-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T",
                        str(Path(__file__).with_name("context-interrupt-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.elf.elf_info(elf)
        original, source = v.Machine(False), v.Machine(True, segs, syms)
        source.symbols["opencfw_boot_context_interrupt_enable"] = syms["opencfw_bl_context_interrupt_enable"]
        cases = []
        for handle in [None, (0, 0), (v.MAGIC ^ 1, 0),
                       (v.MAGIC, 0), (v.MAGIC, 1), (v.MAGIC, 2), (v.MAGIC, 3)]:
            for mask in [0, 1, 2, 4, 0xff, 0x3fffffff, 0x80000000]:
                observed = [m.run(handle, mask, 0x100) for m in [original, source]]
                assert observed[0] == observed[1], (handle, mask, observed)
                cases.append({"handle": handle, "mask": mask, "observed": observed[0]})
        trace = {hex(pc): raw for pc, raw in original.trace.items()}
        used = {int(pc, 16) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.LOCKED_SHA,
                  "source_elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
                  "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "alias_sha256": hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  "stock_entry": "0x42c63b", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Selected platform-finish caller passes a transfer-handle pointer as one ARM32 word and mask 0xff; invalid and additional module/mask cases are compared.",
                             "MMIO is Unicorn RAM. Issued writes and resulting modeled word do not prove physical interrupt-controller behavior."]}
        Path(__file__).with_name("context-interrupt-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
