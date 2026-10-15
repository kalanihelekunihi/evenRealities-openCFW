#!/usr/bin/env python3
"""Bind native-compared LVGL deferred callback cleanup into Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_cleanup_matching_484052.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-cleanup-matching-484052"
BASE = G2 / "build/c-firmware/20261015/main-lv-input-event-453002/apollo-main-lv-input-event-453002.o"
ORACLE = HERE / "verify_main_lv_cleanup_matching_484052_oracle_20261015.py"
RESOLVED = {"audio_uart_lv_cleanup_matching_484052"}
ADDED = {"audio_uart_lv_timer_iter_4645ec", "audio_uart_lv_timer_remove_4644ee"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", flag, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_cleanup_matching_484052.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-lv-cleanup-matching-484052.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if before - after != RESOLVED or after - before != ADDED or \
            len(before) != 239 or len(after) != 240:
        raise RuntimeError("cleanup matching import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_CLEANUP_MATCHING_ORACLE" or \
            oracle["cases"] != 589 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("cleanup matching oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_CLEANUP_MATCHING_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": oracle["limits"] + ["Full image and device behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
