#!/usr/bin/env python3
"""Bind three Terminal imports to existing C-owned LVGL stock-address providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-view-row-5ea768/apollo-main-terminal-view-row-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-lv-existing-aliases"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_lv_existing_aliases_20261016.c"
FLAGS_SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_flags_43ded4.c"
POSITION_SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_set_pos_43f09a.c"
RESOLVED = {"audio_lv_object_flag_43ded4", "audio_lv_object_clear_flag_43dfa4",
            "audio_lv_object_position_43f09a"}
PROVIDERS = {"audio_uart_page_43ded4", "audio_uart_page_43dfa4", "audio_uart_page_43f09a"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", flag, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if len(before) != 229 or not RESOLVED <= before or not PROVIDERS <= defined:
        raise RuntimeError("Terminal LVGL C provider frontier changed")
    obj = OUT / "terminal_lv_existing_aliases_20261016.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if symbols(obj, "-u") != PROVIDERS or not RESOLVED <= symbols(obj, "--defined-only"):
        raise RuntimeError("Terminal LVGL alias ABI target set changed")
    linked = OUT / "apollo-main-terminal-lv-existing-aliases-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before or len(after) != 226:
        raise RuntimeError("Terminal LVGL alias linked frontier changed")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_LV_EXISTING_ALIASES_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "existing_provider_sources": [
                  {"path": str(p.relative_to(ROOT)), "sha256": sha(p)}
                  for p in (FLAGS_SOURCE, POSITION_SOURCE)],
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 229, "unresolved_after": 226,
              "imports_resolved": sorted(RESOLVED), "imports_added": [],
              "provider_symbols": sorted(PROVIDERS), "source_complete": False,
              "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Underlying LVGL provider lower effects and final placement retain their prior gates."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))

if __name__ == "__main__":
    main()
