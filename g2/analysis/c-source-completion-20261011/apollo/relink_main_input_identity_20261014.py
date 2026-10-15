#!/usr/bin/env python3
"""Relink corrected input functions and distinct native input storage."""
import json
import struct
import subprocess
import sys
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/input_identity_state.c"
CORRECTION = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_input_cell_identity_correction_20261014.py"
CORRECTED = G2 / "build/c-firmware/20261014/main-input-cell-identity-correction"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-device-timer-runtime-state/apollo-main-device-timer-runtime-state.o"
OUT = G2 / "build/c-firmware/20261014/main-input-identity-relink"
FUNCTIONS = {
    "audio_uart_input_event_send_464d1c": CORRECTED / "sync_corrected.o",
    "audio_uart_input_event": CORRECTED / "input_corrected.o",
    "audio_uart_display_thread": CORRECTED / "display_corrected.o",
}
CONTRACTS = {
    "audio_uart_input_mutex": (0x200744e8, 0x4448a0, 4),
    "audio_uart_input_queue": (0x200744e4, 0x4448a4, 4),
    "audio_uart_sync_schedule_queue": (0x200749cc, 0x45d068, 4),
    "audio_uart_input_event_flags": (0x20074b10, 0x45d0c8, 4),
    "g2_display_ring": (0x20073b60, 0x4448b0, 20),
}
ROM_NAME, ROM_ADDR, ROM_LITERAL = "audio_uart_input_queue_failure_context", 0x7536fc, 0x4448b4


def bytes_at(segments, address, count=4):
    for base, data in segments:
        if base <= address and address + count <= base + len(data):
            return data[address-base:address-base+count]
    raise RuntimeError(f"unmapped native address {address:#x}")


def symbols(path):
    rows = {}
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(path)], text=True)
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 4:
            rows[parts[-1]] = (int(parts[0], 16), int(parts[1], 16), parts[2])
    return rows


def main():
    subprocess.run([sys.executable, str(CORRECTION)], check=True)
    segments, _ = image(NATIVE)
    for name, (ram, literal, _) in CONTRACTS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native input RAM literal changed: {name}")
    if struct.unpack("<I", bytes_at(segments, ROM_LITERAL))[0] != ROM_ADDR or \
       bytes_at(segments, ROM_ADDR, 33) != b"input: message queue send failed\0":
        raise RuntimeError("native input failure ROM text changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "input_identity_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    rows = symbols(obj)
    expected = {name: size for name, (_, _, size) in CONTRACTS.items()}
    expected[ROM_NAME] = 33
    if names(obj, "-g", "--defined-only") != set(expected) or names(obj, "-u") or \
       {name: rows[name][1] for name in expected} != expected:
        raise RuntimeError("input identity C object symbol sizes changed")
    weakened = OUT / "apollo-main-input-owners-weakened.o"
    command = ["arm-none-eabi-objcopy"] + [f"--weaken-symbol={name}" for name in FUNCTIONS] + \
              [str(BASE), str(weakened)]
    subprocess.run(command, check=True)
    weak_rows = symbols(weakened)
    if any(weak_rows.get(name, (0, 0, ""))[2] not in ("W", "V") for name in FUNCTIONS):
        raise RuntimeError("stale merged input functions were not weakened")
    linked = OUT / "apollo-main-input-identity-relink.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(weakened),
                    *(str(path) for path in FUNCTIONS.values()), str(obj), "-o", str(linked)], check=True)
    linked_rows = symbols(linked)
    if any(linked_rows.get(name, (0, 0, ""))[2] != "T" for name in FUNCTIONS):
        raise RuntimeError("corrected input functions do not own linked strong symbols")
    before, after = names(BASE, "-u"), names(linked, "-u")
    expected_removed = {"audio_uart_input_mutex", "audio_uart_input_queue",
                        "audio_uart_input_event_flags", ROM_NAME, "g2_display_ring"}
    if not expected_removed <= before or expected_removed & after:
        raise RuntimeError(f"old input imports not fully resolved: {expected_removed & after}")
    stale_weak_only = {"audio_uart_input_ring", "audio_uart_display_ring"}
    if not stale_weak_only <= before or not stale_weak_only <= after:
        raise RuntimeError("expected stale weak-body direct-ring imports changed")
    if "audio_uart_sync_schedule_queue" in after or "audio_uart_sync_schedule_queue" in before:
        raise RuntimeError("new sync queue source provider did not resolve")
    if after - before:
        raise RuntimeError(f"unexpected new imports: {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_INPUT_IDENTITY_RELINK_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_ram_contracts": {name: {"ram": hex(ram), "literal": hex(literal),
                                                "source_bytes": size}
                                        for name, (ram, literal, size) in CONTRACTS.items()},
               "native_rom_contract": {"name": ROM_NAME, "address": hex(ROM_ADDR),
                                       "literal": hex(ROM_LITERAL), "text": "input: message queue send failed"},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "corrected_functions": {name: {"object": str(path.relative_to(ROOT)),
                                              "sha256": sha(path)} for name, path in FUNCTIONS.items()},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "weakened_object": str(weakened.relative_to(ROOT)), "weakened_sha256": sha(weakened),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "stale_weak_only_imports": sorted(stale_weak_only),
               "source_complete": False, "full_payload_linked": False,
               "root_rebuild_required": True,
               "limits": ["The old weak function bytes remain in this experimental merged object and retain two stale ring imports; an archive rebuild must remove them.",
                          "Final RAM/ROM placement, full ring backing storage, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
