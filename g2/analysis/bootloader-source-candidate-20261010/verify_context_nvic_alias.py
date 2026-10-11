#!/usr/bin/env python3
"""Platform-finish NVIC alias versus locked stock and selected source."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/initializer_callbacks"
spec = importlib.util.spec_from_file_location("nvic_verify", BASE / "verify_context_nvic.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/context_nvic_alias.c"
SOURCE = BASE / "context_nvic.c"


def main():
    assert hashlib.sha256(v.v.BLOB.read_bytes()).hexdigest() == v.v.LOCKED_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-nvic-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T",
                        str(Path(__file__).with_name("context-nvic-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
        machines = [v.Machine(False, segs, syms), v.Machine(True, segs, syms)]
        machines[1].symbols["opencfw_boot_context_nvic_enable"] = syms["opencfw_bl_context_nvic_enable"]
        values = [0, 1, 10, 31, 32, 255, 0x7fff, 0x8000, 0xffff,
                  0x10000, 0x1234000a, 0xffff800a, 0xffffffff]
        cases = []
        for value in values:
            observed = [m.run(value) for m in machines]
            assert observed[0] == observed[1], (value, observed)
            cases.append({"argument": value, "issued_writes": observed[0]})
        trace = {hex(pc): raw for pc, raw in machines[0].trace.items()}
        used = {int(pc, 16) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.v.LOCKED_SHA,
                  "source_elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
                  "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "alias_sha256": hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  "stock_entry": "0x430471", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Selected platform-finish caller passes IRQ 10; broader halfword sign and truncation cases are sampled here, with exhaustive source verification retained separately.",
                             "Synthetic NVIC memory compares issued writes only; no W1S register effect, valid IRQ range or interrupt delivery is established."]}
        Path(__file__).with_name("context-nvic-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
