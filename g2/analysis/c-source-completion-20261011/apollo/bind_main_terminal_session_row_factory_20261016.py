#!/usr/bin/env python3
"""Bind stock-compared selector row factory, icon choice and icon bytes."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-row-factory-5ecd06"
ICON_OUT = G2 / "build/c-firmware/20261016/main-terminal-session-row-icon-5eccc2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-session-list-rebuild-5ecef6/apollo-main-selector-rebuild-bound.o"
SOURCES = [G2 / "components/audio/uart_thread_source_candidate" / name for name in
           ("terminal_session_row_icon_5eccc2.c", "terminal_session_icon_773060.c",
            "terminal_session_row_factory_5ecd06.c")]
ORACLES = [ICON_OUT / "oracle-receipt.json", OUT / "oracle-receipt.json"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    icon, factory = (json.loads(p.read_text()) for p in ORACLES)
    if icon["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_ROW_ICON_C_ORACLE" or \
            factory["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_ROW_FACTORY_C_ORACLE":
        raise RuntimeError("selector row oracles changed")
    if [icon["source_sha256"], icon["asset_sha256"], factory["source_sha256"]] != \
            [sha(source) for source in SOURCES]:
        raise RuntimeError("selector row sources changed")
    before = imports(BASE)
    removed = {"audio_terminal_session_row_factory_5ecd06"}
    if len(before) != 175 or not removed <= before:
        raise RuntimeError("Apollo candidate frontier changed")
    objects = []
    for source in SOURCES:
        obj = OUT / (source.stem + "-bind.o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    linked = OUT / "apollo-main-selector-row-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                    *(str(obj) for obj in objects), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != removed or after - before or len(after) != 174:
        raise RuntimeError(f"unexpected import change: {before-after=} {after-before=} {len(after)=}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_ROW_FACTORY_C",
               "sources": [str(p.relative_to(ROOT)) for p in SOURCES],
               "source_sha256": [sha(p) for p in SOURCES],
               "oracle_receipts": [str(p.relative_to(ROOT)) for p in ORACLES],
               "oracle_receipt_sha256": [sha(p) for p in ORACLES],
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "objects": [str(p.relative_to(ROOT)) for p in objects],
               "object_sha256": [sha(p) for p in objects],
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "unresolved_before": 175,
               "unresolved_after": 174, "imports_resolved": sorted(removed),
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Selector row construction and icon choice are bounded stock matches; LVGL effects and whole-image/hardware gates remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sha(path))


if __name__ == "__main__":
    main()
