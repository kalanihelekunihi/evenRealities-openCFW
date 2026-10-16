#!/usr/bin/env python3
"""Bind Terminal row imports to existing C-owned stock-address providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-row-bind-5ea564/apollo-main-terminal-row-bind-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-row-existing-aliases"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_row_existing_aliases_20261016.c"
PAIRS = {
    "audio_lv_child_44dce2": "audio_uart_lv_child_get_44dce2",
    "audio_lv_child_count_44ddea": "audio_uart_lv_child_count_44ddea",
    "audio_lv_color_44104c": "audio_uart_page_44104c",
    "audio_lv_delete_44d7b8": "audio_uart_page_delete_event_filter_44d7b8",
    "audio_lv_image_create_498668": "audio_uart_page_498668",
    "audio_lv_image_source_498680": "audio_uart_page_498680",
    "audio_lv_label_create_499416": "audio_uart_page_499416",
    "audio_lv_label_mode_499678": "audio_uart_page_layout_499678",
    "audio_lv_label_text_49942e": "audio_uart_page_49942e",
    "audio_lv_style_a_44145a": "audio_uart_page_44145a",
    "audio_lv_style_alpha_44142e": "audio_uart_page_44142e",
    "audio_lv_style_color_44140e": "audio_uart_page_44140e",
    "audio_lv_style_font_44143e": "audio_uart_page_44143e",
    "audio_lv_style_opa_441488": "audio_uart_display_audio_reset_441488",
    "audio_lv_style_spacing_44144c": "audio_uart_page_44144c",
    "audio_lv_width_43f506": "audio_uart_page_43f506",
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", flag, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if len(before) != 243 or not PAIRS.keys() <= before or not set(PAIRS.values()) <= defined:
        raise RuntimeError("Terminal row existing-provider frontier changed")
    obj = OUT / "terminal_row_existing_aliases_20261016.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if symbols(obj, "-u") != set(PAIRS.values()) or not PAIRS.keys() <= symbols(obj, "--defined-only"):
        raise RuntimeError("Terminal row adapter ABI target set changed")
    linked = OUT / "apollo-main-terminal-row-existing-aliases-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before-after != PAIRS.keys() or after-before or len(after) != 227:
        raise RuntimeError("Terminal row adapter linked frontier changed")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_ROW_EXISTING_ALIASES_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "provider_pairs": PAIRS, "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 243, "unresolved_after": 227,
              "imports_resolved": sorted(PAIRS), "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Existing provider lower-effect gates and final placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))

if __name__ == "__main__":
    main()
