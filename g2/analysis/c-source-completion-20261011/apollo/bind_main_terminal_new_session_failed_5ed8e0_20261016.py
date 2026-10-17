#!/usr/bin/env python3
"""Bind stock-compared new-session failure action into Apollo C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261016/main-terminal-new-session-failed-5ed8e0"
BASE = G2 / "build/c-firmware/20261016/main-terminal-session-row-factory-5ecd06/apollo-main-selector-row-bound.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_new_session_failed_5ed8e0.c"
ORACLE = OUT / "oracle-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_NEW_SESSION_FAILED_C_ORACLE"
            or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("new-session failure oracle/source changed")
    before = imports(BASE)
    removed = {"audio_terminal_ui_action_5ed8e0"}
    if len(before) != 174 or not removed <= before:
        raise RuntimeError("Apollo candidate frontier changed")
    obj = OUT / "new-session-failed-bind.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-new-session-failed-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = imports(linked)
    if before - after != removed or after - before or len(after) != 173:
        raise RuntimeError(f"unexpected import change: {before-after=} {after-before=} {len(after)=}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_NEW_SESSION_FAILED_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(ORACLE),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "unresolved_before": 174,
               "unresolved_after": 173, "imports_resolved": sorted(removed),
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Action passes bounded stock comparisons; lower UI/queue/log effects and full image/hardware remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sha(path))


if __name__ == "__main__":
    main()
