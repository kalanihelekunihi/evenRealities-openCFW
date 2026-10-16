#!/usr/bin/env python3
"""Bind Terminal notification restore and its one-step LVGL scroll child."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-action-asr-start-5e5a7e/apollo-main-terminal-ui-action-asr-start-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-notification-restore-5ebfae"
SOURCES = [
    (G2 / "components/audio/uart_thread_source_candidate/terminal_ui_notification_restore_5ebfae.c",
     OUT / "oracle-receipt.json",
     "PASS_EXPERIMENTAL_TERMINAL_UI_NOTIFICATION_RESTORE_C_ORACLE", 24),
    (G2 / "components/audio/uart_thread_source_candidate/terminal_ui_scroll_to_view_44ea2e.c",
     G2 / "build/c-firmware/20261016/main-terminal-ui-scroll-to-view-44ea2e/oracle-receipt.json",
     "PASS_EXPERIMENTAL_TERMINAL_UI_SCROLL_TO_VIEW_C_ORACLE", 18)]
SYMBOL = "audio_terminal_ui_notification_restore_5ebfae"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    before = imports(BASE)
    if len(before) != 214 or SYMBOL not in before:
        raise RuntimeError("Apollo Terminal notification restore frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    refs, objects = [], []
    for source, oracle_path, status, cases in SOURCES:
        oracle = json.loads(oracle_path.read_text())
        if oracle["status"] != status or oracle["cases"] != cases or \
                oracle["source_sha256"] != sha(source):
            raise RuntimeError(f"Terminal restore oracle changed: {source}")
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)], check=True)
        refs.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                     "oracle_receipt": str(oracle_path.relative_to(ROOT)),
                     "oracle_receipt_sha256": sha(oracle_path),
                     "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj)})
        objects.append(obj)
    linked = OUT / "apollo-main-terminal-ui-notification-restore-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                    *(str(obj) for obj in objects), "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != {SYMBOL} or after-before or len(after) != 213:
        raise RuntimeError(f"Terminal notification restore binding frontier changed: {len(after)}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_NOTIFICATION_RESTORE_C",
              "sources": refs,
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 214, "unresolved_after": 213,
              "imports_resolved": [SYMBOL], "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["LVGL lower-call effects, shared Terminal RAM allocation and hardware remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
