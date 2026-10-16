#!/usr/bin/env python3
"""Bind stock-compared Terminal UI start and expose its two children."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_start_5e716c.c"
BASE = G2 / "build/c-firmware/20261016/main-terminal-display-state-notify/apollo-main-terminal-display-state-notify-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/main-terminal-ui-start-5e716c/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-start-5e716c"
SYMBOL = "audio_terminal_ui_start_5e716c"
ADDED = {"audio_terminal_ui_theme_5e47cc", "audio_terminal_list_anim_init_58966c"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_START_C_ORACLE"
            or oracle["cases"] != 9 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("Terminal UI start oracle changed")
    before = imports(BASE)
    if len(before) != 168 or SYMBOL not in before:
        raise RuntimeError("Apollo Terminal UI start frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_ui_start.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-ui-start-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before-after != {SYMBOL} or after-before != ADDED or len(after) != 169:
        raise RuntimeError(f"Terminal UI start binding frontier changed: {len(after)} {after-before}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_START_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 168, "unresolved_after": 169,
              "imports_resolved": [SYMBOL], "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
