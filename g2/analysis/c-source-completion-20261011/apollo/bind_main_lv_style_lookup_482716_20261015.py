#!/usr/bin/env python3
"""Bind the native-checked dense/sparse LV style lookup into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_style_lookup_482716.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-style-lookup-482716/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-page-style-get-44beaa/apollo-main-page-style-get-44beaa.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-style-lookup-482716"
OWNED = {"audio_uart_lv_style_is_sparse_482708", "audio_uart_lv_style_lookup_482716"}
RESOLVED = {"audio_uart_lv_style_lookup_482716"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_STYLE_LOOKUP_482716" or \
       oracle["cases"] != 62 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or \
       oracle["native_body_sha256"] != {
           "audio_uart_lv_style_is_sparse_482708": "5f4d8578d1c93ca71614bc46df4d853223c3b8e389efde4fef5231c6cde6f999",
           "audio_uart_lv_style_lookup_482716": "094798629ce86c61f6c7e0aee2be68676cb8e7629dba07c4d0a2959a63dabcce"}:
        raise RuntimeError("Native LV style lookup evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_style_lookup_482716.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u"):
        raise RuntimeError("LV style lookup object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 229 or not RESOLVED <= before:
        raise RuntimeError("LV style lookup base contract changed")
    linked = OUT / "apollo-main-lv-style-lookup-482716.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before or len(after) != 228:
        raise RuntimeError("LV style lookup link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_STYLE_LOOKUP_C",
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
               "limits": ["Sparse lookup requires a zero-key terminator in native data.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
