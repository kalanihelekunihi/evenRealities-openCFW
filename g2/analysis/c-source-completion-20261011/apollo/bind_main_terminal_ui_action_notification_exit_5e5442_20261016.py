#!/usr/bin/env python3
"""Bind two Terminal FSM exit actions and stock-compared fade-out provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-notification-restore-5ebfae/apollo-main-terminal-ui-notification-restore-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-notification-exit-5e5442"
SOURCES = [
    (G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_notification_exit_5e5442.c",
     OUT / "oracle-receipt.json",
     "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_NOTIFICATION_EXIT_C_ORACLE", 108),
    (G2 / "components/audio/uart_thread_source_candidate/terminal_fade_out_58c426.c",
     G2 / "build/c-firmware/20261016/main-terminal-fade-out-58c426/oracle-receipt.json",
     "PASS_NATIVE_MAIN_TERMINAL_FADE_OUT_58C426", 300)]
RESOLVED = {"audio_terminal_ui_action_5e5442", "audio_terminal_ui_action_5ed748"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    before = imports(BASE)
    if len(before) != 213 or not RESOLVED <= before:
        raise RuntimeError("Apollo Terminal exit action frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    refs, objects = [], []
    for source, oracle_path, status, cases in SOURCES:
        oracle = json.loads(oracle_path.read_text())
        if oracle["status"] != status or oracle["cases"] != cases or \
                oracle["source_sha256"] != sha(source):
            raise RuntimeError(f"Terminal exit/fade oracle changed: {source}")
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)], check=True)
        refs.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                     "oracle_receipt": str(oracle_path.relative_to(ROOT)),
                     "oracle_receipt_sha256": sha(oracle_path),
                     "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj)})
        objects.append(obj)
    linked = OUT / "apollo-main-terminal-ui-action-notification-exit-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                    *(str(obj) for obj in objects), "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before or len(after) != 211:
        raise RuntimeError(f"Terminal exit action binding frontier changed: {len(after)} {after-before}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_NOTIFICATION_EXIT_C",
              "sources": refs,
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 213, "unresolved_after": 211,
              "imports_resolved": sorted(RESOLVED), "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["LVGL animation runtime, object lifetime, callback concurrency and hardware remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
