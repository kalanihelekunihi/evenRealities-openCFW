#!/usr/bin/env python3
"""Bind stock-compared Terminal tick, timer, voice and elapsed providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-theme-5e47cc/apollo-main-terminal-ui-theme-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-tick-5e8008"
SOURCES = [
    (G2 / "components/audio/uart_thread_source_candidate/terminal_ui_tick_5e8008.c",
     OUT / "oracle-receipt.json", "PASS_EXPERIMENTAL_TERMINAL_UI_TICK_C_ORACLE", 96),
    (G2 / "components/audio/uart_thread_source_candidate/terminal_timer_expired_5e7ea4.c",
     G2 / "build/c-firmware/20261016/main-terminal-timer-expired-5e7ea4/oracle-receipt.json",
     "PASS_EXPERIMENTAL_TERMINAL_TIMER_EXPIRED_C_ORACLE", 252),
    (G2 / "components/audio/uart_thread_source_candidate/terminal_voice_input_encode_5cec72.c",
     G2 / "build/c-firmware/20261016/main-terminal-voice-input-encode-5cec72/oracle-receipt.json",
     "PASS_EXPERIMENTAL_TERMINAL_VOICE_INPUT_C_ORACLE", 24),
    (G2 / "components/audio/uart_thread_source_candidate/td_record_elapsed_get_59769c.c",
     G2 / "build/c-firmware/20261016/main-td-record-elapsed-get-59769c/oracle-receipt.json",
     "PASS_EXPERIMENTAL_TD_RECORD_ELAPSED_C_ORACLE", 160)]
SYMBOL = "audio_terminal_ui_tick_5e8008"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    before = imports(BASE)
    if len(before) != 167 or SYMBOL not in before:
        raise RuntimeError("Apollo Terminal tick frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    source_refs = []
    objects = []
    for source, oracle_path, status, cases in SOURCES:
        oracle = json.loads(oracle_path.read_text())
        if oracle["status"] != status or oracle["cases"] != cases or \
                oracle["source_sha256"] != sha(source):
            raise RuntimeError(f"Terminal tick dependency oracle changed: {source}")
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)], check=True)
        objects.append(obj)
        source_refs.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                            "oracle_receipt": str(oracle_path.relative_to(ROOT)),
                            "oracle_receipt_sha256": sha(oracle_path),
                            "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj)})
    linked = OUT / "apollo-main-terminal-ui-tick-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                    *(str(obj) for obj in objects), "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != {SYMBOL} or after-before or len(after) != 166:
        raise RuntimeError(f"Terminal tick binding frontier changed: {len(after)} {after-before}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_TICK_C",
              "sources": source_refs,
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 167, "unresolved_after": 166,
              "imports_resolved": [SYMBOL], "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Enabled logging, lower-call effects, real timer/RTC, RAM aliasing and hardware remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
