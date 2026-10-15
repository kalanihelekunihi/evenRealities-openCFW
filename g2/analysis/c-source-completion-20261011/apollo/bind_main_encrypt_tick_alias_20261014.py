#!/usr/bin/env python3
"""Alias the two C names for native BLE tick RAM 0x200742f4."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/ancc_cache_cells.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_comm_proc_msg.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-dm-adv-control-state/apollo-main-dm-adv-control-state.o"
OUT = G2 / "build/c-firmware/20261014/main-encrypt-tick-alias"
PRIMARY, ALIAS = "audio_ble_ancc_connection_tick", "audio_ble_encrypt_tick_200742f4"
RAM, LITERAL = 0x200742f4, 0x4b82d4


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def addresses(path):
    rows = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-g", str(path)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[-1] in (PRIMARY, ALIAS):
            rows[parts[-1]] = (int(parts[0], 16), parts[1])
    return rows


def main():
    segments, _ = image(NATIVE)
    if struct.unpack("<I", bytes_at(segments, LITERAL))[0] != RAM or \
       f'__attribute__((alias("{PRIMARY}")))' not in SOURCE.read_text() or \
       f"{ALIAS}=g2_flashdb_candidate_tick();" not in USER.read_text():
        raise RuntimeError("native shared tick or C alias/user changed")
    OUT.mkdir(parents=True, exist_ok=True)
    candidate = OUT / "ancc_cache_cells_alias_check.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(candidate)], check=True)
    check = addresses(candidate)
    if set(check) != {PRIMARY, ALIAS} or check[PRIMARY] != check[ALIAS]:
        raise RuntimeError("source-level BLE tick alias does not share C storage")
    before = names(BASE, "-u")
    if ALIAS not in before or PRIMARY not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main tick alias import/provider changed")
    linked = OUT / "apollo-main-encrypt-tick-alias.o"
    subprocess.run(["arm-none-eabi-ld", "-r", f"--defsym={ALIAS}={PRIMARY}",
                    str(BASE), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ALIAS} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    resolved = addresses(linked)
    if set(resolved) != {PRIMARY, ALIAS} or resolved[PRIMARY][0] != resolved[ALIAS][0]:
        raise RuntimeError("linked BLE tick aliases do not share an address")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_ENCRYPT_TICK_ALIAS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_ram": hex(RAM), "native_literal": hex(LITERAL),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
               "alias_check_object": str(candidate.relative_to(ROOT)),
               "alias_check_object_sha256": sha(candidate),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "linked_symbol_offset": hex(resolved[PRIMARY][0]),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["This binds two source names to one observed native word; the tick's complete initialization/lifetime remains open.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
