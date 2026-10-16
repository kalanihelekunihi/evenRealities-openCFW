#!/usr/bin/env python3
"""Bind stock-compared Terminal reset prelude into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-event-type3-mask-5eaca0/apollo-main-terminal-event-type3-mask-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-reset-first-5e51ba"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_reset_first_5e51ba.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_reset_first_5e51ba"}
ADDED = {"audio_terminal_reset_preclear_5e7f26",
         "audio_terminal_reset_mode_notice_54f50e",
         "audio_terminal_reset_ancillary_5e65f8"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_RESET_FIRST_C_ORACLE" or \
            oracle["cases"] != 156 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal reset prelude oracle changed")
    before = imports(BASE)
    if len(before) != 222 or not RESOLVED <= before:
        raise RuntimeError("Terminal reset prelude frontier changed")
    obj = OUT / "terminal_reset_first_5e51ba.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-reset-first-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before != ADDED or len(after) != 224:
        raise RuntimeError(f"Terminal reset prelude frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESET_FIRST_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 222, "unresolved_after": 224,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Three reset descendants, lower effects and final RAM placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))

if __name__ == "__main__":
    main()
