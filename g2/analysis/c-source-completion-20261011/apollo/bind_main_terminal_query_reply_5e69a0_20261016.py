#!/usr/bin/env python3
"""Bind stock-compared Terminal query-reply action and packet sender."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261016/main-terminal-query-reply-5e69a0"
SEND_OUT = G2 / "build/c-firmware/20261016/main-terminal-query-reply-5ced38"
BASE = G2 / "build/c-firmware/20261016/main-terminal-query-notification-activate-5e66d8/apollo-main-query-activate-bound.o"
SOURCES = (
    G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_query_reply_5e69a0.c",
    G2 / "components/audio/uart_thread_source_candidate/terminal_query_reply_send_5ced38.c",
)
ORACLES = (OUT / "oracle-receipt.json", SEND_OUT / "oracle-receipt.json")
STATUSES = ("PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_REPLY_C_ORACLE",
            "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_REPLY_SEND_C_ORACLE")
CASES = (360, 30)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    for source, oracle_path, status, cases in zip(SOURCES, ORACLES, STATUSES, CASES):
        oracle = json.loads(oracle_path.read_text())
        if oracle["status"] != status or oracle["source_sha256"] != sha(source) or \
                oracle["cases"] != cases:
            raise RuntimeError("query-reply oracle/source changed")
    before = imports(BASE)
    removed = {"audio_terminal_ui_action_5e69a0"}
    if len(before) != 168 or not removed <= before:
        raise RuntimeError("Apollo candidate frontier changed")
    objects = []
    for source, output in zip(SOURCES, (OUT / "reply-action-bind.o", OUT / "reply-send-bind.o")):
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(output)], check=True)
        objects.append(output)
    linked = OUT / "apollo-main-query-reply-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                    *(str(p) for p in objects), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != removed or after - before or len(after) != 167:
        raise RuntimeError(f"unexpected import change: {before-after=} {after-before=} {len(after)=}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_REPLY_C",
               "sources": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in SOURCES],
               "oracle_receipts": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in ORACLES],
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "objects": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in objects],
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "unresolved_before": 168,
               "unresolved_after": 167, "imports_resolved": sorted(removed),
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Bounded action and sender comparisons passed; lower UI/transport, whole image and hardware remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sha(path))


if __name__ == "__main__":
    main()
