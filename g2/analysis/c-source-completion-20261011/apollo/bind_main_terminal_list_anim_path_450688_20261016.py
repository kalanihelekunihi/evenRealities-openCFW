#!/usr/bin/env python3
"""Bind stock-compared Terminal button-fade Bezier path."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-list-anim-fade-start-58c622/apollo-main-terminal-list-anim-fade-start-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-list-anim-path-450688"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_list_anim_path_450688.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_uart_lv_anim_path_450688"}
ADDED = set()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_LIST_ANIM_PATH_C_ORACLE" or \
            oracle["cases"] != 15 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal list-animation path oracle changed")
    before = imports(BASE)
    if len(before) != 203 or not RESOLVED <= before:
        raise RuntimeError("Terminal list-animation path frontier changed")
    obj = OUT / "terminal_list_anim_path_450688.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-list-anim-path-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before != ADDED or len(after) != 202:
        raise RuntimeError(f"Terminal list-animation path frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_LIST_ANIM_PATH_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 203, "unresolved_after": 202,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Button fade callback 0x58c230 and final placement remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(path))

if __name__ == "__main__":
    main()
