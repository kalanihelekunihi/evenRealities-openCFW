#!/usr/bin/env python3
"""Bind the bounded QuickList command decoder C body into Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_decode_558b3c.c"
BASE = G2 / "build/c-firmware/20261014/main-flashdb-store-value/apollo-main-flashdb-store-value.o"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-decode"
ORACLE = Path(__file__).with_name("verify_main_quicklist_decode_oracle_20261015.py")
CHILDREN = {"audio_quicklist_store_one", "audio_quicklist_store_many"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_decode_558b3c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-u") != CHILDREN or names(obj, "-g", "--defined-only") != {
        "audio_quicklist_decode_558b3c", "audio_quicklist_rx_state"}:
        raise RuntimeError("QuickList decoder provider set changed")
    before = names(BASE, "-u")
    if "audio_quicklist_decode_558b3c" not in before or CHILDREN & before:
        raise RuntimeError("QuickList Main import boundary changed")
    linked = OUT / "apollo-main-quicklist-decode.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_quicklist_decode_558b3c"} or after - before != CHILDREN:
        raise RuntimeError("QuickList import delta changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_DECODE_ORACLE" or len(oracle["cases"]) != 10:
        raise RuntimeError("QuickList oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_DECODE_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
        "oracle_script": str(ORACLE.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Native-matched command dispatch uses two unresolved storage children.",
                   "Only logging-disabled paths were compared; native state placement and startup remain open.",
                   "Whole-image and hardware behavior remain unproved."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
