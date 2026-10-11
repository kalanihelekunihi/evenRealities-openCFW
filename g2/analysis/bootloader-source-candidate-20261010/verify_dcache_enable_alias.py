#!/usr/bin/env python3
"""Compare original D-cache entry with selected M55 C and historical alias."""
import hashlib
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHECK = ROOT / "g2/components/bootloader/platform_control/verify_cache_enable.py"
spec = importlib.util.spec_from_file_location("cache_check", CHECK)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
PROVIDER = ROOT / "g2/components/bootloader/platform_control/cache_enable.c"
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/dcache_enable_alias.c"
SCRIPT = ROOT / "g2/components/bootloader/platform_control/cache_enable.ld"
BODY_SHA = "0cab183f23bbfca4244cd5d15ebee4bc86f0f90c47e20e547bca97cc77cde099"


def main():
    assert check.p.sha(check.p.BLOB) == check.p.SHA
    image = check.p.BLOB.read_bytes()
    assert hashlib.sha256(image[0xe266:0xe348]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-dcache-alias-") as temporary:
        p = Path(temporary)
        objects = [p / "provider.o", p / "alias.o"]
        for src, obj in zip([PROVIDER, ALIAS], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                            "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                            "-fdata-sections", "-std=c11", "-O2", "-fwrapv", "-DNDEBUG",
                            "-c", str(src), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(SCRIPT), "-o", str(elf),
                        *(str(obj) for obj in objects)], check=True, capture_output=True)
        _, segments, symbols = check.p.elf.elf_info(elf)
        elf_hash = check.p.sha(elf)
    rows, trace = [], {}
    for guard, ccr, descriptor, configuration, operand in itertools.product(
            [0, 0x100, 0x200, 0x400], [0, 0x10000, 0x20000, 0x30000],
            [0, (2 << 13) | (1 << 3), (0x200 << 13) | (3 << 3)],
            [(0, 0, 0), (7, 7, 7), (255, 128, 9)],
            [0, 1, 256, 257, 0xffffffff]):
        original = check.Machine(False, segments, symbols, "d")
        source = check.Machine(True, segments, symbols, "d")
        source.entry = symbols["opencfw_provider_41e266"]
        a = original.invoke(guard, ccr, descriptor, configuration, operand)
        b = source.invoke(guard, ccr, descriptor, configuration, operand)
        assert a == b, (guard, ccr, descriptor, configuration, operand, a, b)
        trace.update(original.trace)
        rows.append({"guard": guard, "ccr": ccr, "descriptor": descriptor,
                     "configuration": configuration, "operand": operand, "result": a})
    visited = {int(pc, 16) + i for pc, raw in trace.items()
               for i in range(len(bytes.fromhex(raw))) if 0x41e266 <= int(pc, 16) + i < 0x41e348}
    assert visited == set(range(0x41e266, 0x41e348))
    report = {"status": "PASS", "cases": len(rows),
              "original_image_sha256": check.p.SHA, "original_body_sha256": BODY_SHA,
              "original_body_visited_bytes": len(visited), "selected_provider_sha256": check.p.sha(PROVIDER),
              "source_elf_sha256": elf_hash, "comparisons": rows,
              "limits": "Synthetic SCB/cache state; ordered writes/barriers, return, SP and callee saves compared. Physical cache coherence and timing unmeasured."}
    Path(__file__).with_name("dcache-enable-alias-comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(rows), "coverage": len(visited)}))


if __name__ == "__main__":
    main()
