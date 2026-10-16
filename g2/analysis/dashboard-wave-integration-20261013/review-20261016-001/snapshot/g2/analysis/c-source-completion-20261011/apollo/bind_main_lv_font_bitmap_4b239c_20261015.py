#!/usr/bin/env python3
"""Bind native-compared LV font bitmap callback into Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_font_bitmap_4b239c.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-font-bitmap-4b239c"
BASE = G2 / "build/c-firmware/20261015/main-lv-font-lookup-4b2774/apollo-main-lv-font-lookup-4b2774.o"
ORACLE = HERE / "verify_main_lv_font_bitmap_4b239c_oracle_20261015.py"
RESOLVED = {"audio_uart_lv_font_glyph_bitmap_4b239c"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_font_bitmap_4b239c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_FONT_BITMAP_ORACLE" or \
            oracle["cases"] != 198 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("LV glyph bitmap oracle changed")
    linked = OUT / "apollo-main-lv-font-bitmap-4b239c.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE), symbols(linked)
    if before - after != RESOLVED or after - before or len(before) != 235 or len(after) != 234:
        raise RuntimeError("LV glyph bitmap import contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_FONT_BITMAP_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(RESOLVED), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": oracle["limits"]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
