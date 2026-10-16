#!/usr/bin/env python3
"""Bind the native-checked object style lookup and byte-property adapter."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_page_style_get_44beaa.c"
ORACLE = G2 / "build/c-firmware/20261015/main-page-style-get-44beaa/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-obj-set-xy-43f0e0/apollo-main-obj-set-xy-43f0e0.o"
OUT = G2 / "build/c-firmware/20261015/main-page-style-get-44beaa"
OWNED = {"audio_uart_page_style_get_44beaa", "audio_uart_lv_style_get_482946"}
RESOLVED = {"audio_uart_page_style_get_44beaa"}
ADDED = {"audio_uart_lv_style_lookup_482716"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_PAGE_STYLE_GET_44BEAA" or \
       oracle["cases"] != 144 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or \
       oracle["native_body_sha256"] != {
           "audio_uart_page_style_get_44beaa": "214aab7d6730ee19594135e0aa8533eb1f8ff0f02d00567304c245d89064a4ae",
           "audio_uart_lv_style_get_482946": "152db6bc74bffc0424ceeb1dc3eeaffabef107ac09a125bfbfc4c0093ccfb7af"}:
        raise RuntimeError("Native style-get evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_page_style_get_44beaa.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != ADDED:
        raise RuntimeError("Style-get object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 229 or not RESOLVED <= before or \
       ADDED & (before | symbols(BASE, "--defined-only")):
        raise RuntimeError("Style-get base contract changed")
    linked = OUT / "apollo-main-page-style-get-44beaa.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before != ADDED or len(after) != 229:
        raise RuntimeError("Style-get link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_STYLE_GET_C",
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
               "limits": ["The lower style lookup at 0x482716 remains unresolved.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
