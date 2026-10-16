#!/usr/bin/env python3
"""Bind authenticated Terminal style pointer table and image assets."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e583c/apollo-main-terminal-ui-action-5e583c-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-output-style-assets"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_output_style_assets_20261016.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_output_style_20003f80"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_OUTPUT_STYLE_ASSETS" or \
            oracle["descriptors"] != 6 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal output style oracle changed")
    before = imports(BASE)
    if len(before) != 212 or not RESOLVED <= before:
        raise RuntimeError("Terminal output style frontier changed")
    obj = OUT / "terminal_output_style_assets.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-output-style-assets-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before or len(after) != 211:
        raise RuntimeError(f"Terminal style frontier changed: {len(after)} {before-after=} {after-before=}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_OUTPUT_STYLE_ASSETS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 212, "unresolved_after": 211,
               "imports_resolved": sorted(RESOLVED), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Authenticated initial pointer table and ROM bytes; runtime mutation and final placement remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sha(path))

if __name__ == "__main__":
    main()
