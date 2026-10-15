#!/usr/bin/env python3
"""Bind WSF and display fatal callback names to one native RAM word."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/shared_fatal_hook_state.c"
USERS = (G2 / "components/audio/uart_thread_source_candidate/display_ble_wsf_assert.c",
         G2 / "components/audio/uart_thread_source_candidate/display_page_manager_new.c")
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-open-connection/apollo-main-master-open-connection.o"
OUT = G2 / "build/c-firmware/20261014/main-shared-fatal-hook"
PRIMARY, ALIAS = "audio_uart_display_fatal_handler", "audio_ble_wsf_assert_hook"
RAM, LITERALS = 0x2007456c, (0x53af50, 0x569af4)


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def symbol_rows(path):
    rows = {}
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(path)], text=True)
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[-1] in (PRIMARY, ALIAS):
            rows[parts[-1]] = (int(parts[0], 16), int(parts[1], 16), parts[2])
    return rows


def main():
    segments, _ = image(NATIVE)
    if any(struct.unpack("<I", bytes_at(segments, literal))[0] != RAM for literal in LITERALS):
        raise RuntimeError("native shared fatal callback literals changed")
    source, assert_user, display_user = SOURCE.read_text(), *(p.read_text() for p in USERS)
    if f'alias("{PRIMARY}")' not in source or \
       f"extern uintptr_t {ALIAS};" not in assert_user or \
       f"extern void (*{PRIMARY})(const char *,const char *,uint32_t);" not in display_user:
        raise RuntimeError("shared callback source/user contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "shared_fatal_hook_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {PRIMARY, ALIAS} or names(obj, "-u"):
        raise RuntimeError("shared callback C symbol contract changed")
    rows = symbol_rows(obj)
    if set(rows) != {PRIMARY, ALIAS} or rows[PRIMARY][:2] != rows[ALIAS][:2] or rows[PRIMARY][1] != 4:
        raise RuntimeError(f"C aliases do not share one four-byte cell: {rows}")
    before = names(BASE, "-u")
    if not {PRIMARY, ALIAS} <= before:
        raise RuntimeError("Apollo Main callback imports changed")
    linked = OUT / "apollo-main-shared-fatal-hook.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {PRIMARY, ALIAS} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    linked_rows = symbol_rows(linked)
    if set(linked_rows) != {PRIMARY, ALIAS} or linked_rows[PRIMARY][:2] != linked_rows[ALIAS][:2]:
        raise RuntimeError("linked callback aliases do not share storage")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SHARED_FATAL_HOOK_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_ram": hex(RAM), "native_literals": [hex(x) for x in LITERALS],
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in USERS},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "linked_symbol_offset": hex(linked_rows[PRIMARY][0]),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["One native RAM word is represented by two source names; the callback producer and startup value remain open.",
                          "The named section expresses intended RAM address but final placement is unverified.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
