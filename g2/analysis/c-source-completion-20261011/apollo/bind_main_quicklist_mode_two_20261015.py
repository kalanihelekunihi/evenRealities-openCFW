#!/usr/bin/env python3
"""Bind native-compared QuickList add-up mode into Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_mode_two_4f5a1c.c"
BASE = G2 / "build/c-firmware/20261015/main-quicklist-select-records/apollo-main-quicklist-select-records.o"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-mode-two"
ORACLE = HERE / "verify_main_quicklist_mode_two_oracle_20261015.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    return {row.split()[-1] for row in
            subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_mode_two_4f5a1c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SRC), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_quicklist_mode_two_4f5a1c"}:
        raise RuntimeError("QuickList mode-two definition changed")
    linked = OUT / "apollo-main-quicklist-mode-two.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = names(BASE, "-u"), names(linked, "-u")
    if before-after != {"audio_quicklist_mode_two_4f5a1c"} or after-before:
        raise RuntimeError("Main mode-two import delta changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_TWO_ORACLE" or oracle["cases"] != 150:
        raise RuntimeError("QuickList mode-two oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_TWO_C",
               "source": str(SRC.relative_to(ROOT)), "source_sha256": sha(SRC),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
               "oracle_script": str(ORACLE.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE),
               "native_cases": 150, "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Mode-two detail, mode three and auxiliary update remain unresolved.",
                          "Native/C comparison controls the selector, copy, record and auxiliary lower calls.",
                          "Final RAM placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
