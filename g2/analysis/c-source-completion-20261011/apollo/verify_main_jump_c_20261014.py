#!/usr/bin/env python3
"""Compare a C-compilable ARM jump provider with pinned Newlib/native evidence."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-freetype-source-closure"
BASE = OUT / "apollo-main-freetype-libc-complete.o"
SOURCE = G2 / "components/main/freetype_jump_candidate_20261014/jump.c"
NEWLIB = G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/newlib-source/machine/arm/setjmp-no-unwind.o"
PROBE = G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-jump-abi-round409/probe-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    text = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {row.split()[-1] for row in text.splitlines() if row.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = json.loads(PROBE.read_text())
    if (evidence["status"] != "PASS_NATIVE_NEWLIB_ARM_JUMP_REGISTER_AND_BUFFER_COMPARISON"
            or evidence["comparisons"] != 80 or evidence["buffer_written_bytes"] != 104):
        raise RuntimeError("pinned jump ABI evidence changed")
    obj = OUT / "jump-c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if imports(obj):
        raise RuntimeError("C jump provider retains imports")
    texts = []
    for name, path in (("c", obj), ("newlib", NEWLIB)):
        binary = OUT / f"jump-{name}.text.bin"
        subprocess.run(["arm-none-eabi-objcopy", "--only-section=.text",
                        "-O", "binary", str(path), str(binary)], check=True)
        texts.append(binary.read_bytes())
    if texts[0] != texts[1] or len(texts[0]) != 34:
        raise RuntimeError("C jump instructions differ from the finite native-tested provider")
    symbols = subprocess.check_output(["arm-none-eabi-nm", "-g", "--defined-only",
                                       str(obj)], text=True)
    if "00000000 T setjmp" not in symbols or "00000010 T longjmp" not in symbols:
        raise RuntimeError("C jump entry offsets changed")
    final = OUT / "apollo-main-freetype-jump-c.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(final)], check=True)
    before, after = imports(BASE), imports(final)
    if (len(before), len(after)) != (510, 508) or before - after != {"setjmp", "longjmp"} or after - before:
        raise RuntimeError("jump C source did not close exactly two Main contracts")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_JUMP_C_SOURCE_BINDING",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "c_object": str(obj.relative_to(ROOT)), "c_object_sha256": sha(obj),
        "pinned_newlib_object": str(NEWLIB.relative_to(ROOT)),
        "pinned_newlib_object_sha256": sha(NEWLIB),
        "instruction_bytes": len(texts[0]),
        "instruction_sha256": hashlib.sha256(texts[0]).hexdigest(),
        "native_comparison_receipt": str(PROBE.relative_to(ROOT)),
        "native_comparison_receipt_sha256": sha(PROBE),
        "finite_native_comparisons": evidence["comparisons"],
        "linked_object": str(final.relative_to(ROOT)),
        "linked_object_sha256": sha(final),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": ["longjmp", "setjmp"], "imports_added": [],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Native comparison covers finite register and buffer cases, not all FreeType call paths.",
                   "Recovered product jump buffer is 128 bytes; upstream default header is 160 bytes.",
                   "Main final layout, exceptions, and physical hardware behavior remain open."],
    }
    path = OUT / "jump-c-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
