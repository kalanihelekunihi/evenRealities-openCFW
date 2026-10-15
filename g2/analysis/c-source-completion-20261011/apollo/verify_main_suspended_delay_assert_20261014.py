#!/usr/bin/env python3
"""Bind the suspended vTaskDelay fault path to source-owned C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/scheduler_delay_candidate/suspended_assert.c"
BASE = G2 / "build/c-firmware/20261014/main-thread-audio-closure/apollo-main-thread-audio.o"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
OUT = G2 / "build/c-firmware/20261014/main-suspended-delay-assert"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    rows = subprocess.check_output(["arm-none-eabi-nm", *options, str(path)], text=True)
    return {row.split()[-1] for row in rows.splitlines() if row.strip()}


def main():
    native = subprocess.check_output([
        "arm-none-eabi-objdump", "-d", "-M", "force-thumb",
        "--start-address=0x454b60", "--stop-address=0x454b6e", str(NATIVE)], text=True)
    for marker in ("bl\t5fa0a4", "movs\tr0, #0", "movs.w\tr1, #4294967295",
                   "str\tr0, [r1, #0]", "b.n\t454b6c"):
        if marker not in native:
            raise RuntimeError(f"native suspended delay branch changed: {marker}")
    if "audio_delay_scheduler_assert" not in names(BASE, "-u"):
        raise RuntimeError("suspended delay import absent")
    if "audio_mask_save" not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("BASEPRI source provider absent")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "suspended_assert.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    code = subprocess.check_output(["arm-none-eabi-objdump", "-dr", "-M",
                                    "force-thumb", str(obj)], text=True)
    for marker in ("R_ARM_THM_CALL\taudio_mask_save", "#4294967295",
                   "str\tr1, [r0, #0]", "b.n\tc"):
        if marker not in code:
            raise RuntimeError(f"C fault contract changed: {marker}")
    before = names(BASE, "-u")
    linked = OUT / "apollo-main-suspended-delay.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 485 or len(after) != 484 or before - after != {
            "audio_delay_scheduler_assert"} or after - before:
        raise RuntimeError("unexpected Main import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_SUSPENDED_DELAY_C_BOUNDARY",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_branch": "0x454b60..0x454b6c", "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
        "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
        "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked), "unresolved_before": len(before),
        "unresolved_after": len(after), "imports_resolved": sorted(before - after),
        "imports_added": [], "source_complete": False, "full_payload_linked": False,
        "limits": ["The synthetic C boundary reproduces the mask, invalid write, and loop sequence, not byte-identical register allocation.",
                   "The native invalid write is a fatal path; live exception delivery was not tested.",
                   "Main placement and hardware boot remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
