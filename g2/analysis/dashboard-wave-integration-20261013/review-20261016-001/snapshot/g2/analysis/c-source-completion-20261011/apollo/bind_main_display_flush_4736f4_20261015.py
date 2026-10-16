#!/usr/bin/env python3
"""Bind native-compared display flush callback and source-owned pointer."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_flush_callback_4736f4.c"
OUT = G2 / "build/c-firmware/20261015/main-display-flush-4736f4"
BASE = G2 / "build/c-firmware/20261015/main-lv-delete-filter-44d7b8/apollo-main-lv-delete-filter-44d7b8.o"
ORACLE = HERE / "verify_main_display_flush_4736f4_oracle_20261015.py"
RESOLVED = {"audio_uart_display_flush_callback"}
ADDED = {"audio_uart_display_area_copy_439c04", "audio_uart_display_area_x_44fb4e",
         "audio_uart_display_area_y_44fb9a", "audio_uart_display_flush_begin_47381e",
         "audio_uart_display_flush_end_47386a", "audio_uart_display_flush_ready_44fc42",
         "audio_uart_display_flush_transfer_47366c", "audio_uart_display_flush_view_474066"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", flag, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_flush_callback_4736f4.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-display-flush-4736f4.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if before - after != RESOLVED or after - before != ADDED or \
            len(before) != 236 or len(after) != 243:
        raise RuntimeError("display flush import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_ORACLE" or \
            oracle["cases"] != 36 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("display flush oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": oracle["limits"] + ["Eight lower display operations need source ownership."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
