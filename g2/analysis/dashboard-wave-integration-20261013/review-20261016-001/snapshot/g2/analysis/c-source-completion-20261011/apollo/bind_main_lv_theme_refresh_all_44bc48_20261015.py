#!/usr/bin/env python3
"""Bind native-checked LV theme refresh traversal into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_theme_refresh_all_44bc48.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-theme-refresh-all-44bc48/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-page-instance-487022/apollo-main-lv-page-instance-487022.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-theme-refresh-all-44bc48"
OWNED = {"audio_uart_lv_theme_refresh_all_44bc48", "audio_uart_lv_theme_refresh_node_44c970"}
RESOLVED = {"audio_uart_lv_theme_refresh_all_44bc48"}
CHILDREN = {"audio_uart_display_lv_state", "audio_uart_lv_child_count_44ddea", "audio_uart_lv_display_next_44fa22", "audio_uart_lv_style_removed_44ce2a", "audio_uart_page_style_refresh_44bc8c", "audio_uart_page_style_selector_44b860"}
BODIES = {
    "audio_uart_lv_theme_refresh_all_44bc48": "6bda860a385a47f966111cef8726e8ca0df39bc319a07a613b3cb600f107ae6c",
    "audio_uart_lv_theme_refresh_node_44c970": "c161d4db861605518d2d2d272b3f6aa1b69d8820c19f045dfd22bff1050dc16f",
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_THEME_REFRESH_ALL_44BC48" or \
       oracle["cases"] != 144 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or oracle["native_body_sha256"] != BODIES:
        raise RuntimeError("Native LV theme refresh evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_theme_refresh_all_44bc48.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN:
        raise RuntimeError("LV theme refresh symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 218 or not RESOLVED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV theme refresh base contract changed")
    linked = OUT / "apollo-main-lv-theme-refresh-all-44bc48.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before or len(after) != 217:
        raise RuntimeError("LV theme refresh link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_THEME_REFRESH_ALL_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"],
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(RESOLVED), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
