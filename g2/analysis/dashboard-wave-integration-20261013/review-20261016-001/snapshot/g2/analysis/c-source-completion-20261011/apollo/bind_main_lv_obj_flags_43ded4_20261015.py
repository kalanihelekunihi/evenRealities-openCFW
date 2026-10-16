#!/usr/bin/env python3
"""Bind native-checked LV object flag add/remove bodies into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_flags_43ded4.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-obj-flags-43ded4/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-color-setters-44104c/apollo-main-lv-color-setters-44104c.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-obj-flags-43ded4"
OWNED = {"audio_uart_page_43ded4", "audio_uart_page_43dfa4", "audio_uart_lv_obj_has_state_43e184"}
RESOLVED = {"audio_uart_page_43ded4", "audio_uart_page_43dfa4"}
CHILDREN = {"audio_uart_lv_get_scrollbar_areas_44eb28", "audio_uart_lv_invalidate_area_4405d4", "audio_uart_lv_layout_positioned_43f612", "audio_uart_lv_mark_layout_43f648", "audio_uart_lv_obj_group_43e1be", "audio_uart_lv_obj_has_flag_43e0e0", "audio_uart_lv_obj_has_flag_any_43e11c", "audio_uart_lv_obj_parent_44dca2", "audio_uart_page_active_object_44d58c", "audio_uart_page_invalidate_440656", "audio_uart_page_update_unbound_44d45c"}
BODIES = {
    "audio_uart_page_43ded4": "b48425eea285357ae7de5454472c573840fdc05a6ddf92c7507aaf1d469540ee",
    "audio_uart_page_43dfa4": "e48de51576f2a7bcc536d1669b5c903bb9cdfe4bba118af965ebe4a4a2007488",
    "audio_uart_lv_obj_has_state_43e184": "087d0b27daf769f54f8c4c47c41f2fd0bb75c6dec29810e1f775e099a257dc12",
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_OBJ_FLAGS_43DED4" or \
       oracle["cases"] != 193 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or oracle["native_body_sha256"] != BODIES:
        raise RuntimeError("Native LV object flag evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_obj_flags_43ded4.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN:
        raise RuntimeError("LV object flag symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 218 or not RESOLVED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV object flag base contract changed")
    linked = OUT / "apollo-main-lv-obj-flags-43ded4.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before or len(after) != 216:
        raise RuntimeError("LV object flag link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_OBJ_FLAGS_C",
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
               "limits": ["Null-object fatal branches remain outside the controlled native oracle.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
