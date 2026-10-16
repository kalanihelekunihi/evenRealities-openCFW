#!/usr/bin/env python3
"""Bind native-checked LV page instance/cache constructor into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_page_instance_487022.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-page-instance-487022/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-obj-flags-43ded4/apollo-main-lv-obj-flags-43ded4.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-page-instance-487022"
OWNED = {"audio_uart_page_487022", "audio_uart_page_instance_ready_48716c", "audio_uart_page_rgb_equal_44102e"}
RESOLVED = {"audio_uart_page_487022"}
ADDED = {"audio_uart_lv_page_build_484a98", "audio_uart_lv_page_callback_487188", "audio_uart_lv_theme_refresh_all_44bc48"}
CHILDREN = {"audio_uart_display_current_44fa1a", "audio_uart_display_lv_state", "audio_uart_lv_display_dpi_44fbe6", "audio_uart_lv_display_width_44fa7e", "audio_uart_lv_heap_alloc", "audio_uart_lv_theme_lookup_44fe7e"}
BODIES = {
    "audio_uart_page_487022": "19eafca08a3f3a0e1ccf6c57ba4ba8a78c1deef3fcd7a020628eb53d48186b29",
    "audio_uart_page_instance_ready_48716c": "dd2223882596cb5236af83a6c2b86b4ff5b8ec700a0eaeaacd30bc95966f1b11",
    "audio_uart_page_rgb_equal_44102e": "ff83129985844ad55af5d72a6db300dc1ae6789dab91b44c02b6401bd0e18ddd",
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_PAGE_INSTANCE_487022" or \
       oracle["cases"] != 168 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or oracle["native_body_sha256"] != BODIES:
        raise RuntimeError("Native LV page instance evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_page_instance_487022.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN | ADDED:
        raise RuntimeError("LV page instance symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 216 or not RESOLVED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV page instance base contract changed")
    linked = OUT / "apollo-main-lv-page-instance-487022.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before != ADDED or len(after) != 218:
        raise RuntimeError("LV page instance link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_PAGE_INSTANCE_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"],
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Page build, callback and theme refresh are deeper source dependencies.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
