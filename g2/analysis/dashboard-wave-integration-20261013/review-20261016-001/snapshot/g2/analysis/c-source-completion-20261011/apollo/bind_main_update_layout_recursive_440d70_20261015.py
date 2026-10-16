#!/usr/bin/env python3
"""Bind the native-checked recursive LV layout traversal into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_update_layout_recursive_440d70.c"
ORACLE = G2 / "build/c-firmware/20261015/main-update-layout-recursive-440d70/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-update-layout-43f66c/apollo-main-update-layout-43f66c.o"
OUT = G2 / "build/c-firmware/20261015/main-update-layout-recursive-440d70"
OWNED = {"audio_uart_lv_obj_update_layout_440d70"}
ADDED = {"audio_uart_lv_obj_refr_pos_43ffd0", "audio_uart_lv_obj_layout_apply_4546f4",
         "audio_uart_lv_obj_scroll_reconcile_44f316"}
CHILDREN = {"audio_uart_lv_child_count_44ddea", "audio_uart_lv_basic_invalidate_43f1a4"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_UPDATE_LAYOUT_RECURSIVE_440D70" or \
       oracle["cases"] != 40 or oracle["source_sha256"] != sha(SOURCE) or \
       oracle["native_body_sha256"] != "b7ab4305a7cc20a086a8df4692719b7d71432e3a4e7ef5edbacea1d3c75730c1":
        raise RuntimeError("Native recursive layout evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_update_layout_recursive_440d70.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or \
       symbols(obj, "-u") != CHILDREN | ADDED:
        raise RuntimeError("Recursive layout object symbol contract changed")
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if len(before) != 224 or not OWNED <= before or \
       not CHILDREN <= defined or ADDED & (before | defined):
        raise RuntimeError("Recursive layout base contract changed")
    linked = OUT / "apollo-main-update-layout-recursive-440d70.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != OWNED or after - before != ADDED or len(after) != 226:
        raise RuntimeError("Recursive layout link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_UPDATE_LAYOUT_RECURSIVE_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"],
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(OWNED), "imports_added": sorted(ADDED),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Position, layout-apply and scroll providers remain unresolved.",
                          "Child count and effects were controlled native comparisons."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
