#!/usr/bin/env python3
"""Bind close-chain native call names to already linked AppDb C providers."""
import json
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/close_provider_aliases.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-pair-event/apollo-main-master-pair-event.o"
OUT = G2 / "build/c-firmware/20261014/main-master-close-provider-aliases"
ALIASES = {"audio_ble_master_close_child_479b74": "audio_ble_privacy_rewrite_record",
           "audio_ble_master_close_child_47b730": "audio_ble_pair_record_validate"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    disassembly = subprocess.check_output([
        "arm-none-eabi-objdump", "-d", "-M", "force-thumb",
        "--start-address=0x47a47c", "--stop-address=0x47a49c", str(NATIVE)], text=True)
    for address in ("479b74", "47b730"):
        if f"bl\t{address}" not in disassembly:
            raise RuntimeError(f"native close-chain call {address} changed")
    obj = OUT / "close_provider_aliases.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ALIASES) or \
       names(obj, "-u") != set(ALIASES.values()):
        raise RuntimeError("close aliases have unexpected definitions or imports")
    before = names(BASE, "-u")
    base_defined = names(BASE, "-g", "--defined-only")
    if not set(ALIASES) <= before or not set(ALIASES.values()) <= base_defined:
        raise RuntimeError("close alias native contract or C providers missing")
    linked = OUT / "apollo-main-master-close-provider-aliases.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 483 or len(after) != 481 or before - after != set(ALIASES) or \
       after - before:
        raise RuntimeError(f"unexpected Main alias import delta {before-after} {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_CLOSE_PROVIDER_ALIASES_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_parent": "0x47a47c", "native_c_provider_aliases": ALIASES,
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["This validates native call addresses and C symbol wiring; it does not revalidate full AppDb provider behavior.",
                   "The MRAM layout, whole payload, and physical hardware remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
