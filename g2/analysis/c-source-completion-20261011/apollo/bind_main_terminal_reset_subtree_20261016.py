#!/usr/bin/env python3
"""Bind stock-compared Terminal empty-list subtree into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-even-ai-app-release/apollo-main-even-ai-app-release-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-reset-subtree-5ea342"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_reset_subtree_5ea342.c"
ASSETS = G2 / "components/audio/uart_thread_source_candidate/terminal_reset_assets_20261016.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_reset_subtree_5ea342"}
ADDED = {"audio_terminal_lv_style_four_5ea224",
         "audio_terminal_initial_image_y_5ea2d4"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_RESET_SUBTREE_C_ORACLE" or \
            oracle["cases"] != 48 or oracle["source_sha256"] != sha(SOURCE) or \
            oracle["assets_sha256"] != sha(ASSETS):
        raise RuntimeError("Terminal reset subtree oracle changed")
    before = imports(BASE)
    if len(before) != 221 or not RESOLVED <= before:
        raise RuntimeError("Terminal reset subtree frontier changed")
    obj = OUT / "terminal_reset_subtree_5ea342.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    assets_obj = OUT / "terminal_reset_assets_20261016.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(ASSETS), "-o", str(assets_obj)], check=True)
    linked = OUT / "apollo-main-terminal-reset-subtree-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), str(assets_obj), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before != ADDED or len(after) != 222:
        raise RuntimeError(f"Terminal reset subtree frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESET_SUBTREE_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "assets": str(ASSETS.relative_to(ROOT)), "assets_sha256": sha(ASSETS),
              "assets_object": str(assets_obj.relative_to(ROOT)), "assets_object_sha256": sha(assets_obj),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 221, "unresolved_after": 222,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Two style/layout children, lower LVGL effects, source-resource linker relocation and final RAM placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))

if __name__ == "__main__":
    main()
