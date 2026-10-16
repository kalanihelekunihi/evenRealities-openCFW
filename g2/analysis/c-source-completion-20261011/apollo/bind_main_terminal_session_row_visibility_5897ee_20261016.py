#!/usr/bin/env python3
"""Bind stock-compared Terminal row visibility and LVGL class ancestry."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-list-anim-path-450688/apollo-main-terminal-list-anim-path-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-row-visibility-5897ee"
SOURCES = (
    G2 / "components/audio/uart_thread_source_candidate/display_lv_class_is_43e2d4.c",
    G2 / "components/audio/uart_thread_source_candidate/terminal_session_row_visibility_5897ee.c",
)
ORACLES = (G2 / "build/c-firmware/20261016/main-lv-class-is-43e2d4/oracle-receipt.json",
           OUT / "oracle-receipt.json")
EXPECTED = (("PASS_EXPERIMENTAL_MAIN_LV_CLASS_IS_C_ORACLE", 30),
            ("PASS_EXPERIMENTAL_TERMINAL_SESSION_ROW_VISIBILITY_C_ORACLE", 140))
RESOLVED = {"audio_terminal_session_row_show_5897ee",
            "audio_terminal_session_row_hide_589892"}
ADDED = {"audio_uart_image_class_756108"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    proofs = [json.loads(path.read_text()) for path in ORACLES]
    for proof, (status, cases), source in zip(proofs, EXPECTED, SOURCES):
        if proof["status"] != status or proof["cases"] != cases or \
                proof["source_sha256"] != sha(source):
            raise RuntimeError("Terminal row visibility oracle changed")
    before = imports(BASE)
    if len(before) != 202 or not RESOLVED <= before:
        raise RuntimeError("Terminal row visibility frontier changed")
    objects = []
    for source in SOURCES:
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    linked = OUT / "apollo-main-terminal-session-row-visibility-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before != ADDED or len(after) != 201:
        raise RuntimeError(f"Terminal row visibility frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_ROW_VISIBILITY_C",
              "sources": [str(s.relative_to(ROOT)) for s in SOURCES],
              "source_sha256": [sha(s) for s in SOURCES],
              "oracle_receipts": [str(p.relative_to(ROOT)) for p in ORACLES],
              "oracle_receipt_sha256": [sha(p) for p in ORACLES],
              "objects": [str(p.relative_to(ROOT)) for p in objects],
              "object_sha256": [sha(p) for p in objects],
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 202, "unresolved_after": 201,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Image class record 0x756108 and its callbacks remain open; final placement and tree concurrency open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(path))


if __name__ == "__main__":
    main()
