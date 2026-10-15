#!/usr/bin/env python3
"""Bind the native BLE logger flag and observed descriptor prefix."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/logger_ble_state.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_logger_ble_cancel.c"
BASE = G2 / "build/c-firmware/20261014/main-log-buffer-state/apollo-main-log-buffer-state.o"
OUT = G2 / "build/c-firmware/20261014/main-logger-ble-state"
CONTRACTS = {
    "audio_uart_logger_ble_enabled": (0x20074fe2, 0x459264, 1),
    "audio_uart_ble_logger_descriptor": (0x20073b90, 0x448fcc, 16),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


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
    source = SOURCE.read_text()
    user = USER.read_text()
    for name, (ram, literal, _) in CONTRACTS.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"native literal unmapped: {name}")
        if struct.unpack_from("<I", raw, offset + literal - vaddr)[0] != ram:
            raise RuntimeError(f"native RAM literal changed: {name}")
        if name not in source or name not in user or f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"C contract changed: {name}")
    if "descriptor[8u]" not in user or "descriptor+12u" not in user:
        raise RuntimeError("descriptor access bounds changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "logger_ble_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("compiled logger BLE symbols changed")
    sizes = {}
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[-1] in CONTRACTS:
            sizes[parts[-1]] = int(parts[1], 16)
    if sizes != {name: row[2] for name, row in CONTRACTS.items()}:
        raise RuntimeError(f"compiled BLE logger sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main logger BLE imports changed")
    linked = OUT / "apollo-main-logger-ble-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LOGGER_BLE_STATE_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_contracts": {name: {"ram": hex(ram), "literal": hex(lit), "observed_bytes": size}
                             for name, (ram, lit, size) in CONTRACTS.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Descriptor covers the 16-byte prefix touched by the native setter; full allocation and startup remain open.",
                   "Final SRAM placement, whole-image link, and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
