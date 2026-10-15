#!/usr/bin/env python3
"""Bind LV 0x4405d4 event import to its existing source-owned body."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_invalidate_alias_4405d4.c"
EXISTING = G2 / "components/audio/uart_thread_source_candidate/display_lv_invalidate_area.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_display_lv_invalidate_area.py"
OUT = G2 / "build/c-firmware/20261015/main-lv-invalidate-alias-4405d4"
BASE = G2 / "build/c-firmware/20261015/main-lv-scroll-to-view-44ea56/apollo-main-lv-scroll-to-view-44ea56.o"
OWNED = {"audio_uart_lv_invalidate_area_4405d4"}
TARGET = "audio_uart_display_invalidate_area"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_invalidate_alias_4405d4.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    oracle = subprocess.run([sys.executable, str(ORACLE)], check=True,
                            capture_output=True, text=True).stdout.strip().splitlines()
    if len(oracle) != 4 or any(not line.startswith("PASS LV area ") for line in oracle):
        raise RuntimeError("existing area invalidator native comparison changed")
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != {TARGET}:
        raise RuntimeError("invalidate alias object contract changed")
    if TARGET not in symbols(BASE, "--defined-only"):
        raise RuntimeError("source-owned invalidate target missing")
    linked = OUT / "apollo-main-lv-invalidate-alias-4405d4.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before - after != OWNED or after - before or len(before) != 238 or
            len(after) != 237 or not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("invalidate alias linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_INVALIDATE_ALIAS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "existing_source": str(EXISTING.relative_to(ROOT)),
               "existing_source_sha256": sha(EXISTING),
               "existing_oracle": str(ORACLE.relative_to(ROOT)),
               "existing_oracle_sha256": sha(ORACLE), "existing_oracle_cases": oracle,
               "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["The address-labeled event import forwards to an existing source-owned body; its four native branch cases do not prove live display invalidation."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
