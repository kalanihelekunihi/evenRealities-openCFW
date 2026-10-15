#!/usr/bin/env python3
"""Bind native-compared QuickList row selector into Apollo Main C graph."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_select_records_4f5662.c"
BASE = G2 / "build/c-firmware/20261015/main-quicklist-mode-one/apollo-main-quicklist-mode-one.o"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-select-records"
ORACLE = HERE / "verify_main_quicklist_select_records_oracle_20261015.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    return {row.split()[-1] for row in
            subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_select_records_4f5662.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SRC), "-o", str(obj)], check=True)
    defined = names(obj, "-g", "--defined-only")
    if defined != {"audio_quicklist_select_records_4f5662"} or \
            names(obj, "-u") != {"audio_uart_checksum_copy"}:
        raise RuntimeError("QuickList selector provider changed")
    linked = OUT / "apollo-main-quicklist-select-records.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = names(BASE, "-u"), names(linked, "-u")
    if before != after or "audio_quicklist_select_records_4f5662" not in names(linked, "-g", "--defined-only"):
        raise RuntimeError("Main selector binding changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_SELECT_RECORDS_ORACLE" or oracle["cases"] != 640:
        raise RuntimeError("QuickList selector oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_SELECT_RECORDS_C",
               "source": str(SRC.relative_to(ROOT)), "source_sha256": sha(SRC),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
               "oracle_script": str(ORACLE.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE),
               "native_cases": 640, "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [], "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Mode-two handlers that call this selector remain to be reconstructed.",
                          "Selection oracle controls the byte-copy provider at its native interface.",
                          "Final RAM placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
