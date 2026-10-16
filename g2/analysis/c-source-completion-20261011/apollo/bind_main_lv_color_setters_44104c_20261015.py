#!/usr/bin/env python3
"""Bind the bounded native RGB888/color-wrapper contract into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_color_setters_44104c.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-color-setters-44104c/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-anim-remove-450910/apollo-main-lv-anim-remove-450910.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-color-setters-44104c"
OWNED = {"audio_uart_page_44104c", "audio_uart_page_44127e", "audio_uart_page_4412ec", "audio_uart_page_44140e"}
CHILDREN = {"audio_uart_page_style_apply_44be4c"}
BODIES = {
    "audio_uart_page_44104c": "b8269841f44758fab58740c80273272f4ebd3e195c294a0e49b3b3fd91e3165c",
    "audio_uart_page_44127e": "0381c19c8ddf07926776974f7d57426e8cf2bfef04af99b8cf34ccc0f4e70ac2",
    "audio_uart_page_4412ec": "8d131c30f9d3863d960e2f7ca47a6ea9f5471a339e5d3a4c2d6eabbe44e39b23",
    "audio_uart_page_44140e": "0d3afaa58cbe307d5167a807268b52cc78b83c904d37fa8269ff245c5e915cca",
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_COLOR_SETTERS_44104C" or \
       oracle["cases"] != 144 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or oracle["native_body_sha256"] != BODIES:
        raise RuntimeError("Native LV color wrapper evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_color_setters_44104c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN:
        raise RuntimeError("LV color wrapper object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 222 or not OWNED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV color wrapper base contract changed")
    linked = OUT / "apollo-main-lv-color-setters-44104c.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != OWNED or after - before or len(after) != 218:
        raise RuntimeError("LV color wrapper link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_COLOR_SETTERS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"],
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(OWNED), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Native color wrappers leave the upper stack byte unspecified; the bound contract covers RGB888 and style property calls.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
