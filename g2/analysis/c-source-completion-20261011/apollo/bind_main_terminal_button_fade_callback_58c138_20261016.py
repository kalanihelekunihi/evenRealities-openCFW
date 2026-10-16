#!/usr/bin/env python3
"""Bind the stock-compared recursive button fade callback."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-lv-image-lifecycle-498bd0/apollo-main-lv-image-lifecycle-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-button-fade-callback-58c138"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_button_fade_callback_58c138.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_button_fade_callback_58c230"}
ADDED = set()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_BUTTON_FADE_CALLBACK_C_ORACLE" or \
            oracle["cases"] != 168 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal button fade callback oracle changed")
    before = imports(BASE)
    if len(before) != 201 or not RESOLVED <= before:
        raise RuntimeError("Terminal button fade callback frontier changed")
    obj = OUT / "terminal-button-fade-callback.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-button-fade-callback-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before != ADDED or len(after) != 200:
        raise RuntimeError(f"Terminal button fade callback frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_BUTTON_FADE_CALLBACK_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 201, "unresolved_after": 200,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Actual LVGL style effects and cyclic/concurrent trees remain open; final placement open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(path))


if __name__ == "__main__":
    main()
