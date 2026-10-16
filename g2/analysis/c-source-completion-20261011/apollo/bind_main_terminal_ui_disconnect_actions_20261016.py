#!/usr/bin/env python3
"""Bind stock-compared Terminal disconnect actions and assets into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-display-status-alias-44ea04/apollo-main-terminal-display-status-alias-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-disconnect-actions"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_disconnect_actions_20261016.c"
ASSETS = G2 / "components/audio/uart_thread_source_candidate/terminal_fsm_disconnect_assets_20261016.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_ui_action_5e522e",
            "audio_terminal_ui_action_5e52c2",
            "audio_terminal_ui_action_5e5320",
            "audio_terminal_ui_action_5e53b8"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_DISCONNECT_ACTIONS_C_ORACLE" or \
            oracle["cases"] != 512 or oracle["source_sha256"] != sha(SOURCE) or \
            oracle["assets_sha256"] != sha(ASSETS):
        raise RuntimeError("Terminal disconnect actions oracle changed")
    before = imports(BASE)
    if len(before) != 217 or not RESOLVED <= before:
        raise RuntimeError("Terminal disconnect actions frontier changed")
    obj = OUT / "terminal_ui_disconnect_actions_20261016.o"
    assets_obj = OUT / "terminal_fsm_disconnect_assets_20261016.o"
    for source, output in ((SOURCE, obj), (ASSETS, assets_obj)):
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(source), "-o", str(output)], check=True)
    linked = OUT / "apollo-main-terminal-ui-disconnect-actions-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), str(assets_obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before or len(after) != 213:
        raise RuntimeError(f"Terminal disconnect actions frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_DISCONNECT_ACTIONS_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "assets": str(ASSETS.relative_to(ROOT)), "assets_sha256": sha(ASSETS),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "assets_object": str(assets_obj.relative_to(ROOT)),
              "assets_object_sha256": sha(assets_obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 217, "unresolved_after": 213,
              "imports_resolved": sorted(RESOLVED), "imports_added": [],
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Lower LVGL effects and final RAM/resource placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))

if __name__ == "__main__":
    main()
