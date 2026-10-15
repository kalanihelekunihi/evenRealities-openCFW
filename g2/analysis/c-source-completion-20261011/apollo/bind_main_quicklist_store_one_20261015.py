#!/usr/bin/env python3
"""Bind native-matched QuickList converter and single-item store."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_store_one_58d51c.c"
CONVERT = G2 / "components/audio/uart_thread_source_candidate/quicklist_convert_58da28.c"
BASE = G2 / "build/c-firmware/20261014/main-quicklist-decode/apollo-main-quicklist-decode.o"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-store-one"
ORACLES = (Path(__file__).with_name("verify_main_quicklist_convert_oracle_20261015.py"),
           Path(__file__).with_name("verify_main_quicklist_store_one_oracle_20261015.py"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    for src in (SOURCE, CONVERT):
        obj = OUT / (src.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(src), "-o", str(obj)], check=True)
        objects.append(obj)
    provider = OUT / "quicklist-store-one-provider.o"
    subprocess.run(["arm-none-eabi-ld", "-r", *map(str, objects), "-o", str(provider)], check=True)
    if names(provider, "-g", "--defined-only") != {
        "audio_quicklist_store_one", "audio_quicklist_convert_pb", "audio_quicklist_item_cache"}:
        raise RuntimeError("QuickList store-one definitions changed")
    if names(provider, "-u") != {"audio_quicklist_tick_now"}:
        raise RuntimeError("QuickList store-one lower contract changed")
    before = names(BASE, "-u")
    if "audio_quicklist_store_one" not in before or "audio_quicklist_tick_now" in before:
        raise RuntimeError("QuickList store-one Main boundary changed")
    linked = OUT / "apollo-main-quicklist-store-one.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(provider), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_quicklist_store_one"} or after - before != {"audio_quicklist_tick_now"}:
        raise RuntimeError("QuickList store-one import delta changed")
    for oracle_script in ORACLES:
        subprocess.run([sys.executable, str(oracle_script)], check=True, capture_output=True, text=True)
    convert_oracle = G2 / "build/c-firmware/20261014/main-quicklist-convert/oracle.json"
    store_oracle = OUT / "oracle.json"
    if len(json.loads(convert_oracle.read_text())["cases"]) != 11 or len(json.loads(store_oracle.read_text())["cases"]) != 6:
        raise RuntimeError("QuickList oracle coverage changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_STORE_ONE_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "convert_source": str(CONVERT.relative_to(ROOT)), "convert_source_sha256": sha(CONVERT),
        "objects": [{"path": str(obj.relative_to(ROOT)), "sha256": sha(obj)} for obj in objects],
        "provider_object": str(provider.relative_to(ROOT)), "provider_sha256": sha(provider),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "convert_oracle": str(convert_oracle.relative_to(ROOT)), "convert_oracle_sha256": sha(convert_oracle),
        "store_oracle": str(store_oracle.relative_to(ROOT)), "store_oracle_sha256": sha(store_oracle),
        "oracle_scripts": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in ORACLES],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["QuickList clock source remains an explicit unresolved dependency.",
                   "Storage cache placement, startup, logging-enabled paths and device behavior remain unproved."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
