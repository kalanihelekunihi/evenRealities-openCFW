#!/usr/bin/env python3
"""Bind native-matched QuickList multi-item storage into Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_store_many_58d668.c"
BASE = G2 / "build/c-firmware/20261014/main-quicklist-store-one/apollo-main-quicklist-store-one.o"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-store-many"
ORACLE = Path(__file__).with_name("verify_main_quicklist_store_many_oracle_20261015.py")
CHILDREN = {"audio_quicklist_item_cache", "audio_quicklist_convert_pb", "audio_quicklist_tick_now"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_store_many_58d668.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-u") != CHILDREN or names(obj, "-g", "--defined-only") != {"audio_quicklist_store_many"}:
        raise RuntimeError("QuickList multi-item provider set changed")
    before = names(BASE, "-u")
    providers = names(BASE, "-g", "--defined-only")
    if "audio_quicklist_store_many" not in before or not CHILDREN <= providers | before:
        raise RuntimeError("QuickList multi-item Main boundary changed")
    linked = OUT / "apollo-main-quicklist-store-many.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_quicklist_store_many"} or after - before:
        raise RuntimeError("QuickList multi-item import delta changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_STORE_MANY_ORACLE" or len(oracle["cases"]) != 12:
        raise RuntimeError("QuickList multi-item oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_STORE_MANY_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
        "oracle_script": str(ORACLE.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Native/C comparison covers selected count/index paths with logging disabled.",
                   "Clock implementation, cache startup/placement and device behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
