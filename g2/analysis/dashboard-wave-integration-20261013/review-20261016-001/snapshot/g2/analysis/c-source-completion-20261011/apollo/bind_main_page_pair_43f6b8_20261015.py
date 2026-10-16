#!/usr/bin/env python3
"""Bind the native-checked LV page pair into the Main C object chain."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_page_pair_43f6b8.c"
ORACLE = G2 / "build/c-firmware/20261015/main-page-pair-43f6b8/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-graphics-nema-alias-513924/apollo-main-graphics-nema-alias-513924.o"
OUT = G2 / "build/c-firmware/20261015/main-page-pair-43f6b8"
OWNED = {"audio_uart_page_4411d4", "audio_uart_page_43f6b8"}
RESOLVED = {"audio_uart_page_43f6b8"}
ADDED = {"audio_uart_page_43f09a"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_PAGE_PAIR_43F6B8" or \
       oracle["cases"] != 48 or oracle["source_sha256"] != sha(SOURCE) or \
       oracle["native_body_sha256"] != {
           "audio_uart_page_4411d4": "3d89696d92cb859542f864c6b2be546106c8b50f9fbf294fd9b93471e3e46da9",
           "audio_uart_page_43f6b8": "f55ca5ad1ac8828e95f6f2fd2964ce7df23499ef42df073b85afb9ef25f583f2"} or \
       set(oracle["source_owned_symbols"]) != OWNED:
        raise RuntimeError("Page pair native evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_page_pair_43f6b8.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or \
       symbols(obj, "-u") != {"audio_uart_page_style_apply_44be4c", *ADDED}:
        raise RuntimeError("Page pair object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 231 or not RESOLVED <= before or \
       "audio_uart_page_style_apply_44be4c" not in symbols(BASE, "--defined-only"):
        raise RuntimeError("Page pair base contract changed")
    linked = OUT / "apollo-main-page-pair-43f6b8.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before != ADDED or len(after) != 231:
        raise RuntimeError("Page pair link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_PAIR_C",
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
               "limits": ["The nested provider at 0x43f09a remains unresolved.",
                          "The 48 comparisons cover call sequence and arguments only."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
