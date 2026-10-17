#!/usr/bin/env python3
"""Bind stock-compared selector leaf providers into the Apollo C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-selector-leaf"
BASE = G2 / "build/c-firmware/20261016/main-terminal-cancel-pending-5cef8c/apollo-main-terminal-cancel-pending-bound.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_selector_leaf_20261016.c"
ORACLE = OUT / "oracle-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_SELECTOR_LEAF_C_ORACLE"
            or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("selector leaf oracle/source changed")
    before = imports(BASE)
    if len(before) != 175 or "audio_terminal_session_list_rebuild_5ecef6" not in before:
        raise RuntimeError("Apollo candidate frontier changed")
    obj = OUT / "selector-leaf-bind.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-selector-leaf-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = imports(linked)
    if before != after:
        raise RuntimeError(f"unexpected import change: {before-after=} {after-before=}")
    symbols = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(linked)], text=True)
    for name in ("audio_terminal_session_four_margins_5eca00",
                 "audio_terminal_session_row_text_5ecc74"):
        if not any(line.endswith(" " + name) for line in symbols.splitlines()):
            raise RuntimeError(f"missing selector leaf provider: {name}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_SELECTOR_LEAF_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(ORACLE),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "unresolved_before": 175,
               "unresolved_after": 175, "imports_resolved": [], "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Selector rebuild 0x5ecef6 does not yet reference these C leaves; whole-image and hardware gates remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sha(path))


if __name__ == "__main__":
    main()
