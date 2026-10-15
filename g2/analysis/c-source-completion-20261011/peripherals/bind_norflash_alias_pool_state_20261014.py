#!/usr/bin/env python3
"""Carry checked NOR flash and scheduler bridges into pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-nema-float-current-receipt.json"
PROVIDER_RECEIPT = OUT / "ambiq-graph-current-receipt.json"
DELAY_RECEIPT = G2 / "build/c-firmware/terminal-os-delay-bridge-round970/receipt.json"
OBJECT = OUT / "norflash-alias-pool-state-abi.o"
DELAY_OBJECT = OUT / "norflash-delay-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-norflash-alias-bound.o"
RECEIPT = OUT / "pool-state-norflash-alias-current-receipt.json"
SOURCE = "g2/components/main/norflash_alias_candidates_20261014/aliases.c"
PROVIDERS = {"g2_norflash_lock_46f65e", "g2_norflash_unlock_46f674",
             "g2_norflash_scheduler_delay_449376"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    provider = json.loads(PROVIDER_RECEIPT.read_text())
    delay = json.loads(DELAY_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_NEMA_FLOAT_C"
    assert provider["status"] == "PASS_CURRENT_MAIN_AMBIQ_GRAPH_COMPILE"
    assert delay["status"] == "PASS_TERMINAL_OS_DELAY_BRIDGE"
    row, = [row for row in provider["source_units"] if row["source"] == SOURCE]
    assert set(row["defined"]) == PROVIDERS
    source = ROOT / SOURCE
    old_object = ROOT / row["object"]
    original = ROOT / base["linked_object"]
    assert sha(source) == row["source_sha256"]
    assert sha(old_object) == row["object_sha256"]
    assert sha(original) == base["linked_sha256"]
    before = names(original, "-u")
    assert PROVIDERS <= before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(OBJECT)],
                   check=True)
    assert names(OBJECT, "-g", "--defined-only") == PROVIDERS
    delay_source = G2 / delay["source"]
    assert sha(delay_source) == delay["source_sha256"]
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(delay_source),
                    "-o", str(DELAY_OBJECT)], check=True)
    assert names(DELAY_OBJECT, "-g", "--defined-only") == {"audio_os_delay"}
    assert names(DELAY_OBJECT, "-u") == {"audio_delay"}
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(OBJECT),
                    str(DELAY_OBJECT),
                    "-o", str(BOUND)], check=True)
    after = names(BOUND, "-u")
    assert after == before - PROVIDERS
    receipt = {
        "status": "PASS_POOLED_MAIN_NORFLASH_ALIAS_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "provider_receipt": str(PROVIDER_RECEIPT.relative_to(ROOT)),
        "provider_receipt_sha256": sha(PROVIDER_RECEIPT),
        "delay_bridge_receipt": str(DELAY_RECEIPT.relative_to(ROOT)),
        "delay_bridge_receipt_sha256": sha(DELAY_RECEIPT),
        "source": SOURCE,
        "source_sha256": sha(source),
        "pool_abi_object": str(OBJECT.relative_to(ROOT)),
        "pool_abi_object_sha256": sha(OBJECT),
        "delay_pool_abi_object": str(DELAY_OBJECT.relative_to(ROOT)),
        "delay_pool_abi_object_sha256": sha(DELAY_OBJECT),
        "imports_resolved": sorted(PROVIDERS),
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Other Main imports, final image placement and device execution remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
