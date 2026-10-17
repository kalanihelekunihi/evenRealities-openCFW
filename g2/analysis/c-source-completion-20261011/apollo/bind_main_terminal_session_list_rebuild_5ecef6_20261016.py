#!/usr/bin/env python3
"""Bind stock-compared session-list rebuild into Apollo C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-list-rebuild-5ecef6"
BASE = G2 / "build/c-firmware/20261016/main-terminal-session-selector-leaf/apollo-main-selector-leaf-bound.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_list_rebuild_5ecef6.c"
ORACLE = OUT / "oracle-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_REBUILD_C_ORACLE"
            or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("selector rebuild oracle/source changed")
    before = imports(BASE)
    removed = {"audio_terminal_session_list_rebuild_5ecef6"}
    added = {"audio_terminal_session_row_factory_5ecd06"}
    if len(before) != 175 or not removed <= before:
        raise RuntimeError("Apollo candidate frontier changed")
    obj = OUT / "rebuild-bind.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-selector-rebuild-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = imports(linked)
    if before - after != removed or after - before != added or len(after) != 175:
        raise RuntimeError(f"unexpected import change: {before-after=} {after-before=} {len(after)=}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_REBUILD_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(ORACLE),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "unresolved_before": 175,
               "unresolved_after": 175, "imports_resolved": sorted(removed),
               "imports_added": sorted(added), "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["The selector row factory 0x5ecd06 remains open; whole-image and hardware gates remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sha(path))


if __name__ == "__main__":
    main()
