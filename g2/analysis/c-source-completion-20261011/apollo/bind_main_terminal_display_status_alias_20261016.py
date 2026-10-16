#!/usr/bin/env python3
"""Bind Terminal name for the stock-compared LVGL scroll-to-Y provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-image-set-5e47fe/apollo-main-terminal-image-set-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-display-status-alias-44ea04"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_display_status_alias_44ea04.c"
PROVIDER = G2 / "components/audio/uart_thread_source_candidate/display_lv_scroll_axes_44e9da.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-scroll-axes-44e9da/oracle.json"
RESOLVED = {"audio_terminal_display_status_44ea04"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def defined(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "--defined-only", str(path)], text=True).splitlines()
            if len(line.split()) >= 3}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_AXES_ORACLE" or \
            oracle["cases"] != 80 or oracle["source_sha256"] != sha(PROVIDER) or \
            "0x44ea04..0x44ea2d" not in oracle["native_spans"]:
        raise RuntimeError("LVGL scroll-to-Y stock oracle changed")
    before = imports(BASE)
    if len(before) != 218 or not RESOLVED <= before or \
            "audio_uart_lv_scroll_to_y_44ea04" not in defined(BASE):
        raise RuntimeError("Terminal display-status alias frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_display_status_alias_44ea04.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-display-status-alias-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before or len(after) != 217:
        raise RuntimeError(f"Terminal display-status alias frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_DISPLAY_STATUS_ALIAS_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "provider": str(PROVIDER.relative_to(ROOT)), "provider_sha256": sha(PROVIDER),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 218, "unresolved_after": 217,
              "imports_resolved": sorted(RESOLVED), "imports_added": [],
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Five lower scroll calls were controlled by the provider oracle; final LVGL effects and placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))

if __name__ == "__main__":
    main()
