#!/usr/bin/env python3
"""Bind the observed LVGL RAM slice and its three interior aliases."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/lvgl_runtime_state.c"
USERS = (
    G2 / "components/audio/uart_thread_source_candidate/display_lvlog.c",
    G2 / "components/audio/uart_thread_source_candidate/display_timer_children.c",
    G2 / "components/audio/uart_thread_source_candidate/display_lv_realloc.c",
)
BASE = G2 / "build/c-firmware/20261014/main-corrected-archive-tail-replay/07-main-event-wait-workers.o"
OUT = G2 / "build/c-firmware/20261014/main-lvgl-runtime-state"
ROOT_NAME = "audio_uart_display_lv_state"
CONTRACTS = {
    ROOT_NAME: (0x2006f548, 0x44d320, 0),
    "audio_uart_lv_static_slot": (0x2006f5ac, 0x44f7a4, 0x64),
    "audio_uart_lv_tick_state": (0x2006f600, 0x4734bc, 0xb8),
    "audio_uart_lv_lock_cell": (0x2006f718, 0x49acd0, 0x1d0),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def globals_at(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", str(path)], text=True)
    return {parts[-1]: (int(parts[0], 16), parts[1]) for line in output.splitlines()
            if len(parts := line.split()) == 3 and parts[-1] in CONTRACTS}


def main():
    raw = NATIVE.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("native ELF format changed")
    phoff = struct.unpack_from("<I", raw, 28)[0]
    if struct.unpack_from("<H", raw, 44)[0] != 1:
        raise RuntimeError("native ELF segment count changed")
    kind, offset, vaddr, _, filesz, _, _, _ = struct.unpack_from("<IIIIIIII", raw, phoff)
    if kind != 1:
        raise RuntimeError("native ELF load segment changed")
    users = "\n".join(p.read_text() for p in USERS)
    source = SOURCE.read_text()
    for name, (ram, literal, rel) in CONTRACTS.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"native literal unmapped: {name}")
        if struct.unpack_from("<I", raw, offset + literal - vaddr)[0] != ram:
            raise RuntimeError(f"native LVGL RAM literal changed: {name}")
        if ram != CONTRACTS[ROOT_NAME][0] + rel or name not in users:
            raise RuntimeError(f"LVGL user/offset contract changed: {name}")
    if "audio_uart_display_lv_state[0x1d4]" not in source or ".g2_ram_2006f548" not in source:
        raise RuntimeError("LVGL C storage extent changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "lvgl_runtime_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {ROOT_NAME} or names(obj, "-u"):
        raise RuntimeError("LVGL C object symbol contract changed")
    sizes = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if f"00000000 000001d4 D {ROOT_NAME}" not in sizes:
        raise RuntimeError("LVGL C storage size changed")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main LVGL imports changed")
    linked = OUT / "apollo-main-lvgl-runtime-state.o"
    aliases = [f"--defsym={name}={ROOT_NAME}+{rel:#x}"
               for name, (_, _, rel) in CONTRACTS.items() if name != ROOT_NAME]
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), *aliases,
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected LVGL import delta: {before-after}, {after-before}")
    symbols = globals_at(linked)
    root_address = symbols[ROOT_NAME][0]
    if set(symbols) != set(CONTRACTS) or any(
            symbols[name][0] != root_address + row[2]
            for name, row in CONTRACTS.items()):
        raise RuntimeError(f"LVGL interior aliases changed: {symbols}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LVGL_RUNTIME_STATE_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_contracts": {name: {"ram": hex(ram), "literal": hex(literal),
                                    "offset_from_root": hex(rel)}
                             for name, (ram, literal, rel) in CONTRACTS.items()},
        "observed_root_bytes": 0x1d4,
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in USERS},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["0x1d4 bytes cover observed references only; complete allocation and startup values remain open.",
                   "Final SRAM placement, whole-image link and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
