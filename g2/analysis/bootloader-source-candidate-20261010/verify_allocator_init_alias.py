#!/usr/bin/env python3
"""Main-init allocator alias versus locked stock and selected TLSF source."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/allocator"
spec = importlib.util.spec_from_file_location("allocator_verify", BASE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/allocator_init_alias.c"
SOURCES = [BASE / "allocator.c", BASE / "upstream/tlsf.c",
           ROOT / "g2/components/bootloader/filesystem/runtime_memory.c"]


def main():
    assert v.v.sha(v.v.BLOB) == v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-allocator-init-alias-") as tmp:
        p = Path(tmp)
        objects = []
        for i, source in enumerate([ALIAS, *SOURCES]):
            obj = p / f"unit_{i}.o"
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv", "-DNDEBUG",
                            "-I" + str(BASE), "-I" + str(BASE / "freestanding_include"),
                            "-I" + str(ROOT / "g2/components/bootloader/filesystem/freestanding_include"),
                            "-c", str(source), "-o", str(obj)], check=True)
            objects.append(obj)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(BASE / "module.ld"),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
        stock, source = v.Machine(), v.Machine(True, segs, syms)
        source.symbols["opencfw_boot_allocator_init"] = syms["opencfw_provider_41fd70"]
        observed = [m.invoke("allocator_init", []) for m in [stock, source]]
        assert observed[0] == observed[1], observed
        trace = stock.trace
        used = {int(pc, 0) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": 1,
                  "original_sha256": v.v.SHA, "source_elf_sha256": v.v.sha(elf),
                  "alias_sha256": v.v.sha(ALIAS),
                  "source_sha256": {str(x.relative_to(ROOT)): v.v.sha(x) for x in SOURCES},
                  "stock_entry": "0x41fd71", "distinct_original_trace_bytes": len(used),
                  "observed": observed[0],
                  "limits": ["The selected main-init caller takes no result; return R0 and full 460800-byte arena SHA are compared as additional evidence.",
                             "Initialization logger is a controlled cut; allocator source and pinned TLSF core execute.",
                             "Compatible M4 source executes in Unicorn; M55 archive compilation and direct relocation are checked separately. No hardware execution or production layout proof."]}
        Path(__file__).with_name("allocator-init-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: report[k] for k in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
